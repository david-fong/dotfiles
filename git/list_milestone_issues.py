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
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any

DEFAULT_REPO = "detektra/detektra"  # fallback when not run inside a git repo
DEFAULT_PROJECT = 13  # "Detektra Product Development"


class ProjectField(StrEnum):
    """Project-board field names (members act as their str value)."""

    ITERATION = "Iteration"
    PRIORITY = "Priority"
    SIZE = "Size"
    ESTIMATE = "Estimate"
    STATUS = "Status"


# OSC 8 terminal hyperlink: \033]8;;URL\033\\ TEXT \033]8;;\033\\
_OSC8 = "\033]8;;{url}\033\\{text}\033]8;;\033\\"

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_UNDIM = "\033[22m"  # normal intensity (cancels an enclosing dim)
_DARK_GREY = "\033[38;5;238m"  # faded foreground, for shipped (Done) titles

# Priority text weight: P0 stands out (bold), P1 is normal, P2 recedes
# (dim). Codes absent here render plain.
_PRIORITY_WEIGHT = {"P0": _BOLD, "P2": _DIM}

# Shorter display labels for some board statuses (display only; the
# board's own names still drive sorting, colours, and emphasis).
_STATUS_LABELS = {"in progress": "wip", "in review": "rvw"}

# Signals shown next to a still-open PR's number.
_REVIEW_GLYPH = {"changes_requested": "🚧", "approved": "✅"}
_BEHIND_GLYPH = "🍂"  # head branch is out of date with its base
_DRAFT_GLYPH = "📝"  # PR is still a draft
_TEAM_GLYPH = "👥"  # issue assigned to more than one person
_NO_REVIEWER_GLYPH = "🚨"  # ready PR (not draft) with no reviewer assigned
_WIDE_GLYPHS = (
    *_REVIEW_GLYPH.values(),
    _BEHIND_GLYPH,
    _DRAFT_GLYPH,
    _TEAM_GLYPH,
    _NO_REVIEWER_GLYPH,
)

# Stand-in for a PR number that recurs brighter lower down: a down
# arrowhead (U+2304) pointing at the leading (bottom-most) row.
_DUP_PR = "⌄"


def display_width(text: str) -> int:
    """Visible width, counting (double-wide) PR emojis as 2 cells."""
    return len(text) + sum(text.count(glyph) for glyph in _WIDE_GLYPHS)


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
    prs: list[PullRequest]


@dataclass(frozen=True, slots=True, kw_only=True)
class Milestone:
    """Milestone header metadata (counts are issues only, not PRs)."""

    title: str
    description: str | None
    html_url: str
    state: str
    due_on: str | None
    open_issues: int
    closed_issues: int


@dataclass(frozen=True, slots=True, kw_only=True)
class Board:
    """Everything one GraphQL round-trip returns for a milestone."""

    issues: list[Issue]
    options: dict[str, list[dict]]
    """Each single-select field name → its options, in board order.

    Each option is a {"name", "color"} dict.
    """
    milestones: list[Milestone]
    """The milestones in view (one, or current + following), in time order
    (earliest first). Each renderer arranges its own display order."""


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


def weekdays_until(end_date: datetime.date) -> int:
    """Count of weekdays (Mon–Fri) from today through `end_date`, inclusive."""
    day, count = datetime.date.today(), 0
    while day <= end_date:
        if day.weekday() < 5:
            count += 1
        day += datetime.timedelta(days=1)
    return count


def iteration_date_range(
    start: str | None, duration: int | None, *, current: bool = False
) -> str | None:
    """Format an iteration's span and the time until its end.

    E.g. "2026-05-25 – 2026-06-07, ends in 4 days" (end inclusive). For
    the current iteration, the tail is weekdays remaining instead.
    """
    if not start or not duration:
        return None
    start_date = datetime.date.fromisoformat(start)
    end_date = start_date + datetime.timedelta(days=duration - 1)
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
    if not start or not duration:
        return False
    start_date = datetime.date.fromisoformat(start)
    end_date = start_date + datetime.timedelta(days=duration - 1)
    return start_date <= datetime.date.today() <= end_date


def is_past_iteration(start: str | None, duration: int | None) -> bool:
    """True when the iteration's (inclusive) end date is before today."""
    if not start or not duration:
        return False
    start_date = datetime.date.fromisoformat(start)
    end_date = start_date + datetime.timedelta(days=duration - 1)
    return end_date < datetime.date.today()


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


