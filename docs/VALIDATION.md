# Validation record

Date: 2026-09-18. This describes the Codex-first 0.3 branch, not the earlier 0.2 release.

## Executed locally

Python 3.14.2 on macOS, using disposable directories/repositories:

The implementation run completed **27 tests** (29 at 0.3.1), the offline package/reference checker, and
`git diff --check`. The supplied Codex Plugin Creator validator and all four Skill Creator
validators also passed, using PyYAML in a temporary environment outside this repository.

- Read-only previews and stale-plan refusal.
- Installation, zero-diff rerun, upgrades, and self-contained installed helper.
- Existing instructions, project documents, hook configuration, and staged work preserved.
- Unowned files, changed managed blocks, and symlink destinations rejected.
- Content rollback after an injected write failure.
- Subdirectory installation in a monorepo and non-Git installation.
- Removal preserves modified files and privacy rules for retained private data.
- Tracked sensitive files detected; changed/deleted/unsupported knowledge handled explicitly.
- Source-hash checks and prior-summary history.
- Identical capture retries, conflict rejection, concurrent writers, and empty captures.
- Real command success/failure, timeout, changed-tree detection, stale evidence, and altered logs.
- A complete helper lifecycle: setup, failing check, code fix, passing evidence, capture, index
  refresh, and a new process reading persisted resume state. This is not a fresh model-session trial.
- Claude Code install (0.3.1): `--claude` mirrors the skills to `.claude/skills/`, imports
  AGENTS.md from CLAUDE.md, preserves existing CLAUDE.md content, upgrades the 0.3.0 bridge, and
  uninstalls cleanly. `claude plugin validate` passed for the plugin and marketplace.
- Evaluation aggregation preserves failures, separates model/revision cohorts, rejects duplicate
  or incomplete records, and never invents missing trials.

Run `python3 -m unittest discover -s tests -v` to reproduce the current suite. The suite is the
authoritative case list; additions may increase the test count. Run `python3 scripts/check_repository.py`
for packaging, versions, entrypoints, and local links. GitHub Actions is configured for macOS/Linux
and Python 3.10/3.14; configured checks are not claims that those remote runs have passed.

## Limits

No controlled repeated model comparisons have been run. The provided evaluation protocol and
fixtures do not establish a success-rate, cost, or productivity improvement. Session capture
semantics still depend on the model reading and summarizing honestly. Evidence binds a command
to local tracked/nonignored files, excluding the three handoff documents (tasks/issues/resume),
external systems, ignored artifacts, and submodule contents.

No automatic session lifecycle, scheduler, or Control Center is installed or claimed tested.
Claude support was checked by one headless Claude Code 2.1.291 session that listed the installed
skills and the loaded AGENTS.md contract; full Claude workflow sessions are not validated here. The local
Codex CLI version inspected was 0.154.0; configuration discovery and model behavior should be
checked in a fresh session in each adopting project. Package validation is not that runtime test.
