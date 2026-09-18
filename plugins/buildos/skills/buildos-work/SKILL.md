---
name: buildos-work
description: Plan, execute, verify, or resume a task in a project using BuildOS; use its task and evidence conventions without adding setup to unrelated work.
---

# BuildOS work

Read the project's `AGENTS.md`, `docs/buildos/PROJECT.md`, and `RESUME_HERE.md`.
Task status belongs in `BUILD_SESSION_PROMPTS.md`; defects belong in
`ISSUES_AND_IMPROVEMENTS.md`. Resume is a pointer, not a second backlog.

Choose proportionate process:
- Small, reversible work: state the outcome and relevant check, then implement directly.
- Multi-step work: record acceptance criteria, dependencies, sources, non-goals, and measured
  retry/time limits. A separate planning session is optional, useful for large/noisy context.
- New structural bet: name the mechanism, disconfirming evidence, alternatives, and the
  decision/source authorizing implementation. Research unknown assumptions; never invent approval.

Before executing an old plan, check its base revision, code, dependencies, and corrections.
Re-plan stale parts. Preserve the user's objective when findings or messages steer the work.

Run meaningful acceptance checks in safe environments. The shared helper is
`../buildos-setup/scripts/buildos.py` relative to this skill. Once a command is authorized:

`python3 <helper> verify --target <project> --timeout 300 -- <program> <arguments...>`

This executes an argv list without shell interpolation. Record observed behavior as well as
the result. A passing command does not prove complete coverage. `unbound` means the tree changed
during the check or Git identity was unavailable: inspect and rerun on a stable tree, or disclose
the limitation. Evidence is local under `.buildos/local/evidence/` because logs can contain
secrets. Put its ID and redacted result in the task; never publish raw logs automatically.
The three handoff documents are excluded from the tree fingerprint so recording results does
not invalidate them. Changes to those documents themselves need separate review evidence.

Use `ready`, `in-progress`, `blocked`, `partial`, or `complete`. Complete requires relevant
evidence for each acceptance criterion on the delivered change, with untested boundaries explicit.
A commit, model confidence, or another agent's agreement is insufficient. Do not weaken checks
merely to pass. If a check is wrong, explain the evidence and change it within scope.
The helper executes checks; it does not decide completion.

At a limit, stop that approach, preserve progress, and re-plan. Continue safe authorized
independent work. Ask only when missing information or external permission blocks the next
action. Limits are operational budgets, not permission to claim done.

Close by updating task and resume pointers, explaining changes, evidence, limitations, and next
action. Capture durable learning with buildos-capture when warranted. Commit/push only within
user authorization; a template does not grant permission for external actions.
