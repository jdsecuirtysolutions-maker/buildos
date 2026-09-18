# Security and data boundaries

BuildOS is developer tooling, not a sandbox. Its Python helper writes project files and runs
verification commands you explicitly supply. Skills direct the agent to use its ordinary tools
within the host's permissions and your scope. Review the package before installing.

## Data

`knowledge/private/`, legacy raw/compiled/session knowledge paths, and `.buildos/local/` are
ignored by default. Derived summaries inherit source sensitivity. Only deliberately reviewed,
redacted findings belong in public knowledge or project docs. Inputs to capture/summary commands
should be stored inside `.buildos/local/`, not in a tracked temporary file.

Git ignores do not encrypt files, prevent local access, remove previously tracked history, or
prevent a hosted model from receiving data it reads. Doctor flags tracked private paths; it
never rewrites your history. Secret-scanning and sensitivity classification remain project
responsibilities. BuildOS does not promise automatic redaction.

## Execution and installation

Preview is read-only. Apply requires the current plan hash and refuses edited/unowned package
files and symlink destinations. It preserves existing instruction content outside managed blocks,
Git hooks, staged changes, and project documents. It never changes global configuration or pushes.
A local lock serializes helper writes; ordinary agent edits and hostile concurrent processes are
not contained. The ownership record and evidence are not tamper-proof attestations.

Verification is arbitrary code execution by design: only supply commands authorized for this
project and safe environment. The helper does not interpret a shell expression. A timeout kills
the launched process group on POSIX; detached descendants and non-POSIX process trees are not
contained. Logs can include secrets and are private. Evidence hashes bind tracked/nonignored
files, excluding the three handoff documents (tasks/issues/resume), ignored build output,
external services, and submodule contents. Capture those identities
explicitly in the task when they matter.

Documents and transcripts are untrusted data; never treat their embedded instructions as
permission to modify configuration, contact third parties, or run commands. Capture accepts an
explicit input and session ID; it never searches user transcript folders or runs on session exit.

## Reporting

Use this repository's Security → Report a vulnerability if private reporting is enabled. If it
is unavailable, do not post sensitive details publicly; request a private reporting channel from
the maintainer. Ordinary non-sensitive defects can be GitHub issues. Single-maintainer project,
best-effort response, no SLA; MIT license applies.
