#!/usr/bin/env python3
"""List a milestone's issues, sorted by project iteration then priority.

Reads issues from the repository's GitHub Project (ProjectV2) board
and orders them by the project's *Iteration* field (earliest iteration
first, unscheduled last) and then by *Priority* (in the order the
options are defined on the board, e.g. P0 before P1; unset last).

Requires the `gh` CLI authenticated with the `read:project` scope:

    gh auth refresh -s read:project

Examples, run from inside the target repo:
    # My open issues in the current milestone (default project)
    list_milestone_issues.py

    # Anyone's issues, closed ones too, as JSON
    list_milestone_issues.py --assignee any --state all --json
"""

# The embedded GraphQL fragment strings run past 88 columns; wrapping them
# adds no clarity (whitespace is insignificant in GraphQL) and a `# noqa`
# can't sit inside a triple-quoted string, so E501 is silenced file-wide.
# flake8: noqa: E501

import argparse
import atexit
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field, fields, replace
from enum import StrEnum
from typing import Any, Final, NewType

# MARK: - Configuration & type aliases

DEFAULT_REPO: Final = "detektra/detektra"  # fallback when not run inside a git repo
DEFAULT_PROJECT: Final = 13  # "Detektra Product Development"

# A GitHub user login, distinguished from arbitrary strings.
Login = NewType("Login", str)

# A milestone's display title (shown in headers; the user's --milestone arg).
MilestoneTitle = NewType("MilestoneTitle", str)

# A milestone's stable repo-scoped number (the `/milestone/N` in its URL),
# used as its identity — robust to title renames, unlike the title.
MilestoneNumber = NewType("MilestoneNumber", int)

# A JSON object decoded from a GraphQL/REST response (loosely shaped).
Json = dict[str, Any]


class ProjectField(StrEnum):
    """Project-board field names (members act as their str value)."""

    ITERATION = "Iteration"
    PRIORITY = "Priority"
    SIZE = "Size"
    ESTIMATE = "Estimate"
    STATUS = "Status"


# MARK: - ANSI & display constants

# OSC 8 terminal hyperlink: \033]8;;URL\033\\ TEXT \033]8;;\033\\
_OSC8: Final = "\033]8;;{url}\033\\{text}\033]8;;\033\\"

_RESET: Final = "\033[0m"
_BOLD: Final = "\033[1m"
_DIM: Final = "\033[2m"
_UNDIM: Final = "\033[22m"  # normal intensity (cancels an enclosing dim)
_DARK_GREY: Final = "\033[38;5;238m"  # faded foreground, for shipped (Done) titles
_YELLOW: Final = "\033[38;5;220m"  # yellow foreground

# Priority text weight: P0 stands out (bold), P1 is normal, P2 recedes
# (dim). Codes absent here render plain.
_PRIORITY_WEIGHT: Final = {"P0": _BOLD, "P2": _DIM}

# Shorter display labels for some board statuses (display only; the
# board's own names still drive sorting, colours, and emphasis).
_STATUS_LABELS: Final = {"in progress": "wip", "in review": "rvw"}

# Signals shown next to a still-open PR's number.
_REVIEW_GLYPH: Final = {"changes_requested": "🚧", "approved": "✅"}
_BEHIND_GLYPH: Final = "🍂"  # head branch is out of date with its base
_DRAFT_GLYPH: Final = "📝"  # PR is still a draft
_TEAM_GLYPH: Final = "👥"  # issue assigned to more than one person
_NO_REVIEWER_GLYPH: Final = "🚨"  # ready PR (not draft) with no reviewer assigned
_WIDE_GLYPHS: Final = (
    *_REVIEW_GLYPH.values(),
    _BEHIND_GLYPH,
    _DRAFT_GLYPH,
    _TEAM_GLYPH,
    _NO_REVIEWER_GLYPH,
)

# Stand-in for a PR number that recurs brighter lower down: a down
# arrowhead (U+2304) pointing at the leading (bottom-most) row.
_DUP_PR: Final = "⌄"


# MARK: - Domain models


@dataclass(frozen=True, slots=True, kw_only=True)
class Issue:
    """A milestone issue with its board fields and closing PRs."""

    number: int
    title: str
    url: str
    state: str
    assignee_count: int
    status: str | None
    iteration: str | None
    iteration_start: str | None
    iteration_duration: int | None
    priority: str | None
    size: str | None
    estimate: float | None
    prs: list["PullRequest"]
    milestone: MilestoneNumber | None = None  # owning milestone (per-milestone rollups)


@dataclass(frozen=True, slots=True, kw_only=True)
class PullRequest:
    """A PR that closes an issue, with the signals shown beside it."""

    number: int
    url: str
    state: str  # OPEN / CLOSED / MERGED
    is_draft: bool
    review: str | None  # "changes_requested" / "approved" / None
    behind: bool  # head branch is out of date with its base
    branch_url: str | None  # link target for the status badge
    branch: str | None = (
        None  # head branch name (badge tooltip); default for old caches
    )
    has_reviewer: bool = True  # any requested/actual reviewer; True for old caches
    reviewers: tuple[Login, ...] = ()  # logins that left an opinionated review
    assigned: tuple[Login, ...] = ()  # logins ever assigned as a reviewer


@dataclass(frozen=True, slots=True, kw_only=True)
class Milestone:
    """Milestone header metadata (counts are issues only, not PRs)."""

    number: MilestoneNumber
    title: MilestoneTitle
    description: str | None
    html_url: str
    state: str
    due_on: str | None
    open_issues: int
    closed_issues: int


@dataclass(frozen=True, slots=True, kw_only=True)
class TeammatePR:
    """A teammate's PR within the window, with your involvement in it.

    Sourced from search (their PRs often close no issue), so it carries only
    what the reviewer stats need: which window milestone it falls in, its
    estimate (points), and whether you reviewed it / were ever assigned to.
    """

    number: int
    milestone: MilestoneNumber
    estimate: float | None
    you_reviewed: bool
    you_assigned: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class Board:
    """Everything one GraphQL round-trip returns for a milestone."""

    issues: list[Issue]
    options: dict[str, list[Json]]
    """Each single-select field name → its options, in board order.

    Each option is a {"name", "color"} dict.
    """
    milestones: list[Milestone]
    """The milestones in view (one, or current + following), in time order
    (earliest first). Each renderer arranges its own display order."""
    reverse: dict[Login, list[TeammatePR]] = field(default_factory=dict)
    """Each teammate (a reviewer of your PRs) → their own window PRs, for the
    reverse review-relationship columns. Empty for old caches; populated by a
    second targeted fetch."""


@dataclass(frozen=True, slots=True, kw_only=True)
class Cell:
    """A row's pre-rendered cells and the bits to lay them out."""

    iteration: str | None
    iteration_start: str | None
    iteration_duration: int | None
    is_done: bool
    prio: str  # rendered, visible width always 4 ("P0" + 2 padding)
    status: str  # rendered
    status_vis: int  # visible width of the (variable) status column
    size: str  # padded to 2
    est: str  # rendered, padded to 3
    issue: str  # rendered "#NNN title" hyperlink


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewInvolvement:
    """One person's review involvement over a set of PRs: distinct PRs
    reviewed / ever assigned to review, and the summed ticket estimates of
    each."""

    reviewed: int = 0
    assigned: int = 0
    reviewed_points: float = 0.0
    assigned_points: float = 0.0


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewerStats:
    """A teammate's review relationship with you for one iteration."""

    login: Login
    mine: ReviewInvolvement  # their involvement in your PRs
    theirs: ReviewInvolvement  # your involvement in their PRs
    their_total_prs: int = 0  # their PRs in the window (favouritism denominator)
    their_total_points: float = 0.0  # summed estimate of those PRs


@dataclass(frozen=True, slots=True, kw_only=True)
class Highlights:
    """Reviewer cells to flag. `load` is the assignment-balance flag on the
    assigned side ("hot"/"cold" → bold/dim). The rest are logins whose
    reviewing falls below a fair share (yellow): under_mine on your PRs,
    under_theirs on theirs; each split into the count and points cells."""

    load: dict[Login, str]
    under_mine_count: set[Login]
    under_mine_points: set[Login]
    under_theirs_count: set[Login]
    under_theirs_points: set[Login]


@dataclass(frozen=True, slots=True, kw_only=True)
class Groups:
    """Iteration groups classified relative to today.

    `current` and `noiter` (the unscheduled group) are at most one group
    each; `future` and `past` are lists of groups. The ordering methods
    arrange them for each view's reading direction.
    """

    current: list[Issue] | None
    noiter: list[Issue] | None
    future: list[list[Issue]]
    past: list[list[Issue]]

    def top_down(self) -> list[list[Issue]]:
        """Markdown order: current first, then upcoming iterations (soonest
        first), unscheduled, then past (most recent first)."""
        return (
            ([self.current] if self.current else [])
            + sorted(self.future, key=lambda g: g[0].iteration_start or "")
            + ([self.noiter] if self.noiter else [])
            + sorted(self.past, key=lambda g: g[0].iteration_start or "", reverse=True)
        )

    def bottom_up(self) -> list[list[Issue]]:
        """Terminal order (printed then read upward): future iterations
        (latest start on top, so the soonest-ahead sits lowest), unscheduled,
        current, then past at the very bottom (newest higher) — so the
        most-relevant work lands closest to the prompt."""
        return (
            sorted(self.future, key=lambda g: g[0].iteration_start or "", reverse=True)
            + ([self.noiter] if self.noiter else [])
            + ([self.current] if self.current else [])
            + sorted(self.past, key=lambda g: g[0].iteration_start or "", reverse=True)
        )


# MARK: - Date & iteration helpers


