# Migration and recovery

## From a BuildOS 0.2 project

1. Inspect Git status, existing CLAUDE.md, trackers, knowledge locations, `.claude/settings.json`,
   `.githooks/`, and `git config --get core.hooksPath`. Preserve uncommitted and staged work.
2. Preview 0.3 setup from the newer checkout. Existing project documents stay in place. The new
   AGENTS.md contract and installed skills do not automatically repair old, conflicting prose.
   Merge project-specific facts into docs/buildos/PROJECT.md and intentionally retire old
   universal force-add/revert/approval rules from the project's instructions.
3. If the old session-capture hook is present, review the exact SessionEnd entry and remove only
   that BuildOS entry within the user's migration authorization. Never overwrite the settings
   file or remove unrelated hooks. Retire its unused prompt only after confirming references.
4. Keep any existing commit-msg hook until its owner chooses to remove it. Version 0.3 installs
   none and does not change core.hooksPath. If removing the last hook, restore the known prior
   hook configuration, not a guessed default. No test commits are made in the user's index.
5. Existing knowledge/raw, compiled, sessions, and INDEX.md are ignored but not moved. Review and
   migrate approved sources into knowledge/private/raw/. Preserve originals and source locators;
   rebuild summaries rather than treating old summaries as primary evidence. Doctor flags data
   already tracked; address history/disclosure separately instead of silently rewriting it.
6. Doctor, inspect the final diff, and open a fresh Codex session. Verify the next task can be
   resumed. Do not claim Claude lifecycle compatibility from a manifest check.

## Upgrades within 0.3

The installation record stores ownership hashes and the public setup profile. Unchanged package
files can update. Changed package files/managed blocks conflict; compare and merge intentionally.
Project documents are seeded once and remain yours. A new profile does not overwrite a tailored
PROJECT.md; edit that document deliberately. If switching capabilities/overlays, preview and check
that instructions and project facts agree.

Projects installed with the 0.3.0 `--claude` bridge upgrade automatically to the 0.3.1 form: the
unedited CLAUDE.md block becomes an `@AGENTS.md` import and the skills are added to
`.claude/skills/`. An existing, unowned `.claude/skills/buildos-*` file is a conflict, not overwritten.

## Uninstall

Preview removal first. Unchanged owned files and unedited managed blocks are removed; modified
files, user documents, private records, and empty directories remain. Privacy ignore rules are
retained when private knowledge/evidence remains. Removing those rules later can expose data.
The ownership record is removed; retained edits become user-owned and may conflict on reinstall.

## Interrupted writes

A caught write failure rolls back file contents; created empty directories may remain. A process
crash or machine failure is not a transactional filesystem guarantee. A stale `.buildos/write.lock`
records PID/time. Confirm the writer is no longer active before removing that lock. Inspect Git
diff and `.buildos/install.json`; preserve modified/unowned files. Preview again and resolve
specific conflicts. Never use a blanket Git reset or deletion to recover setup.