def format_milestone(
    ms: Milestone, *, use_links: bool, use_colour: bool, current: bool = True
) -> str:
    """Two-line milestone header (title, due date, progress).

    Bolded only when `current`, so a following milestone reads quieter.
    """
    title = hyperlink(ms.title, ms.html_url, enabled=use_links)
    closed, total = ms.closed_issues, ms.open_issues + ms.closed_issues
    pct = f"{round(100 * closed / total)}%" if total else "—"
    progress = f"{closed}/{total} closed ({pct})"
    if ms.due_on:
        due = datetime.datetime.fromisoformat(ms.due_on).date()
        meta = f"Due {due.isoformat()} ({relative_day_phrase(due)})  ·  {progress}"
    else:
        meta = f"No due date  ·  {progress}"
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
_ESTIMATE_GREY = {1: 246, 2: 249, 3: 251, 4: 253, 5: 255}


def estimate_cell(estimate: float | None, *, use_colour: bool) -> str:
    """Estimate padded to 3 cols, brighter the higher the value."""
    text = (f"{estimate:g}" if estimate is not None else "-").ljust(3)
    if not use_colour or estimate is None:
        return text
    code = _ESTIMATE_GREY[max(1, min(5, round(estimate)))]
    return f"\033[38;5;{code}m{text}{_RESET}"