def weekdays_until(end_date: datetime.date) -> int:
    """Count of weekdays (Mon–Fri) from today through `end_date`, inclusive."""
    day, count = datetime.date.today(), 0
    while day <= end_date:
        if day.weekday() < 5:
            count += 1
        day += datetime.timedelta(days=1)
    return count


def iteration_span(
    start: str | None, duration: int | None
) -> tuple[datetime.date, datetime.date] | None:
    """An iteration's inclusive (start, end) dates, or None if unscheduled."""
    if not start or not duration:
        return None
    start_date = datetime.date.fromisoformat(start)
    return start_date, start_date + datetime.timedelta(days=duration - 1)


def iteration_date_range(
    start: str | None, duration: int | None, *, current: bool = False
) -> str | None:
    """Format an iteration's span and the time until its end.

    E.g. "2026-05-25 – 2026-06-07, ends in 4 days" (end inclusive). For
    the current iteration, the tail is weekdays remaining instead.
    """
    span = iteration_span(start, duration)
    if span is None:
        return None
    start_date, end_date = span
    if current:
        n = weekdays_until(end_date)
        ends = f"{n} weekday{'' if n == 1 else 's'} remain{'s' if n == 1 else ''}"
    else:
        days = (end_date - datetime.date.today()).days
        if days > 0:
            ends = f"ends in {days} day{'s' if days != 1 else ''}"
        elif days == 0:
            ends = "ends today"
        else:
            ends = f"ended {-days} day{'s' if days != -1 else ''} ago"
    return f"{start_date.isoformat()} – {end_date.isoformat()}, {ends}"


def is_current_iteration(start: str | None, duration: int | None) -> bool:
    """True when today is within the iteration's [start, end] span."""
    span = iteration_span(start, duration)
    return span is not None and span[0] <= datetime.date.today() <= span[1]


def is_past_iteration(start: str | None, duration: int | None) -> bool:
    """True when the iteration's (inclusive) end date is before today."""
    span = iteration_span(start, duration)
    return span is not None and span[1] < datetime.date.today()


def relative_day_phrase(target: datetime.date) -> str:
    """Human phrasing for how far off a date is from today."""
    days = (target - datetime.date.today()).days
    if days == 0:
        return "today"
    if days == 1:
        return "tomorrow"
    if days == -1:
        return "yesterday"
    return f"in {days} days" if days > 0 else f"{-days} days ago"


# MARK: - Display & formatting helpers


def display_width(text: str) -> int:
    """Visible width, counting (double-wide) PR emojis as 2 cells."""
    return len(text) + sum(text.count(glyph) for glyph in _WIDE_GLYPHS)


def milestone_meta(ms: Milestone, *, sep: str = "  ·  ") -> str:
    """A milestone's 'Due <date> (<phrase>) · <closed>/<total> closed (<pct>)'
    line (or 'No due date · …' when undated); `sep` joins the two halves."""
    closed, total = ms.closed_issues, ms.open_issues + ms.closed_issues
    pct = f"{round(100 * closed / total)}%" if total else "—"
    progress = f"{closed}/{total} closed ({pct})"
    if ms.due_on:
        due = datetime.datetime.fromisoformat(ms.due_on).date()
        return f"Due {due.isoformat()} ({relative_day_phrase(due)}){sep}{progress}"
    return f"No due date{sep}{progress}"


def format_milestone(
    ms: Milestone, *, use_links: bool, use_colour: bool, current: bool = True
) -> str:
    """Two-line milestone header (title, due date, progress).

    Bolded only when `current`, so a following milestone reads quieter.
    """
    title = hyperlink(ms.title, ms.html_url, enabled=use_links)
    meta = milestone_meta(ms)
    if use_colour and current:
        title, meta = f"{_BOLD}{title}{_RESET}", f"{_BOLD}{meta}{_RESET}"
    return f"{title}\n{meta}"


def status_cell(
    row: "Issue",
    colour: str | None,
    *,
    use_links: bool,
    use_colour: bool,
    emphasise: bool,
    dim_prs: frozenset[int] = frozenset(),
) -> tuple[str, int]:
    """Build the status column and return (rendered, visible_width).

    A coloured dot, then the lowercased status, with any linked PR
    numbers appended. The status word and the first PR share one
    hyperlink (so clicking the status opens its PR); extra PRs each get
    their own link. When `emphasise` is set, a "backlog"/"todo" status
    is bolded to flag unstarted current work. Any PR number in
    `dim_prs` is replaced by a downward arrow — within a contiguous run
    of rows sharing a PR, only the bottom row shows the real number and
    the arrows above point down to it; an arrow row also has its status
    (dot and word) dimmed, so the run reads as one unit led by its bottom
    row.
    """
    lowered = (row.status or "-").lower()
    base = _STATUS_LABELS.get(lowered, lowered)
    # A team glyph rides beside the status when the issue has
    # multiple assignees.
    team = f" {_TEAM_GLYPH}" if row.assignee_count > 1 else ""
    # A non-leading member of a same-PR block (its PR shows bright lower
    # down) has its whole status — dot and word — dimmed.
    recede = use_colour and any(pr.number in dim_prs for pr in row.prs)
    # `text` (unstyled) drives column width; `shown` carries any
    # bold styling.
    text = base + team
    if use_colour and row.status == "Done":
        # Shipped: faded grey at normal intensity, matching the title and
        # escaping the row-wide dim.
        shown = f"{_UNDIM}{_DARK_GREY}{base}{_RESET}{team}"
    elif emphasise and use_colour and base in ("backlog", "todo"):
        shown = f"{_BOLD}{base}{_RESET}{team}"
    else:
        shown = text
    if recede:
        # Re-arm dim after any inner reset (e.g. the emphasis bold).
        shown = _DIM + shown.replace(_RESET, _RESET + _DIM) + _RESET
    refs = []  # (number, suffix, glyphs, pr_url, branch_url)
    for pr in row.prs:
        pr_state = pr.state.lower()  # open / closed / merged
        # The status already conveys open/merged; only flag a closed PR.
        suffix = " (closed)" if pr_state == "closed" else ""
        # Signals for still-open PRs: draft (or, if ready but unreviewed,
        # a warning), then review state, then stale branch. Only the
        # leading (bottom-most) render carries them; the arrow rows above
        # drop the badge entirely as noise.
        dup = pr.number in dim_prs
        glyphs = []
        if pr_state == "open" and not dup:
            if pr.is_draft:
                glyphs.append(_DRAFT_GLYPH)
            elif not pr.has_reviewer:
                glyphs.append(_NO_REVIEWER_GLYPH)
            review = _REVIEW_GLYPH.get(pr.review or "")
            if review:
                glyphs.append(review)
            if pr.behind:
                glyphs.append(_BEHIND_GLYPH)
        refs.append((pr.number, suffix, glyphs, pr.url, pr.branch_url))

    def render_ref(ref: tuple, *, first: bool) -> str:
        # "#NNN" (+ "(closed)") links to the PR; the status badge is a
        # separate link to the PR's head branch. The first PR shares its
        # link with the status word so clicking the status opens the PR.
        number, suffix, glyphs, pr_url, branch_url = ref
        if number in dim_prs:  # shows its real number only at its lowest row
            core = f"{_DIM}{_DUP_PR}{_RESET}" if use_colour else _DUP_PR
        else:
            core = f"#{number}{suffix}"
        prefix = f"{shown} " if first else ""
        out = hyperlink(f"{prefix}{core}", pr_url, enabled=use_links)
        if glyphs:
            badge = " ".join(glyphs)
            out += " " + (
                hyperlink(badge, branch_url, enabled=use_links) if branch_url else badge
            )
        return out

    if refs:
        plain_parts = [text]
        for number, suffix, glyphs, _, _ in refs:
            seg = _DUP_PR if number in dim_prs else f"#{number}{suffix}"
            if glyphs:
                seg += " " + " ".join(glyphs)
            plain_parts.append(seg)
        plain = " ".join(plain_parts)
        body = " ".join(render_ref(ref, first=(i == 0)) for i, ref in enumerate(refs))
    else:
        plain, body = text, shown

    if not use_colour:
        return body, display_width(plain)
    dot = (
        f"\033[38;5;{_GH_DOT[colour]}m●{_RESET} "
        if colour in _GH_DOT
        else "  "  # keep the dot column's width when the status has no colour
    )
    if recede:
        dot = _DIM + dot
    return dot + body, 2 + display_width(plain)


# Estimate brightness on the xterm grayscale ramp:
# 1 (grey) → 5+ (white).
_ESTIMATE_GREY: Final = {1: 246, 2: 249, 3: 251, 4: 253, 5: 255}


def estimate_cell(estimate: float | None, *, use_colour: bool) -> str:
    """Estimate padded to 3 cols, brighter the higher the value."""
    text = (f"{estimate:g}" if estimate is not None else "-").ljust(3)
    if not use_colour or estimate is None:
        return text
    code = _ESTIMATE_GREY[max(1, min(5, round(estimate)))]
    return f"\033[38;5;{code}m{text}{_RESET}"


# GitHub single-select option colours → 256-colour code for
# the status dot.
_GH_DOT: Final = {
    "GRAY": 245,
    "BLUE": 39,
    "GREEN": 40,
    "YELLOW": 220,
    "ORANGE": 208,
    "RED": 196,
    "PINK": 211,
    "PURPLE": 141,
}

# Board option colour → coloured-circle emoji, for markdown (which has
# no ANSI colour). No pink circle exists, so PINK uses the pink flower
# 💮 to stay distinct from both RED's 🔴 and PURPLE's 🟣.
_MD_DOT: Final = {
    "GRAY": "⚪",
    "BLUE": "🔵",
    "GREEN": "🟢",
    "YELLOW": "🟡",
    "ORANGE": "🟠",
    "RED": "🔴",
    "PINK": "💮",
    "PURPLE": "🟣",
}


