# BuildOS

**Project continuity and evidence-backed execution for Codex.**

BuildOS helps a coding agent retain the right context, keep work scoped, verify what changed,
and leave a useful handoff. It combines a short project contract, four skills, and a local
Python helper. Small tasks stay small; complicated work gets an explicit plan and evidence.

**0.3 is Codex-first.** The original Claude workflow remains in Git history. This release
replaces unsupported session hooks and universal deployment rules with tested local mechanics.
It does not claim to eliminate model errors or outperform simpler prompts without evaluation.

## What you get

| Capability | What it actually does |
|---|---|
| Setup | Previews a diff; adds AGENTS.md guidance and repository skills; preserves user documents; records file ownership |
| Work | Plan → build → verify → resume, with task tiers, stale-plan checks, and explicit partial/blocked states |
| Evidence | Executes an approved command; records exit status, private output, and tested Git/tree identity |
| Knowledge | Inventories private sources, tracks hashes and stale/deleted summaries; an agent performs cited summarization |
| Capture | Explicit, private session notes with stable IDs and duplicate/conflict protection |
| Maintenance | Doctor checks, conflict-aware upgrades, removal that retains modified work and private records |

No global settings, Git hooks, commits, pushes, background agents, schedules, or cloud services
are installed. The helper uses Python 3.10+ and its standard library; Git is needed for revision
binding and repository privacy checks. macOS and Linux are the supported test targets.

## Start in Codex

Clone this repository, then tell Codex:

> Read the buildos-setup skill at
> /absolute/path/to/buildos/plugins/buildos/skills/buildos-setup/SKILL.md
> and set up BuildOS in /absolute/path/to/my-project.

The skill discovers the project, asks only for important unknowns, previews the exact changes,
and applies them within your authorization. It does not start feature work as part of setup.
Open a **fresh Codex session in the target project** afterward. The installed skills are:

- `$buildos-setup` — setup, upgrade, doctor, removal.
- `$buildos-work` — plan, execute, verify, resume.
- `$buildos-knowledge` — refresh, summarize, query, correct.
- `$buildos-capture` — explicitly save durable session learning.

Repository skills live in `.agents/skills/`; the root `AGENTS.md` supplies project guidance.
The checkout also includes a validated `.codex-plugin/plugin.json` for plugin packaging.
Plugin marketplace/UI installation is not required for the documented repository-skill path.
See [compatibility](docs/COMPATIBILITY.md) for verified boundaries.

## Command-line setup

The target directory must already exist. From this checkout, preview:

```bash
python3 plugins/buildos/skills/buildos-setup/scripts/buildos.py init --target /path/to/project
```

Read the diff, then repeat with `--apply --expect-plan HASH`, replacing `HASH` with the printed
plan hash. If anything relevant changes, preview again. Default project facts explicitly mark
unknowns; for tailored facts add `--profile /path/to/profile.json` to **both** commands:

```json
{
  "name": "My project",
  "purpose": "What it delivers and for whom",
  "milestone": "The next useful outcome",
  "constraint": "The principle that resolves trade-offs",
  "verify": [["python3", "-m", "unittest", "discover"]],
  "overlays": []
}
```

Profiles and generated project docs are shareable: never put secrets or confidential domain
facts in them. Profiles configure checks; installation does not execute them. Optional overlays
are `web-saas` and `security-product` and are read only when relevant.

Installed layout:

```text
AGENTS.md                         short managed block; existing instructions retained
.agents/skills/buildos-*/          four skills, helper, and reusable templates
.buildos/install.json             version and ownership hashes; shareable
.buildos/local/                   private evidence and temporary inputs; ignored
BUILD_SESSION_PROMPTS.md           task status and acceptance evidence
ISSUES_AND_IMPROVEMENTS.md          defects, hypotheses, improvements
RESUME_HERE.md                     one current handoff pointer
docs/buildos/                     project facts and conditional guidance
knowledge/private/                created on use; sources, summaries, captures; ignored
knowledge/public/                 optional reviewed/redacted findings
```

Existing project documents are never silently replaced. Edited package files or managed blocks
cause a conflict instead of a forced overwrite. A monorepo install can target a subdirectory;
parent and nested instructions still apply. Existing AGENTS.override.md needs manual review.

## Working day to day

Ask Codex to use `$buildos-work` for the next task. For meaningful command evidence:

```bash
python3 .agents/skills/buildos-setup/scripts/buildos.py verify -- python3 -m unittest discover
python3 .agents/skills/buildos-setup/scripts/buildos.py doctor
```

`verify` executes exactly the argv following `--`, without a shell. Run only checks authorized
for the project and safe environment. A pass means that command succeeded on a stable recorded
tree, not that the entire feature is correct. Exit 3 means the result is unbound (no Git identity
or files changed during the check); inspect and rerun or disclose the limitation. Logs are private.

Drop approved source material into `knowledge/private/raw/`, then use `$buildos-knowledge`.
The helper tracks inventory and provenance; it does not magically extract PDFs or decide truth.
Use `$buildos-capture` before a handoff when there is substantive learning. Nothing runs on exit.

## Upgrade or remove

Use the helper from the newer checkout and repeat preview/apply. It updates unchanged package
files; tailored project documents stay intact. Resolve reported conflicts deliberately. Removal:

```bash
python3 .agents/skills/buildos-setup/scripts/buildos.py uninstall
```

Review, then repeat with `--apply --expect-plan HASH`. Changed files and knowledge/evidence
remain. Privacy ignore rules remain if private files remain. Empty directories are retained.
See [migration and recovery](docs/MIGRATION.md) for existing 0.2 projects and interrupted writes.

## Validation and limitations

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
```

The tests exercise real temporary directories and Git repositories. CI runs the same checks
on macOS/Linux with Python 3.10/3.14. [Validation report](docs/VALIDATION.md) separates executed
checks from unrun model comparisons. [Evaluation protocol](evals/README.md) provides reproducible
cases for ordinary instructions, compact BuildOS, and the complete workflow.

Automatic capture and Control Center are **deferred**, not shipped features. Their graduation
criteria are in [the roadmap](docs/ROADMAP.md). Claude support is a manual bridge (`init --claude`),
not a tested automation integration. See [SECURITY.md](SECURITY.md). MIT licensed.