# GitHub single-select option colours → 256-colour code for
# the status dot.
_GH_DOT = {
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
_MD_DOT = {
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


def _reset_phrase(info: dict) -> str:
    """'resets at HH:MM:SS (in 3m 20s)' for a rate-limit resource."""
    reset = datetime.datetime.fromtimestamp(info["reset"], datetime.timezone.utc)
    secs = max(
        0, int((reset - datetime.datetime.now(datetime.timezone.utc)).total_seconds())
    )
    mins, rem = divmod(secs, 60)
    local = reset.astimezone().strftime("%H:%M:%S")
    return f"resets at {local} (in {mins}m {rem}s)"


def rate_limit_hint(args: list[str]) -> str | None:
    """A 'resets at ...' hint for a rate-limited request, or None.

    Reads the free `rate_limit` endpoint (which doesn't count against
    any limit) for the resource that the failing request used.
    """
    probe = subprocess.run(
        ["gh", "api", "rate_limit"], capture_output=True, text=True, check=False
    )
    try:
        resources = json.loads(probe.stdout)["resources"]
    except (json.JSONDecodeError, KeyError):
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
    probe = subprocess.run(
        ["gh", "api", "rate_limit"], capture_output=True, text=True, check=False
    )
    try:
        resources = json.loads(probe.stdout)["resources"]
    except (json.JSONDecodeError, KeyError):
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


def graphql(query: str, **variables: Any) -> dict[str, Any]:
    # -F coerces ints/bools (needed for Int! vars); -f keeps
    # strings verbatim so a search query or milestone title isn't
    # reinterpreted.
    args = ["api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        flag = "-F" if isinstance(value, int) else "-f"
        args += [flag, f"{key}={value}"]
    return json.loads(gh(args))


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


# GraphQL fragment: an issue's board field values + the PRs that
# close it. We pull exactly the five board fields we need by name
# (via fieldValueByName) rather than paging the whole fieldValues
# connection — cheaper and order-proof.
# (Indentation is cosmetic — GraphQL ignores whitespace.)
_ISSUE_BOARD_FIELDS = f"""
  number title url state
  assignees(first: 1) {{ totalCount }}
  closedByPullRequestsReferences(first: 5, includeClosedPrs: true) {{
    nodes {{
      number url state isDraft mergeStateStatus
      headRefName headRepository {{ url }}
      reviewRequests {{ totalCount }}
      reviews {{ totalCount }}
      latestOpinionatedReviews(first: 10) {{ nodes {{ state }} }}
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


def extract_project_values(issue: dict, project: int) -> Issue:
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
        # Each reviewer's latest opinionated (approve/changes) review.
        states = {r["state"] for r in pr["latestOpinionatedReviews"]["nodes"]}
        if "CHANGES_REQUESTED" in states:
            review = "changes_requested"
        elif "APPROVED" in states:
            review = "approved"
        else:
            review = None
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
    )


def fetch_board(
    owner: str,
    name: str,
    project: int,
    milestone_titles: list[str],
    assignee_login: str | None,
    state: str,
) -> Board:
    """One round-trip: issues, single-select options, and milestone(s).

    Folds what used to be four `gh` calls (issue list, project fields,
    batched project values, milestone REST) into a single GraphQL
    request. Each milestone is looked up by exact title via its own
    aliased connection; issues come from the milestone's live `issues`
    connection (real-time, unlike the search index), filtered server-side
    by assignee/state, with board fields inline. Issues from every
    milestone are merged into one board.
    """
    states = {"open": "[OPEN]", "closed": "[CLOSED]"}.get(state, "[OPEN, CLOSED]")
    if assignee_login:
        login_decl = ", $login: String!"
        issue_args = f"first: 100, states: {states}, filterBy: {{assignee: $login}}"
    else:
        login_decl = ""
        issue_args = f"first: 100, states: {states}"

    # One aliased milestone lookup per title. `first: 3` leaves room for
    # the title search to return near-matches we filter out client-side,
    # while keeping the node-cost budget safe for up to a couple of them.
    ms_fields = f"""
        title description url state dueOn
        openIssues: issues(states: OPEN) {{ totalCount }}
        closedIssues: issues(states: CLOSED) {{ totalCount }}
        matched: issues({issue_args}) {{
          pageInfo {{ hasNextPage }}
          nodes {{ {_ISSUE_BOARD_FIELDS} }}
        }}
    """
    ms_var_decls = "".join(f", $ms{i}: String!" for i in range(len(milestone_titles)))
    ms_blocks = "\n".join(
        f"m{i}: milestones(query: $ms{i}, first: 3) {{ nodes {{ {ms_fields} }} }}"
        for i in range(len(milestone_titles))
    )
    variables: dict[str, Any] = dict(owner=owner, name=name, project=project)
    if assignee_login:
        variables["login"] = assignee_login
    for i, title in enumerate(milestone_titles):
        variables[f"ms{i}"] = title

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
    for i, title in enumerate(milestone_titles):
        ms_node = next((m for m in repo[f"m{i}"]["nodes"] if m["title"] == title), None)
        if ms_node is None:
            continue
        if ms_node["matched"]["pageInfo"]["hasNextPage"]:
            print(
                f"warning: milestone {title!r} has more than 100 matching issues; "
                "only the first 100 were fetched.",
                file=sys.stderr,
            )
        milestones.append(
            Milestone(
                title=ms_node["title"],
                description=ms_node["description"],
                html_url=ms_node["url"],
                state=ms_node["state"],
                due_on=ms_node["dueOn"],
                open_issues=ms_node["openIssues"]["totalCount"],
                closed_issues=ms_node["closedIssues"]["totalCount"],
            )
        )
        issues.extend(
            extract_project_values(n, project) for n in ms_node["matched"]["nodes"]
        )
    return Board(issues=issues, options=options, milestones=milestones)


def fetch_milestone_window(owner: str, name: str) -> list[str]:
    """Titles of the current open milestone and the one following it.

    "Current" is the open milestone whose due date is nearest today.
    "Following" is the next one by milestone number (creation order),
    since the upcoming milestone often has no due date yet — ordering by
    due date alone would miss it. Returns `[current, following]`,
    `[current]` if current is the last, or `[]` if none have a due date.
    GitHub can't surface the active milestone server-side (null due dates
    sort first, no due-date predicate), so we choose client-side. Cheap —
    no issue/project traversal.
    """
    data = graphql(
        """
        query($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) {
            milestones(first: 100, states: OPEN) { nodes { number title dueOn } }
          }
        }
        """,
        owner=owner,
        name=name,
    )
    today = datetime.date.today()
    nodes = data["data"]["repository"]["milestones"]["nodes"]
    dated = [
        (abs((datetime.datetime.fromisoformat(m["dueOn"]).date() - today).days), m)
        for m in nodes
        if m["dueOn"]
    ]
    if not dated:
        return []
    current = min(dated)[1]
    titles = [current["title"]]
    later = [m for m in nodes if m["number"] > current["number"]]
    if later:
        titles.append(min(later, key=lambda m: m["number"])["title"])
    return titles


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

    def revive(issue: dict) -> Issue:
        prs = [PullRequest(**pr) for pr in issue.pop("prs", [])]
        return Issue(**issue, prs=prs)

    try:
        return Board(
            issues=[revive(issue) for issue in data["issues"]],
            options=data["options"],
            milestones=[Milestone(**m) for m in data["milestones"]],
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


def render_markdown(
    milestones: list[Milestone],
    groups: list[list[Issue]],
    status_colours: dict[str, str],
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
    # Top-down: headers in time order, current milestone first.
    for ms in milestones:
        closed, total = ms.closed_issues, ms.open_issues + ms.closed_issues
        pct = f"{round(100 * closed / total)}%" if total else "—"
        progress = f"{closed}/{total} closed ({pct})"
        if ms.due_on:
            due = datetime.datetime.fromisoformat(ms.due_on).date()
            meta = f"Due {due.isoformat()} ({relative_day_phrase(due)}) · {progress}"
        else:
            meta = f"No due date · {progress}"
        out += [f"## [{md_escape(ms.title)}]({ms.html_url})", "", meta, ""]

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
        help="Reuse a cached result newer than this many seconds (0 disables; default 60)",
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
    cache_key = "|".join(
        [
            args.repo,
            str(args.project),
            args.milestone or "<current+following>",
            str(assignee_login),
            args.state,
        ]
    )

    board = read_board_cache(cache_key, args.cache_ttl)
    if board is None:
        # With an explicit --milestone, fetch just that one; otherwise a
        # cheap lookup picks the current open milestone and the one
        # following it. A single GraphQL round-trip then fetches the
        # matching issues (board fields inline), project options, and the
        # milestone(s).
        try:
            if args.milestone:
                titles = [args.milestone]
            else:
                titles = fetch_milestone_window(owner, name)
            if not titles:
                sys.exit(
                    "No --milestone given and no open milestone with a due date found."
                )
            board = fetch_board(
                owner, name, args.project, titles, assignee_login, args.state
            )
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
    for row in board.issues:
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

    rows = sorted(board.issues, key=sort_key)

    if args.json:
        # JSON is the raw fetched set (it already honours --state); no extra
        # filtering so it stays a faithful export.
        payload = {
            "milestones": [asdict(m) for m in milestones],
            "issues": [asdict(row) for row in rows],
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
        print("No matching issues.")
        return

    # Group rows into contiguous iterations (rows are already start-sorted)
    # and classify each group relative to today; both the table and the
    # Markdown renderer order their output from this.
    row_groups: list[list[Issue]] = []
    for row in rows:
        if not row_groups or row_groups[-1][0].iteration_start != row.iteration_start:
            row_groups.append([])
        row_groups[-1].append(row)

    current_g = noiter_g = None
    future: list[list[Issue]] = []
    past: list[list[Issue]] = []
    for g in row_groups:
        head_row = g[0]
        if head_row.iteration_start is None:
            noiter_g = g
        elif is_current_iteration(
            head_row.iteration_start, head_row.iteration_duration
        ):
            current_g = g
        elif is_past_iteration(head_row.iteration_start, head_row.iteration_duration):
            past.append(g)
        else:
            future.append(g)

    if args.markdown:
        # Top-down reading order: current first, then upcoming iterations
        # (soonest first), unscheduled, then past (most recent first).
        md_groups = (
            ([current_g] if current_g else [])
            + sorted(future, key=lambda g: g[0].iteration_start or "")
            + ([noiter_g] if noiter_g else [])
            + sorted(past, key=lambda g: g[0].iteration_start or "", reverse=True)
        )
        print(render_markdown(milestones, md_groups, status_colours), end="")
        return

    # OSC 8 hyperlinks and ANSI colour render in supporting
    # terminals; both degrade to plain text when piped/redirected.
    # NO_COLOR disables colour (https://no-color.org); --no-hyperlink
    # disables links.
    is_tty = sys.stdout.isatty()
    use_links = is_tty and not args.no_hyperlink
    use_colour = is_tty and "NO_COLOR" not in os.environ

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

    # Order the groups top→bottom: future iterations (latest start on top,
    # so the soonest-ahead sits lowest), then no-iteration, then the
    # current iteration, then past iterations at the very bottom (newest
    # higher, oldest lowest). Most-relevant work ends up most visible when
    # reading up from the prompt.
    future.sort(key=lambda g: g[0].iteration_start or "", reverse=True)
    past.sort(key=lambda g: g[0].iteration_start or "", reverse=True)
    ordered_rows = (
        future
        + ([noiter_g] if noiter_g else [])
        + ([current_g] if current_g else [])
        + past
    )

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
    for g in ordered:
        lines += [render_row(c) for c in reversed(g)]
        lines += [section_label(g[0]), ""]
    lines.append(column_header)
    # Bottom-up: milestone headers sit below the table in reverse time
    # order, so the current one lands closest to the prompt. Only the
    # current milestone (earliest in time order) is bolded.
    for ms in reversed(milestones):
        block = format_milestone(
            ms,
            use_links=use_links,
            use_colour=use_colour,
            current=ms is milestones[0],
        )
        lines += ["", *block.split("\n")]
    print("\n".join(lines))


if __name__ == "__main__":
    main()