def hyperlink(text: str, url: str, *, enabled: bool) -> str:
    """Wrap text in an OSC 8 hyperlink, or append the bare URL."""
    if enabled:
        return _OSC8.format(url=url, text=text)
    return f"{text}  {url}"


# MARK: - GitHub I/O — gh, GraphQL, rate limits


def _reset_phrase(info: Json) -> str:
    """'resets at HH:MM:SS (in 3m 20s)' for a rate-limit resource."""
    reset = datetime.datetime.fromtimestamp(info["reset"], datetime.timezone.utc)
    secs = max(
        0, int((reset - datetime.datetime.now(datetime.timezone.utc)).total_seconds())
    )
    mins, rem = divmod(secs, 60)
    local = reset.astimezone().strftime("%H:%M:%S")
    return f"resets at {local} (in {mins}m {rem}s)"


def _rate_limit_resources() -> Json | None:
    """The `resources` map from the free `rate_limit` endpoint, or None.

    Reads `gh api rate_limit`, which doesn't count against any limit.
    """
    probe = subprocess.run(
        ["gh", "api", "rate_limit"], capture_output=True, text=True, check=False
    )
    try:
        return json.loads(probe.stdout)["resources"]
    except (json.JSONDecodeError, KeyError):
        return None


def rate_limit_hint(args: list[str]) -> str | None:
    """A 'resets at ...' hint for a rate-limited request, or None.

    For the resource (graphql/core) that the failing request used.
    """
    resources = _rate_limit_resources()
    if resources is None:
        return None
    info = resources.get("graphql" if "graphql" in args else "core")
    if not info:
        return None
    return (
        f"rate limit: {info['remaining']}/{info['limit']} left; "
        f"{_reset_phrase(info)}"
    )


def report_rate_limit() -> None:
    """Best-effort: print GraphQL/REST quota usage to stderr.

    Reads the free `rate_limit` endpoint (no quota cost). GraphQL bills in
    points, REST (core) in requests; both show remaining/limit and used.
    """
    resources = _rate_limit_resources()
    if resources is None:
        return
    parts = []
    for name in ("graphql", "core"):
        info = resources.get(name)
        if not info:
            continue
        seg = f"{name} {info['remaining']}/{info['limit']} left ({info['used']} used)"
        if name == "graphql":
            seg += f", {_reset_phrase(info)}"
        parts.append(seg)
    if parts:
        # Routine quota report dims into the background; the louder
        # not-enough-quota messages (rate_limit_hint, cache fallback)
        # stay at normal intensity.
        msg = "rate limit — " + " · ".join(parts)
        if sys.stderr.isatty() and "NO_COLOR" not in os.environ:
            msg = f"{_DIM}{msg}{_RESET}"
        sys.stderr.write(msg + "\n")


class RateLimitError(Exception):
    """A gh call failed because a GitHub rate limit was exceeded."""


def gh(args: list[str]) -> str:
    """Run a `gh` command and return stdout.

    Exits on failure; a rate-limit failure raises RateLimitError so the
    caller can point the user at a cached result.
    """
    proc = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        if "rate limit" in proc.stderr.lower():
            hint = rate_limit_hint(args)
            if hint:
                sys.stderr.write(hint + "\n")
            raise RateLimitError
        sys.exit(proc.returncode)
    return proc.stdout


