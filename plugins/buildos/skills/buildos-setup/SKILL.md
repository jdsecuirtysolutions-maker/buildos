---
name: buildos-setup
description: Set up, upgrade, inspect, or remove BuildOS project instructions and skills when the user requests BuildOS installation or maintenance.
---

# BuildOS setup

Use the Python 3.10+ helper at `scripts/buildos.py` relative to this skill.
Resolve its absolute path from the loaded skill location, not the working directory.
It works from the plugin or an installed project copy.

1. Establish the requested target. Read existing instructions, relevant stack manifests,
   working-tree status, and deployment/test configuration. In a monorepo, scope installation
   to the requested project; report parent/nested instruction conflicts. Check for
   `AGENTS.override.md`, which can supersede the generated AGENTS.md.
2. Infer facts from code. Ask only for a missing product goal, milestone, trade-off constraint,
   or material preference. Existing authorization persists; do not ask to approve setup again.
   Do not ingest sensitive documents merely to bootstrap.
3. Create a temporary profile JSON with public facts only: `name`, `purpose`, `milestone`,
   `constraint`, `verify` (list of argv lists), `overlays` (zero or more of `web-saas`,
   `security-product`). Commands are configuration, not permission to execute. Record unknowns
   explicitly rather than inventing facts.
4. Run `python3 <helper> init --target <project> --profile <profile.json>`. Inspect the diff
   and warnings. Preview writes nothing. Apply the same inputs with
   `--apply --expect-plan <printed-hash>` when installation is authorized. A changed payload
   or target requires another preview. Unowned/edited package files cause a refusal; resolve
   the specific conflict, never blanket overwrite. Existing project documents are preserved;
   merge relevant facts deliberately if they already exist.
5. Run `python3 <helper> doctor --target <project>`. Tailor `docs/buildos/PROJECT.md` and
   `RESUME_HERE.md`; seed one useful task in `BUILD_SESSION_PROMPTS.md` when the goal is known.
   Use its entry-gate/evidence fields for complex work. No generic backlog is required.
   Verify generated references resolve. Report unknowns and conflicts.
6. Explain where files landed and the first task. Start a fresh Codex session in the target
   so AGENTS.md and `.agents/skills/` are discovered. Setup stops here; feature implementation
   requires scope that includes it.

For upgrades, run the helper from the newer BuildOS checkout. Unchanged owned assets update;
project documents are seed-once. `--claude` adds a CLAUDE.md bridge: secondary manual
compatibility, not tested Claude automation.

For removal, preview `uninstall --target <project>`, then use the same apply/hash flags.
It removes unchanged owned content and unedited managed blocks, retaining modified files,
knowledge, evidence, and user additions. Inspect the report for retained blocks.

The helper never commits, pushes, changes Git hooks, schedules work, reads ambient transcripts,
or installs into user-wide settings. A preview hash prevents applying a stale diff; it is not
approval or a sandbox. A process crash can leave a stale lock or partial files: inspect the
working diff and ownership record before recovery.
