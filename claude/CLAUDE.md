# Global Claude Code instructions

General practice:

- Cite sources for factual claims
- Be thorough when refactoring. Use tools like grep to search for things that need updating, or language specific code parsing tools / ad-hoc scripts.
- Read permissions and common, allowed commands from `<project-root>/.claude/settings.local.json`.

- Several `gh` subcommands break on the deprecated classic-Projects `projectCards` GraphQL field: `gh pr edit` (leaves PR unchanged), `gh pr view`, and `gh issue view` (return no data). Workarounds via REST: view a PR with `gh api repos/<owner>/<repo>/pulls/<n>`; edit a PR title/body with `gh api -X PATCH repos/<owner>/<repo>/pulls/<n> -F body=@file.md` / `-f title=...`; view an issue with `gh api repos/<owner>/<repo>/issues/<n>`. `gh pr create` and `gh issue create/edit` are fine.
- When passing a file ref to `gh api`, `-F` (like `gh api -X POST ... -F body=@/tmp/claude/abc123/comment.md ...`) is usually the correct flag (instead of `f`). When in doubt, check the manpage.
- In a git repo, run `git update-index --chmod=+x` for new executable scripts.

## Bash: long-output commands

When a Bash-tool command is expected to produce long output (e.g. `pytest`, `git commit` with hooks, builds, deep `git log`, broad `grep`/`rg` over large trees), `tee` it to a file under `/tmp/claude/<random-per-session-slug>/` before piping to `head` or `tail` so you keep the full output on disk *and* still get the inline preview.

**Why:** Piping straight to `head`/`tail` discards the rest. If more lines are needed later (or both ends, or a `grep` for a specific failure), the command has to be re-run — slow, expensive, or taxing on system resources. `tee`-ing to a file gives the inline preview now *and* lets any other portion be inspected at leisure with whatever fits (Read tool, `grep`, `awk`, `wc`, etc.) — no re-run.

**How to apply:**
- Pick a random slug per session (e.g. `/tmp/claude/a3f9k2/`) and reuse it for all logs that session.
- Pattern: `command 2>&1 | tee /tmp/claude/<slug>/<descriptive-name>.log | tail -n 50` (use `head` if leading lines matter more). `2>&1` captures stderr too.
- If no inline preview is needed, redirect instead: `command > /tmp/claude/<slug>/<name>.log 2>&1`.
- Inspect the file after with whatever fits best: Read tool (with `offset`/`limit`) for a region, `grep`/`rg` to find specific lines, `wc -l` for size, `awk`/`sed` for slicing.