def graphql(query: str, **variables: Any) -> Json:
    # -F coerces ints/bools (needed for Int! vars); -f keeps
    # strings verbatim so a search query or milestone title isn't
    # reinterpreted.
    args = ["api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        flag = "-F" if isinstance(value, int) else "-f"
        args += [flag, f"{key}={value}"]
    return json.loads(gh(args))


# MARK: - Environment resolution


def local_gh_login(host: str = "github.com") -> str | None:
    """The active gh login for `host` from the local hosts.yml.

    No network call — gh caches the authenticated user there, so we
    avoid a `gh api user` round-trip. Returns None if the file/host/key
    is absent, so the caller can fall back.
    """
    # gh's own precedence: GH_CONFIG_DIR, then XDG_CONFIG_HOME/gh,
    # then ~/.config/gh.
    config_dir = os.environ.get("GH_CONFIG_DIR") or os.path.join(
        os.environ.get("XDG_CONFIG_HOME")
        or os.path.join(os.path.expanduser("~"), ".config"),
        "gh",
    )
    try:
        with open(os.path.join(config_dir, "hosts.yml"), encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return None
    # Tiny scoped parse (avoids a PyYAML dependency): find `user:`
    # under the host block. The `users:` sub-map keys are logins,
    # not `user:`, so they don't match.
    in_host = False
    for line in lines:
        if line[:1].strip() and line.rstrip().endswith(":"):  # column-0 host header
            in_host = line.rstrip()[:-1].strip().strip('"') == host
        elif in_host:
            m = re.match(r"\s+user:\s*(\S+)", line)
            if m:
                return m.group(1).strip().strip('"')
    return None


def git_remote_repo() -> str | None:
    """Parse "owner/name" from the origin remote URL.

    Local git, no network. Handles both ssh
    (git@github.com:owner/name.git) and https
    (https://github.com/owner/name.git) forms; None outside a repo.
    """
    proc = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    m = re.search(r"[:/]([^/:]+/[^/:]+?)(?:\.git)?/?$", proc.stdout.strip())
    return m.group(1) if m else None


def resolve_assignee_login(assignee: str) -> str | None:
    """Turn --assignee into a concrete login (None means no filter).

    The live `Milestone.issues(filterBy:)` connection needs a real
    login, so "@me" is resolved to the authenticated user (locally if
    possible, else via the API); "any" disables the filter.
    """
    if assignee == "any":
        return None
    if assignee == "@me":
        return local_gh_login() or gh(["api", "user", "--jq", ".login"]).strip()
    return assignee


# MARK: - GraphQL fragments & node parsing

# GraphQL fragment: an issue's board field values + the PRs that
# close it. We pull exactly the five board fields we need by name
# (via fieldValueByName) rather than paging the whole fieldValues
# connection — cheaper and order-proof.
# (Indentation is cosmetic — GraphQL ignores whitespace.)
_ISSUE_BOARD_FIELDS: Final = f"""
  number title url state
  assignees(first: 1) {{ totalCount }}
  closedByPullRequestsReferences(first: 3, includeClosedPrs: true) {{
    nodes {{
      number url state isDraft mergeStateStatus
      headRefName headRepository {{ url }}
      reviewRequests(first: 5) {{ totalCount nodes {{ requestedReviewer {{ ... on User {{ login }} }} }} }}
      reviews {{ totalCount }}
      latestOpinionatedReviews(first: 5) {{ nodes {{ state author {{ login }} }} }}
      latestReviews(first: 5) {{ nodes {{ state author {{ login }} }} }}
      timelineItems(itemTypes: [REVIEW_REQUESTED_EVENT], first: 10) {{ nodes {{ ... on ReviewRequestedEvent {{ requestedReviewer {{ ... on User {{ login }} }} }} }} }}
    }}
  }}
  projectItems(first: 3) {{
    nodes {{
      project {{ number }}
      status: fieldValueByName(name: "{ProjectField.STATUS.value}") {{ ... on ProjectV2ItemFieldSingleSelectValue {{ name }} }}
      priority: fieldValueByName(name: "{ProjectField.PRIORITY.value}") {{ ... on ProjectV2ItemFieldSingleSelectValue {{ name }} }}
      size: fieldValueByName(name: "{ProjectField.SIZE.value}") {{ ... on ProjectV2ItemFieldSingleSelectValue {{ name }} }}
      estimate: fieldValueByName(name: "{ProjectField.ESTIMATE.value}") {{ ... on ProjectV2ItemFieldNumberValue {{ number }} }}
      iteration: fieldValueByName(name: "{ProjectField.ITERATION.value}") {{ ... on ProjectV2ItemFieldIterationValue {{ title startDate duration }} }}
    }}
  }}
"""


# Per-PR fields for the search-sourced reverse ("their PRs"): the author,
# the review-request timeline (your assignment), merge/open dates (to place
# an issue-less PR by time window), the PR's own project estimate (points
# for such a PR), and each closing issue's milestone + estimate (placement
# and points for a PR that closes one).
_REVERSE_PR_FIELDS: Final = f"""
  number
  author {{ login }}
  mergedAt
  createdAt
  timelineItems(itemTypes: [REVIEW_REQUESTED_EVENT], first: 10) {{ nodes {{ ... on ReviewRequestedEvent {{ requestedReviewer {{ ... on User {{ login }} }} }} }} }}
  projectItems(first: 3) {{
    nodes {{
      project {{ number }}
      estimate: fieldValueByName(name: "{ProjectField.ESTIMATE.value}") {{ ... on ProjectV2ItemFieldNumberValue {{ number }} }}
    }}
  }}
  closingIssuesReferences(first: 3) {{
    nodes {{
      milestone {{ number }}
      projectItems(first: 3) {{
        nodes {{
          project {{ number }}
          estimate: fieldValueByName(name: "{ProjectField.ESTIMATE.value}") {{ ... on ProjectV2ItemFieldNumberValue {{ number }} }}
        }}
      }}
    }}
  }}
"""


def _logins(nodes: list[Json], key: str) -> tuple[Login, ...]:
    """Sorted distinct logins from a list of review/request nodes."""
    return tuple(
        sorted(Login(login) for n in nodes if (login := (n[key] or {}).get("login")))
    )


def _project_estimate(node: Json, project: int) -> float | None:
    """The Estimate project-field value for an issue/PR node, or None."""
    for item in (node.get("projectItems") or {}).get("nodes", []):
        if item["project"]["number"] == project:
            return (item.get("estimate") or {}).get("number")
    return None


def parse_board_issue(issue: Json, project: int, milestone: MilestoneNumber) -> Issue:
    """Pull board fields + closing PRs from one GraphQL issue node."""
    iteration_title = iteration_start = iteration_duration = None
    priority = size = estimate = status = None
    for item in issue["projectItems"]["nodes"]:
        if item["project"]["number"] != project:
            continue
        # Each alias is the named field's value object, or None
        # when unset.
        status = (item["status"] or {}).get("name")
        priority = (item["priority"] or {}).get("name")
        size = (item["size"] or {}).get("name")
        estimate = (item["estimate"] or {}).get("number")
        if it := item["iteration"]:
            iteration_title = it.get("title")
            iteration_start = it.get("startDate")
            iteration_duration = it.get("duration")
        break  # at most one project item matches our project
    prs = []
    for pr in issue["closedByPullRequestsReferences"]["nodes"]:
        # Everyone ever assigned as a reviewer, for the reviewer stats —
        # from the timeline, since GitHub clears a request once reviewed.
        # (Team requests carry no login, so they fall out.)
        assigned = _logins(pr["timelineItems"]["nodes"], "requestedReviewer")
        # A re-requested reviewer (back in the live reviewRequests) supersedes
        # their prior review, so drop their opinion: a changes-requested that's
        # since been re-requested reads as pending, not blocking.
        rerequested = set(_logins(pr["reviewRequests"]["nodes"], "requestedReviewer"))
        states = {
            r["state"]
            for r in pr["latestOpinionatedReviews"]["nodes"]
            if (r["author"] or {}).get("login") not in rerequested
        }
        if "CHANGES_REQUESTED" in states:
            review = "changes_requested"
        elif "APPROVED" in states:
            review = "approved"
        else:
            review = None
        # Everyone who substantively reviewed (one entry per person), for
        # the reviewer tables: opinionated reviewers, plus anyone whose
        # review you later dismissed (state DISMISSED — they did review).
        # Includes re-requested reviewers; they reviewed, historically.
        dismissed = {
            login
            for r in pr["latestReviews"]["nodes"]
            if r["state"] == "DISMISSED" and (login := (r["author"] or {}).get("login"))
        }
        reviewers = tuple(
            sorted(
                set(_logins(pr["latestOpinionatedReviews"]["nodes"], "author"))
                | dismissed
            )
        )
        repo = pr["headRepository"]
        branch_url = f"{repo['url']}/tree/{pr['headRefName']}" if repo else None
        has_reviewer = (
            pr["reviewRequests"]["totalCount"] > 0 or pr["reviews"]["totalCount"] > 0
        )
        prs.append(
            PullRequest(
                number=pr["number"],
                url=pr["url"],
                state=pr["state"],
                is_draft=pr["isDraft"],
                review=review,
                behind=pr["mergeStateStatus"] == "BEHIND",
                branch_url=branch_url,
                branch=pr["headRefName"],
                has_reviewer=has_reviewer,
                reviewers=reviewers,
                assigned=assigned,
            )
        )
    return Issue(
        number=issue["number"],
        title=issue["title"],
        url=issue["url"],
        state=issue["state"],
        assignee_count=issue["assignees"]["totalCount"],
        status=status,
        iteration=iteration_title,
        iteration_start=iteration_start,
        iteration_duration=iteration_duration,
        priority=priority,
        size=size,
        estimate=estimate,
        prs=prs,
        milestone=milestone,
    )


# MARK: - Fetching


def fetch_board(
    owner: str,
    name: str,
    project: int,
    milestone_numbers: list[MilestoneNumber],
    assignee_login: str | None,
    state: str,
) -> Board:
    """One main round-trip: issues, single-select options, milestone(s).

    Folds what used to be four `gh` calls (issue list, project fields,
    batched project values, milestone REST) into a single GraphQL request.
    Each milestone is looked up directly by its stable `number`; issues
    come from the milestone's live `issues` connection (real-time, unlike
    the search index), filtered server-side by assignee/state, with board
    fields inline. Issues from every milestone are merged into one board.

    The forward board only; the reverse review data is fetched separately
    (concurrently by the caller) and merged into `Board.reverse`.
    """
    states = {"open": "[OPEN]", "closed": "[CLOSED]"}.get(state, "[OPEN, CLOSED]")
    if assignee_login:
        login_decl = ", $login: String!"
        issue_args = f"first: 100, states: {states}, filterBy: {{assignee: $login}}"
    else:
        login_decl = ""
        issue_args = f"first: 100, states: {states}"

    # One aliased milestone lookup per id — an exact `milestone(number:)`,
    # so no fuzzy title search and no near-match filtering.
    ms_fields = f"""
        number title description url state dueOn
        openIssues: issues(states: OPEN) {{ totalCount }}
        closedIssues: issues(states: CLOSED) {{ totalCount }}
        matched: issues({issue_args}) {{
          pageInfo {{ hasNextPage }}
          nodes {{ {_ISSUE_BOARD_FIELDS} }}
        }}
    """
    ms_var_decls = "".join(f", $ms{i}: Int!" for i in range(len(milestone_numbers)))
    ms_blocks = "\n".join(
        f"m{i}: milestone(number: $ms{i}) {{ {ms_fields} }}"
        for i in range(len(milestone_numbers))
    )
    variables: dict[str, Any] = dict(owner=owner, name=name, project=project)
    if assignee_login:
        variables["login"] = assignee_login
    for i, ms_number in enumerate(milestone_numbers):
        variables[f"ms{i}"] = ms_number

    data = graphql(
        f"""
        query($owner: String!, $name: String!, $project: Int!{login_decl}{ms_var_decls}) {{
          organization(login: $owner) {{
            projectV2(number: $project) {{
              fields(first: 50) {{
                nodes {{ ... on ProjectV2SingleSelectField {{ name options {{ name color }} }} }}
              }}
            }}
          }}
          repository(owner: $owner, name: $name) {{
            {ms_blocks}
          }}
        }}
        """,
        **variables,
    )
    root = data["data"]
    options = {
        n["name"]: n["options"]
        for n in root["organization"]["projectV2"]["fields"]["nodes"]
        if n.get("name")
    }
    repo = root["repository"]
    milestones: list[Milestone] = []
    issues: list[Issue] = []
    for i, ms_number in enumerate(milestone_numbers):
        ms_node = repo[f"m{i}"]  # milestone(number:) — a single node or null
        if ms_node is None:
            continue
        if ms_node["matched"]["pageInfo"]["hasNextPage"]:
            print(
                f"warning: milestone {ms_node['title']!r} has more than 100 matching "
                "issues; only the first 100 were fetched.",
                file=sys.stderr,
            )
        milestones.append(
            Milestone(
                number=ms_number,
                title=MilestoneTitle(ms_node["title"]),
                description=ms_node["description"],
                html_url=ms_node["url"],
                state=ms_node["state"],
                due_on=ms_node["dueOn"],
                open_issues=ms_node["openIssues"]["totalCount"],
                closed_issues=ms_node["closedIssues"]["totalCount"],
            )
        )
        issues.extend(
            parse_board_issue(n, project, ms_number)
            for n in ms_node["matched"]["nodes"]
        )
    return Board(issues=issues, options=options, milestones=milestones)


def parse_reverse_pr(
    pr: Json,
    project: int,
    ranges: list[tuple[MilestoneNumber, str | None, str | None]],
    window_set: set[MilestoneNumber],
    reviewed: set[int],
    me: Login,
) -> tuple[Login, TeammatePR] | None:
    """Place one search-sourced PR into its milestone as a TeammatePR.

    Returns `(author, TeammatePR)` with your involvement (reviewed / ever
    assigned) layered on, or None to skip a PR that is yours, authorless,
    or lands outside every milestone span. A PR closing an in-window issue
    takes that issue's milestone and estimate; an issue-less PR is placed by
    when it landed (merged date, else open date) with its own estimate.
    """
    number = pr["number"]
    author = (pr["author"] or {}).get("login")
    if not author or author == me:
        return None
    closing = pr["closingIssuesReferences"]["nodes"]
    in_window = next(
        (c for c in closing if (c.get("milestone") or {}).get("number") in window_set),
        None,
    )
    if in_window:
        # Closes an in-window issue: that issue's milestone and estimate.
        ms_number = MilestoneNumber(in_window["milestone"]["number"])
        estimate = _project_estimate(in_window, project)
    elif not closing:
        # Issue-less PR: place by when it landed (merged date, else open
        # date) into the milestone span covering it; its own estimate.
        when = (pr.get("mergedAt") or pr.get("createdAt") or "")[:10]
        span = next(
            (
                num
                for num, start, end in ranges
                if when
                and (not start or start[:10] <= when)
                and (not end or when <= end[:10])
            ),
            None,
        )
        if span is None:
            return None  # landed outside every milestone span
        ms_number = span
        estimate = _project_estimate(pr, project)
    else:
        return None  # closes only out-of-window / unmilestoned issues
    teammate_pr = TeammatePR(
        number=number,
        milestone=ms_number,
        estimate=estimate,
        you_reviewed=number in reviewed,
        you_assigned=me in _logins(pr["timelineItems"]["nodes"], "requestedReviewer"),
    )
    return Login(author), teammate_pr


def fetch_reverse(
    owner: str,
    name: str,
    project: int,
    ranges: list[tuple[MilestoneNumber, str | None, str | None]],
    me: Login | None,
) -> dict[Login, list[TeammatePR]]:
    """Everyone's PRs in the window, by author, with your involvement.

    The fair-share review flags need each teammate's *total* PRs (the
    denominator), so this fetches every window PR — not just ones you
    touched — via a broad `is:pr` search, scoped to PRs updated since the
    window's start and paged. (PRs here carry no milestone of their own, so
    the search can't filter by it; placement is client-side.) Your own
    involvement on each is layered on: reviewed from a single
    `reviewed-by:@me` set, assigned (ever asked to review) from the PR's
    timeline. `ranges` gives each window milestone its `(title, start,
    end)` span. A PR that closes an in-window milestone issue is placed in
    that issue's milestone with its estimate; an issue-less PR is placed by
    when it landed (merged date, or open date if still open) into the
    milestone span covering it, with the PR's own estimate; anything else
    (only out-of-window issues, or landed outside every span) is skipped.
    Returns each author → their TeammatePRs (one per PR). Reads the (slightly
    stale) search index, unlike the live forward path.
    """
    start = ranges[0][1] if ranges else None
    if me is None or start is None:
        return {}
    since = start[:10]  # the window start as a plain date, for `updated:>=`
    window_set = {t for t, _, _ in ranges}

    def paged_search(scope: str, fields: str) -> list[Json]:
        """All PR nodes matching `scope`, paging until the index is
        exhausted (search caps each page at 100)."""
        nodes: list[Json] = []
        cursor: str | None = None
        while True:
            kwargs: dict[str, Any] = {"q": scope}
            if cursor:
                kwargs["after"] = cursor
            page = graphql(
                f"""
                query($q: String!, $after: String) {{
                  search(query: $q, type: ISSUE, first: 100, after: $after) {{
                    pageInfo {{ hasNextPage endCursor }}
                    nodes {{ ... on PullRequest {{ {fields} }} }}
                  }}
                }}
                """,
                **kwargs,
            )["data"]["search"]
            nodes.extend(p for p in page["nodes"] if p)
            if not page["pageInfo"]["hasNextPage"]:
                return nodes
            cursor = page["pageInfo"]["endCursor"]

    base = f"repo:{owner}/{name} is:pr updated:>={since}"
    # The two searches are independent — overlap the (small) reviewed-by
    # lookup with the (large, paged) all-PRs fetch instead of serialising.
    with ThreadPoolExecutor(max_workers=2) as pool:
        reviewed_future = pool.submit(
            lambda: {
                n["number"] for n in paged_search(f"{base} reviewed-by:{me}", "number")
            }
        )
        all_prs = paged_search(base, _REVERSE_PR_FIELDS)
        reviewed = reviewed_future.result()
    result: dict[Login, list[TeammatePR]] = {}
    for pr in all_prs:
        placed = parse_reverse_pr(pr, project, ranges, window_set, reviewed, me)
        if placed is not None:
            author, teammate_pr = placed
            result.setdefault(author, []).append(teammate_pr)
    return result


def resolve_window(
    owner: str, name: str, explicit: str | None
) -> list[tuple[MilestoneNumber, str | None, str | None]]:
    """The window milestones as `(id, start, end)` spans, by due date.

    Each milestone ends at its own due date and starts at the previous
    milestone's — so the reverse fetch can derive its date window without
    waiting on the board (letting the two run concurrently). `explicit`
    pins the current milestone by title; otherwise it's the open milestone
    whose due date is nearest today, plus the one following it by number
    (the upcoming milestone often has no due date, so number — not due
    date — orders it). Identity is the milestone `number`, not the title.
    `[]` when no current milestone can be determined (incl. an explicit
    title that matches none). Cheap: no issue/project traversal.
    """
    # ~1 GraphQL point, 0 REST/core: milestone metadata only (no issues/PRs).
    nodes = graphql(
        """
        query($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) {
            milestones(first: 100, states: [OPEN, CLOSED]) {
              nodes { number title dueOn state }
            }
          }
        }
        """,
        owner=owner,
        name=name,
    )["data"]["repository"]["milestones"]["nodes"]
    if explicit:
        current = next((m for m in nodes if m["title"] == explicit), None)
        if current is None:
            return []  # unknown title — caller reports "not found"
    else:
        today = datetime.date.today()
        dated = [
            (abs((datetime.datetime.fromisoformat(m["dueOn"]).date() - today).days), m)
            for m in nodes
            if m["dueOn"] and m["state"] == "OPEN"
        ]
        if not dated:
            return []
        current = min(dated, key=lambda d: d[0])[1]
    earlier = [m for m in nodes if m["number"] < current["number"] and m["dueOn"]]
    start = max(earlier, key=lambda m: m["number"])["dueOn"] if earlier else None
    ranges = [(MilestoneNumber(current["number"]), start, current["dueOn"])]
    # An explicit --milestone means just that one; the window's "following"
    # milestone is only added when picking the current one automatically.
    later = [m for m in nodes if m["number"] > current["number"]]
    if not explicit and later:
        following = min(later, key=lambda m: m["number"])
        ranges.append(
            (MilestoneNumber(following["number"]), current["dueOn"], following["dueOn"])
        )
    return ranges


# MARK: - Caching


def _cache_path(key: str) -> str:
    digest = hashlib.sha256(key.encode()).hexdigest()[:16]
    return os.path.join(
        tempfile.gettempdir(), "list-milestone-issues-cache", f"{digest}.json"
    )


def read_board_cache(key: str, ttl: int) -> Board | None:
    """Return a cached Board for `key` if younger than `ttl` seconds.

    Returns None on a miss or stale entry.
    """
    if ttl <= 0:
        return None
    path = _cache_path(key)
    try:
        if time.time() - os.path.getmtime(path) > ttl:
            return None
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None

    pr_keys = {f.name for f in fields(PullRequest)}
    tpr_keys = {f.name for f in fields(TeammatePR)}

    def revive(issue: Json) -> Issue:
        # Drop keys an older cache schema may carry (e.g. the renamed
        # `requested`); missing new fields fall back to their defaults.
        prs = [
            PullRequest(**{k: v for k, v in pr.items() if k in pr_keys})
            for pr in issue.pop("prs", [])
        ]
        return Issue(**issue, prs=prs)

    def revive_teammate_pr(pr: Json) -> TeammatePR:
        # An older reverse cache (lean Issues) lacks you_reviewed/you_assigned,
        # so TeammatePR(**…) raises TypeError below → treated as a cache miss.
        return TeammatePR(**{k: v for k, v in pr.items() if k in tpr_keys})

    try:
        return Board(
            issues=[revive(issue) for issue in data["issues"]],
            options=data["options"],
            milestones=[Milestone(**m) for m in data["milestones"]],
            reverse={
                Login(p): [revive_teammate_pr(pr) for pr in prs]
                for p, prs in data.get("reverse", {}).items()
            },
        )
    except (KeyError, TypeError):
        return None  # cache predates a schema change; treat as a miss


def write_board_cache(key: str, board: Board) -> None:
    """Persist `board` so re-runs within the TTL skip the network."""
    path = _cache_path(key)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(asdict(board), fh)
    except OSError:
        pass  # caching is best-effort; never fail the run over it


# MARK: - Markdown helpers


def md_escape(text: str) -> str:
    """Neutralise table/link-breaking chars; collapse whitespace.

    Deliberately minimal — only `\\ | [ ] < >` — so prose like
    "fix(api):" stays readable.
    """
    text = " ".join(text.split())
    text = text.replace("\\", "\\\\")
    for ch in "|[]<>":
        text = text.replace(ch, "\\" + ch)
    return text


def md_title(text: str) -> str:
    """Escape a markdown link title (the "…" hover tooltip)."""
    text = " ".join(text.split())
    return text.replace("\\", "\\\\").replace('"', '\\"')


# MARK: - Review analytics


def _involvement(issues: list[Issue]) -> dict[Login, ReviewInvolvement]:
    """Per login, their review involvement over these issues' PRs.

    Distinct PRs (a PR closing several of these issues counts once; an
    opinionated review counts once per PR). Points sum the closed
    tickets' estimates — each ticket once per login, a missing one as 0.
    """
    rev_prs: dict[Login, set[int]] = {}
    asg_prs: dict[Login, set[int]] = {}
    rev_pts: dict[Login, float] = {}
    asg_pts: dict[Login, float] = {}
    for issue in issues:
        est = issue.estimate or 0.0
        rev_here: set[Login] = set()
        asg_here: set[Login] = set()
        for pr in issue.prs:
            for login in pr.reviewers:
                rev_prs.setdefault(login, set()).add(pr.number)
                rev_here.add(login)
            for login in pr.assigned:
                asg_prs.setdefault(login, set()).add(pr.number)
                asg_here.add(login)
        for login in rev_here:
            rev_pts[login] = rev_pts.get(login, 0.0) + est
        for login in asg_here:
            asg_pts[login] = asg_pts.get(login, 0.0) + est
    return {
        p: ReviewInvolvement(
            reviewed=len(rev_prs.get(p, ())),
            assigned=len(asg_prs.get(p, ())),
            reviewed_points=rev_pts.get(p, 0.0),
            assigned_points=asg_pts.get(p, 0.0),
        )
        for p in set(rev_prs) | set(asg_prs)
    }


def reverse_for_milestone(
    reverse: dict[Login, list[TeammatePR]], milestone: MilestoneNumber
) -> dict[Login, list[TeammatePR]]:
    """Restrict each teammate's reverse PRs to one milestone."""
    return {
        p: [pr for pr in prs if pr.milestone == milestone] for p, prs in reverse.items()
    }


def _pr_totals(prs: list[TeammatePR]) -> tuple[int, float]:
    """Distinct-PR count and summed estimate of a teammate's window PRs."""
    return len({pr.number for pr in prs}), sum(pr.estimate or 0.0 for pr in prs)


def _my_involvement(prs: list[TeammatePR]) -> ReviewInvolvement | None:
    """Your distinct-PR involvement (reviewed / assigned + points) over a
    teammate's window PRs, or None if you neither reviewed nor were assigned
    to any of them (so they earn no `theirs` entry)."""
    reviewed = [pr for pr in prs if pr.you_reviewed]
    assigned = [pr for pr in prs if pr.you_assigned]
    if not reviewed and not assigned:
        return None
    return ReviewInvolvement(
        reviewed=len({pr.number for pr in reviewed}),
        assigned=len({pr.number for pr in assigned}),
        reviewed_points=sum(pr.estimate or 0.0 for pr in reviewed),
        assigned_points=sum(pr.estimate or 0.0 for pr in assigned),
    )


def review_stats(
    my_issues: list[Issue],
    reverse: dict[Login, list[TeammatePR]],
    me: Login | None,
) -> list[ReviewerStats]:
    """Reviewer rows for an iteration: each teammate's involvement in your
    PRs (`mine`) and yours in theirs (`theirs`), plus each teammate's own
    PR total (the favouritism denominator).

    `reverse` maps each teammate to their own PRs for this iteration; your
    involvement in those (recorded per TeammatePR) becomes `theirs`. Rows
    are people involved with your PRs or whose PRs you touched, sorted by
    your-PRs reviewed (desc), assigned (desc), login.
    """
    forward = _involvement(my_issues)
    # `my_issues` is issue-anchored, so reviewers of your PRs that close no
    # issue aren't counted in `mine` (left as-is: you nearly always link an
    # issue, so the gap is tiny — unlike the reverse path, where teammates
    # often don't, which is why that side is sourced from search instead).
    people = set(forward)
    if me is not None:
        people.discard(me)  # you are not your own reviewer row
    theirs: dict[Login, ReviewInvolvement] = {}
    for person, their_prs in reverse.items():
        mine_in_theirs = _my_involvement(their_prs) if me else None
        if mine_in_theirs:
            theirs[person] = mine_in_theirs
            people.add(person)
    zero = ReviewInvolvement()
    rows = []
    for p in people:
        total_prs, total_points = _pr_totals(reverse.get(p, []))
        rows.append(
            ReviewerStats(
                login=p,
                mine=forward.get(p, zero),
                theirs=theirs.get(p, zero),
                their_total_prs=total_prs,
                their_total_points=total_points,
            )
        )
    rows.sort(key=lambda s: (-s.mine.reviewed, -s.mine.assigned, s.login))
    return rows


# Reviewer-table flag thresholds. Reviewing should spread evenly: with the
# table's N reviewers each fair share is total/N, and reviewing below a
# fraction of that share is flagged. Points need a minimum to read into.
_HL_MIN_POINTS: Final = 5.0
_LOAD_HOT_SHARE: Final = 2.0  # ≥ 2× an even split of your review assignments
_LOAD_COLD_SHARE: Final = 0.25  # ≤ ¼ of an even split (including zero)
_FAIR_SHARE_FLOOR: Final = 0.75  # flag reviewing below ¾ of an even share


def review_highlights(rows: list[ReviewerStats]) -> Highlights:
    """Reviewer cells to flag for one milestone.

    `load` marks an uneven assignment split on the assigned (my points)
    side. The `under_*` sets mark reviewing below `_FAIR_SHARE_FLOOR` of a
    fair share among the table's N reviewers, computed per count and points
    cell. The two sides use different baselines: `under_mine` (teammates
    reviewing your PRs) splits the review work *actually done* on your PRs,
    so a busy reviewer isn't flagged just because your PRs are broadly
    under-reviewed; `under_theirs` (you reviewing theirs) is a fair fraction
    of each teammate's *own* PR total, so neglecting a low-volume author
    still shows. Needs ≥2 reviewers; points flags also need volume.
    """
    n = len(rows)
    if n < 2:
        return Highlights(
            load={},
            under_mine_count=set(),
            under_mine_points=set(),
            under_theirs_count=set(),
            under_theirs_points=set(),
        )
    load: dict[Login, str] = {}
    asg = {s.login: s.mine.assigned_points for s in rows}
    if (total := sum(asg.values())) >= _HL_MIN_POINTS:
        even = total / n
        for login, v in asg.items():
            if v >= _LOAD_HOT_SHARE * even:
                load[login] = "hot"
            elif v <= _LOAD_COLD_SHARE * even:
                load[login] = "cold"

    def under_count(reviewed: int, total_prs: int) -> bool:
        # The fair share must be at least one whole PR to read into.
        share = total_prs / n
        return share >= 1 and reviewed < _FAIR_SHARE_FLOOR * share

    def under_points(reviewed_pts: float, total_pts: float) -> bool:
        return total_pts >= _HL_MIN_POINTS and reviewed_pts < _FAIR_SHARE_FLOOR * (
            total_pts / n
        )

    mine_reviewed = sum(s.mine.reviewed for s in rows)
    mine_reviewed_pts = sum(s.mine.reviewed_points for s in rows)
    return Highlights(
        load=load,
        under_mine_count={
            s.login for s in rows if under_count(s.mine.reviewed, mine_reviewed)
        },
        under_mine_points={
            s.login
            for s in rows
            if under_points(s.mine.reviewed_points, mine_reviewed_pts)
        },
        under_theirs_count={
            s.login for s in rows if under_count(s.theirs.reviewed, s.their_total_prs)
        },
        under_theirs_points={
            s.login
            for s in rows
            if under_points(s.theirs.reviewed_points, s.their_total_points)
        },
    )


# MARK: - Rendering


def review_table_terminal(rows: list[ReviewerStats], *, use_colour: bool) -> list[str]:
    """Plain-text reviewer table (header + a row per person), or [].

    The reviewed side of each column pair (counts and points) goes yellow
    when that reviewing is below a fair share: `my PRs`/`my points` for a
    teammate under-reviewing your PRs, `their PRs`/`their points` for one
    whose PRs you under-review. The assigned side of `my points` carries
    the assignment-load flag (bold/dim). Other cells are plain.
    """
    if not rows:
        return []
    hl = review_highlights(rows)
    headers = ["reviewer", "my PRs", "my points", "their PRs", "their points"]

    def yellow(text: str, flagged: bool) -> str:
        return f"{_YELLOW}{text}{_RESET}" if use_colour and flagged else text

    def load_style(text: str, flag: str) -> str:
        if not use_colour or not flag:
            return text
        return f"{_BOLD if flag == 'hot' else _DIM}{text}{_RESET}"

    # Each cell is (plain, styled): plain (escape-free) drives column width,
    # styled is what prints.
    table: list[list[tuple[str, str]]] = []
    for s in rows:
        lg = s.login
        mrev_c, masg_c = str(s.mine.reviewed), str(s.mine.assigned)
        trev_c, tasg_c = str(s.theirs.reviewed), str(s.theirs.assigned)
        mrev_p, masg_p = f"{s.mine.reviewed_points:g}", f"{s.mine.assigned_points:g}"
        trev_p, tasg_p = (
            f"{s.theirs.reviewed_points:g}",
            f"{s.theirs.assigned_points:g}",
        )
        ld = hl.load.get(lg, "")
        my_pr = f"{yellow(mrev_c, lg in hl.under_mine_count)}/{masg_c}"
        my_pts = (
            f"{yellow(mrev_p, lg in hl.under_mine_points)}/{load_style(masg_p, ld)}"
        )
        their_pr = f"{yellow(trev_c, lg in hl.under_theirs_count)}/{tasg_c}"
        their_pts = f"{yellow(trev_p, lg in hl.under_theirs_points)}/{tasg_p}"
        table.append(
            [
                (lg, lg),
                (f"{mrev_c}/{masg_c}", my_pr),
                (f"{mrev_p}/{masg_p}", my_pts),
                (f"{trev_c}/{tasg_c}", their_pr),
                (f"{trev_p}/{tasg_p}", their_pts),
            ]
        )
    widths = [max(len(headers[i]), *(len(r[i][0]) for r in table)) for i in range(5)]

    def fmt(cells: list[tuple[str, str]]) -> str:
        parts = [cells[0][1].ljust(widths[0])]
        for i in range(1, 5):
            plain, styled = cells[i]
            parts.append(" " * (widths[i] - len(plain)) + styled)
        return "  ".join(parts)

    return [fmt([(h, h) for h in headers])] + [fmt(r) for r in table]


def review_table_markdown(rows: list[ReviewerStats]) -> list[str]:
    """Markdown reviewer table rows (header + separator + a row each), or
    []. Same flags as the terminal: the fair-share shortfall italicises the
    reviewed cells (counts and points), assignment load bolds/italicises the
    assigned (my points) cell."""
    if not rows:
        return []
    hl = review_highlights(rows)
    out = [
        "| Reviewer "
        "| assigned (my PRs) | reviewed (my PRs) "
        "| assigned (their PRs) | reviewed (their PRs) "
        "| assigned (my points) | reviewed (my points) "
        "| assigned (their points) | reviewed (their points) |",
        "|:--|--:|--:|--:|--:|--:|--:|--:|--:|",
    ]

    def under(text: str, flagged: bool) -> str:
        return f"*{text}*" if flagged else text

    def md_emphasis(text: str, flag: str) -> str:
        """Markdown highlight: hot → bold, cold → italic (no dim in MD)."""
        if flag == "hot":
            return f"**{text}**"
        if flag == "cold":
            return f"*{text}*"
        return text

    for s in rows:
        lg = s.login
        ld = hl.load.get(lg, "")
        out.append(
            f"| {md_escape(lg)} "
            f"| {s.mine.assigned} "
            f"| {under(str(s.mine.reviewed), lg in hl.under_mine_count)} "
            f"| {s.theirs.assigned} "
            f"| {under(str(s.theirs.reviewed), lg in hl.under_theirs_count)} "
            f"| {md_emphasis(f'{s.mine.assigned_points:g}', ld)} "
            f"| {under(f'{s.mine.reviewed_points:g}', lg in hl.under_mine_points)} "
            f"| {s.theirs.assigned_points:g} "
            f"| {under(f'{s.theirs.reviewed_points:g}', lg in hl.under_theirs_points)} "
            "|"
        )
    return out


def render_markdown(
    milestones: list[Milestone],
    groups: list[list[Issue]],
    status_colours: dict[str, str],
    reverse: dict[Login, list[TeammatePR]],
    me: Login | None,
) -> str:
    """Render the milestone(s) as a top-down GitHub-Flavored Markdown doc.

    A `##` header per milestone, then a `###` heading + table per
    iteration group (already in display order). Unlike the terminal view
    there's no dim/arrow dedup: every row carries its full, self-contained
    PR links.
    """

    def pr_refs(row: Issue) -> str:
        parts = []
        for pr in row.prs:
            suffix = " (closed)" if pr.state.lower() == "closed" else ""
            tip = md_title(f"{pr.state.lower()} pull request")
            ref = f'[#{pr.number}{md_escape(suffix)}]({pr.url} "{tip}")'
            # (glyph, human description) for each still-open signal.
            signals: list[tuple[str, str]] = []
            if pr.state.lower() == "open":
                if pr.is_draft:
                    signals.append((_DRAFT_GLYPH, "draft"))
                elif not pr.has_reviewer:
                    signals.append((_NO_REVIEWER_GLYPH, "no reviewer assigned"))
                if pr.review and (g := _REVIEW_GLYPH.get(pr.review)):
                    signals.append((g, pr.review.replace("_", " ")))
                if pr.behind:
                    signals.append((_BEHIND_GLYPH, "stale branch"))
            if signals:
                badge = "".join(g for g, _ in signals)
                if pr.branch_url:
                    desc = ", ".join(d for _, d in signals)
                    btip = md_title(f"{desc} · {pr.branch}" if pr.branch else desc)
                    ref += f' [{badge}]({pr.branch_url} "{btip}")'
                else:
                    ref += f" {badge}"
            parts.append(ref)
        return " ".join(parts)

    def row_line(row: Issue) -> str:
        prio = row.priority or "--"
        prio_md = f"**{prio}**" if prio == "P0" else prio
        dot = _MD_DOT.get(status_colours.get(row.status or "") or "", "⚪")
        label = (row.status or "-").lower()
        label = _STATUS_LABELS.get(label, label)
        team = " 👥" if row.assignee_count > 1 else ""
        status = " ".join(filter(None, [f"{dot} {label}{team}", pr_refs(row)]))
        size = row.size or "-"
        est = f"{row.estimate:g}" if row.estimate is not None else "-"
        title = md_escape(row.title)
        if row.status == "Done":
            title = f"~~{title}~~"
        issue = f"[#{row.number} {title}]({row.url})"
        return f"| {prio_md} | {status} | {size} | {est} | {issue} |"

    out: list[str] = []
    all_my = [issue for g in groups for issue in g]
    # Top-down: headers in time order, current milestone first. The
    # reviewer table sits under each milestone, rolled up over the
    # milestone for a steadier read than a single iteration.
    for ms in milestones:
        meta = milestone_meta(ms, sep=" · ")
        out += [f"## [{md_escape(ms.title)}]({ms.html_url})", "", meta, ""]
        my_ms = [i for i in all_my if i.milestone == ms.number]
        stats = review_stats(my_ms, reverse_for_milestone(reverse, ms.number), me)
        if table := review_table_markdown(stats):
            out += [*table, ""]

    for g in groups:
        head = g[0]
        current = is_current_iteration(head.iteration_start, head.iteration_duration)
        span = iteration_date_range(
            head.iteration_start, head.iteration_duration, current=current
        )
        name = head.iteration or "No iteration"
        out += [
            f"### {name}" + (f" ({span})" if span else ""),
            "",
            "| Prio | Status | Sz | Est | Issue |",
            "|:--|:--|:--|:--|:--|",
            *(row_line(row) for row in g),
            "",
        ]
    return "\n".join(out).rstrip() + "\n"


def render_terminal(
    rows: list[Issue],
    groups: Groups,
    status_colours: dict[str, str],
    board: Board,
    me: Login | None,
    *,
    use_links: bool,
    use_colour: bool,
) -> str:
    """Render the board as the bottom-up ANSI terminal view (header, rows,
    iteration sections, milestone footers + reviewer tables), as one string.

    `groups` arrives pre-classified; `rows` is the flat filtered set (for
    column widths) and `board` carries the full issues + reverse data for
    the per-milestone reviewer tables.
    """
    num_width = max(len(str(r.number)) for r in rows) + 1  # "#NNN" column

    def build_cell(row: "Issue", dim_prs: frozenset[int]) -> Cell:
        raw_status = row.status
        emphasise = is_current_iteration(row.iteration_start, row.iteration_duration)
        status_rendered, status_vis = status_cell(
            row,
            status_colours.get(raw_status or ""),
            use_links=use_links,
            use_colour=use_colour,
            emphasise=emphasise,
            dim_prs=dim_prs,
        )
        # Priority weights P0/P1/P2 by emphasis; Done rows stay plain so
        # the row-wide dim reads. The code is always 2 chars, padded to 4.
        code = row.priority or "--"
        weight = _PRIORITY_WEIGHT.get(code) if raw_status != "Done" else None
        if use_colour and weight:
            prio_cell = f"{weight}{code}{_RESET}  "
        else:
            prio_cell = code.ljust(4)
        title = row.title
        if use_colour and raw_status == "Done":
            # Shipped: black title, kept at normal intensity so the
            # row-wide dim doesn't fade it into the background.
            title = f"{_UNDIM}{_DARK_GREY}{title}{_RESET}"
        elif use_colour and row.priority == "P2":
            title = f"{_DIM}{title}{_RESET}"  # low priority recedes
        label = f"#{str(row.number).ljust(num_width)} {title}"
        if use_colour and raw_status == "In Review":
            label = f"{_DIM}{label}{_RESET}"  # de-emphasise issues awaiting review
        return Cell(
            iteration=row.iteration,
            iteration_start=row.iteration_start,
            iteration_duration=row.iteration_duration,
            is_done=raw_status == "Done",
            prio=prio_cell,
            status=status_rendered,
            status_vis=status_vis,
            size=(row.size or "-").ljust(2),
            est=estimate_cell(row.estimate, use_colour=use_colour),
            issue=hyperlink(label, row.url, enabled=use_links),
        )

    # Order the groups top→bottom so the most-relevant work ends up most
    # visible when reading up from the prompt (see Groups.bottom_up).
    ordered_rows = groups.bottom_up()

    # Walk the final visual order bottom→top. A PR shows its real number
    # at the bottom of each *contiguous* run of rows sharing it; rows
    # directly above in that run collapse to an arrow. Adjacency (rather
    # than a global "lowest occurrence") means a PR split across far-apart
    # rows — e.g. a Done block reordered by priority — keeps its number on
    # each fragment instead of leaving a lone arrow pointing at a distant
    # row.
    visual = [row for g in ordered_rows for row in reversed(g)]
    dim_by_number: dict[int, frozenset[int]] = {}
    below_nums: set[int] = set()
    for row in reversed(visual):
        nums = {pr.number for pr in row.prs}
        dim_by_number[row.number] = frozenset(nums & below_nums)
        below_nums = nums

    # Pre-render each row's cells, remembering the status column's visible
    # width (it varies with appended PR refs) so every column stays aligned.
    status_width = len("STATUS")
    ordered: list[list[Cell]] = []
    for g in ordered_rows:
        cell_group = []
        for row in g:
            cell = build_cell(row, dim_by_number[row.number])
            status_width = max(status_width, cell.status_vis)
            cell_group.append(cell)
        ordered.append(cell_group)

    def pad(text: str, visible: int, target: int) -> str:
        return text + " " * max(0, target - visible)

    def dim_all(text: str) -> str:
        # Faint the whole row but keep nested colours by re-arming
        # dim after each reset that an inner colour code emits.
        return _DIM + text.replace(_RESET, _RESET + _DIM) + _RESET

    head = "\033[1;4m" if use_colour else ""  # bold + underline header
    column_header = (
        f"{head}{pad('PRIO', 4, 4)}  {pad('STATUS', 6, status_width)}  "
        f"{pad('SZ', 2, 2)}  {pad('EST', 3, 3)}  ISSUE{_RESET if use_colour else ''}"
    )

    def render_row(cell: Cell) -> str:
        line = (
            f"{cell.prio}  {pad(cell.status, cell.status_vis, status_width)}  "
            f"{cell.size}  {cell.est}  {cell.issue}"
        )
        return dim_all(line) if (use_colour and cell.is_done) else line

    width = int(os.environ.get("COLUMNS") or 80)

    def section_label(cell: Cell) -> str:
        name = cell.iteration or "No iteration"
        current = is_current_iteration(cell.iteration_start, cell.iteration_duration)
        span = iteration_date_range(
            cell.iteration_start, cell.iteration_duration, current=current
        )
        head = f"=== {name}  ({span}) " if span else f"=== {name} "
        label = head + "=" * max(3, width - display_width(head))
        return f"{_BOLD}{label}{_RESET}" if use_colour else label

    # Each group prints its rows reversed with the iteration header beneath
    # them; the column header sits at the bottom of the table, then the
    # milestone header. Quota footer follows via atexit. Read bottom-up to
    # recover the normal order.
    lines: list[str] = []
    for cell_group in ordered:
        lines += [render_row(c) for c in reversed(cell_group)]
        lines += [section_label(cell_group[0]), ""]
    lines.append(column_header)
    # Bottom-up: milestone headers sit below the table in reverse time
    # order, so the current one lands closest to the prompt. Only the
    # current milestone (earliest in time order) is bolded. Each carries
    # its reviewer table, rolled up over the milestone for a steadier
    # read than a single iteration.
    for ms in reversed(board.milestones):
        block = format_milestone(
            ms,
            use_links=use_links,
            use_colour=use_colour,
            current=ms is board.milestones[0],
        )
        my_ms = [i for i in board.issues if i.milestone == ms.number]
        stats = review_stats(my_ms, reverse_for_milestone(board.reverse, ms.number), me)
        table = review_table_terminal(stats, use_colour=use_colour)
        if table and use_colour and ms is not board.milestones[0]:
            table = [dim_all(t) for t in table]  # following milestone recedes
        lines += ["", *block.split("\n"), *table]
    return "\n".join(lines)


# MARK: - Sorting, classification & entry point


def sort_issues(
    issues: list[Issue],
    priority_rank: dict[str, int],
    status_rank: dict[str, int],
) -> list[Issue]:
    """Sort issues for display: iteration first (unscheduled last), then
    status (board order), then a priority-aware ordering that keeps a PR's
    issues together as one block. See `sort_key` for per-status tie-breaks.
    """
    n_prio = len(priority_rank)
    no_prio = n_prio + 1

    def own_prio(row: Issue) -> int:
        return priority_rank.get(row.priority or "", no_prio)

    def pr_number(row: Issue) -> float:
        return min((pr.number for pr in row.prs), default=float("inf"))

    def magnitude(counts: list[int]) -> tuple[int, ...]:
        # Negated per-rank counts: more high-priority tickets sort first,
        # ties broken by the next rank down (a single P0 still beats any
        # number of P1s).
        return tuple(-c for c in counts)

    # Per-(iteration, status, PR) tallies of how many tickets sit at each
    # priority rank, so a block of issues closed by one PR is weighed by
    # its whole priority profile rather than by PR number.
    group_counts: dict[tuple, list[int]] = {}
    for row in issues:
        pr = pr_number(row)
        if pr == float("inf"):
            continue
        counts = group_counts.setdefault(
            (row.iteration_start, row.status, pr), [0] * n_prio
        )
        rank = priority_rank.get(row.priority or "")
        if rank is not None:
            counts[rank] += 1

    def sort_key(row: Issue) -> tuple:
        # Iteration first (unscheduled last). Within an iteration, by
        # status (Backlog > Todo > In progress > In Review > Done, board
        # order). Within a status:
        #
        #   - Done rows order by priority *profile*, keeping a PR's issues
        #     together as one block (a PR-less issue is its own singleton),
        #     then by PR number, then own priority within the block — so
        #     shipped work scans by importance without scattering a PR's
        #     issues across tiers.
        #   - Not-yet-done rows put PR-less issues first (the table prints
        #     bottom-up, so PR-less work — what still needs a PR — lands
        #     most visible near the prompt), each by its own priority (not
        #     a group); then PR'd blocks by priority profile, PR number,
        #     and own priority within the block.
        #
        # Every tail ends with estimate (descending; none last) then number.
        start = row.iteration_start or "9999-99-99"
        status_key = status_rank.get(row.status or "", len(status_rank) + 1)
        tail = (-row.estimate if row.estimate is not None else float("inf"), row.number)
        pr_key = pr_number(row)
        has_pr = pr_key != float("inf")
        if has_pr:
            mag = magnitude(group_counts[(row.iteration_start, row.status, pr_key)])
        else:
            # Singleton so a PR-less Done row interleaves with PR blocks by
            # priority (Done groups by PR; other statuses keep PR-less first).
            single = [0] * n_prio
            if (rank := priority_rank.get(row.priority or "")) is not None:
                single[rank] = 1
            mag = magnitude(single)
        if row.status == "Done":
            return (start, status_key, mag, pr_key, own_prio(row), *tail)
        if has_pr:
            return (start, status_key, 1, mag, pr_key, own_prio(row), *tail)
        return (start, status_key, 0, own_prio(row), *tail)

    return sorted(issues, key=sort_key)


def classify_groups(rows: list[Issue]) -> Groups:
    """Group start-sorted rows into contiguous iterations and classify each
    relative to today (current / unscheduled / future / past)."""
    row_groups: list[list[Issue]] = []
    for row in rows:
        if not row_groups or row_groups[-1][0].iteration_start != row.iteration_start:
            row_groups.append([])
        row_groups[-1].append(row)

    current = noiter = None
    future: list[list[Issue]] = []
    past: list[list[Issue]] = []
    for g in row_groups:
        head = g[0]
        if head.iteration_start is None:
            noiter = g
        elif is_current_iteration(head.iteration_start, head.iteration_duration):
            current = g
        elif is_past_iteration(head.iteration_start, head.iteration_duration):
            past.append(g)
        else:
            future.append(g)
    return Groups(current=current, noiter=noiter, future=future, past=past)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--milestone",
        help="Exact milestone title; if omitted, the current open milestone "
        "(the one whose due date is closest to today) is used",
    )
    parser.add_argument(
        "--assignee",
        default="@me",
        help='GitHub login, "@me" (default), or "any" for unfiltered',
    )
    parser.add_argument(
        "--state",
        default="all",
        choices=["open", "closed", "all"],
        help='Issue state filter (default "all", so done/closed issues are shown)',
    )
    parser.add_argument(
        "--repo",
        default=git_remote_repo() or DEFAULT_REPO,
        help="owner/name (defaults to the origin remote of the current repo)",
    )
    parser.add_argument(
        "--project",
        type=int,
        default=DEFAULT_PROJECT,
        help="ProjectV2 number to read Iteration/Priority from",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the full result as JSON instead of a table",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Emit a top-down Markdown report instead of a terminal table",
    )
    parser.add_argument(
        "--no-hyperlink",
        action="store_true",
        help="Print bare URLs instead of OSC 8 terminal hyperlinks",
    )
    parser.add_argument(
        "--cache-ttl",
        type=int,
        default=60,
        metavar="SECONDS",
        help="Reuse a cached result newer than this many seconds "
        "(0 disables; default 60)",
    )
    args = parser.parse_args()
    # Always report quota on exit (but not for --help / arg errors,
    # which exit inside parse_args above, before this registration).
    atexit.register(report_rate_limit)

    owner, _, name = args.repo.partition("/")

    # Resolving "@me" is a local file read (no network), so it's safe
    # to do before the cache check; it also keeps the cache key
    # distinct per authenticated user.
    assignee_login = resolve_assignee_login(args.assignee)
    # Your own login drives the reverse review columns (their PRs you're
    # involved in); resolved locally, no network.
    me = Login(login) if (login := resolve_assignee_login("@me")) else None
    cache_key = "|".join(
        [
            args.repo,
            str(args.project),
            args.milestone or "<current+following>",
            str(assignee_login),
            str(me),
            args.state,
        ]
    )

    board = read_board_cache(cache_key, args.cache_ttl)
    if board is None:
        # A cheap lookup resolves the milestone window (the explicit
        # --milestone, or the current open milestone + the one following)
        # into dated spans. The forward board and the reverse review data
        # are independent given those spans, so fetch them concurrently.
        try:
            ranges = resolve_window(owner, name, args.milestone)
            if not ranges:
                sys.exit(
                    f"milestone {args.milestone!r} not found."
                    if args.milestone
                    else "No open milestone with a due date found."
                )
            milestone_numbers = [number for number, _, _ in ranges]
            with ThreadPoolExecutor(max_workers=2) as pool:
                reverse_future = pool.submit(
                    fetch_reverse, owner, name, args.project, ranges, me
                )
                board = fetch_board(
                    owner,
                    name,
                    args.project,
                    milestone_numbers,
                    assignee_login,
                    args.state,
                )
                board = replace(board, reverse=reverse_future.result())
            write_board_cache(cache_key, board)
        except RateLimitError:
            cached = _cache_path(cache_key)
            if os.path.exists(cached):
                age = int(time.time() - os.path.getmtime(cached))
                sys.stderr.write(
                    f"cached result from {age}s ago: {cached}\n"
                    f"  reuse it with: --cache-ttl {age + 60}\n"
                )
            else:
                sys.stderr.write(
                    "no cached result for this query yet — retry after the reset.\n"
                )
            sys.exit(1)
    options, milestones = board.options, board.milestones

    priority_rank = {
        o["name"]: i for i, o in enumerate(options.get(ProjectField.PRIORITY, []))
    }
    status_order = [o["name"] for o in options.get(ProjectField.STATUS, [])]
    status_rank = {name: i for i, name in enumerate(status_order)}
    status_colours = {
        o["name"]: o["color"] for o in options.get(ProjectField.STATUS, [])
    }

    rows = sort_issues(board.issues, priority_rank, status_rank)

    if args.json:
        # JSON is the raw fetched set (it already honours --state); no extra
        # filtering so it stays a faithful export. `reverse` is each teammate's
        # window PRs with your involvement (the reviewer tables' raw input).
        payload = {
            "milestones": [asdict(m) for m in milestones],
            "issues": [asdict(row) for row in rows],
            "reverse": {
                login: [asdict(pr) for pr in prs]
                for login, prs in board.reverse.items()
            },
        }
        print(json.dumps(payload, indent=2))
        return

    # Table view only: a past iteration contributes just its unfinished work.
    rows = [
        r
        for r in rows
        if not (
            r.status == "Done"
            and is_past_iteration(r.iteration_start, r.iteration_duration)
        )
    ]

    if not rows:
        print("No matching issues.", file=sys.stderr)
        return

    # Group rows into contiguous iterations and classify each relative to
    # today; both the table and the Markdown renderer order their output
    # from this.
    groups = classify_groups(rows)

    if args.markdown:
        print(
            render_markdown(
                milestones, groups.top_down(), status_colours, board.reverse, me
            ),
            end="",
        )
        return

    # OSC 8 hyperlinks and ANSI colour render in supporting terminals; both
    # degrade to plain text when piped/redirected. NO_COLOR disables colour
    # (https://no-color.org); --no-hyperlink disables links.
    is_tty = sys.stdout.isatty()
    use_links = is_tty and not args.no_hyperlink
    use_colour = is_tty and "NO_COLOR" not in os.environ
    print(
        render_terminal(
            rows,
            groups,
            status_colours,
            board,
            me,
            use_links=use_links,
            use_colour=use_colour,
        )
    )


if __name__ == "__main__":
    main()
