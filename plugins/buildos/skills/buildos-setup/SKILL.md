---
name: buildos-setup
description: "Bootstrap a project with BuildOS: engineering-discipline rules, a BUG/IMP tracker, the two-phase build model, loops, a knowledge base, and project-fit automation."
disable-model-invocation: true
allowed-tools: Bash Read Write Edit Grep Glob
---

# BuildOS Setup

You are bootstrapping a project with **BuildOS** — a portable operating system for
AI-assisted builds (engineering constraints, disciplined docs, root-cause debugging, the
two-phase build-session model, and loop methodology). The reusable templates are bundled at
`${CLAUDE_SKILL_DIR}/templates/`. Your job is to deploy them into the current working
directory and tailor them to THIS project through discovery and planning.

Run the phases below in order. Do not skip Discover — a generic CLAUDE.md full of unfilled
`<FILL: ...>` placeholders is worse than none. The value is in the tailoring.

> Apply the OS's own discipline while running this: verify before asserting, ask when a
> choice genuinely matters but default when it's obvious, and never clobber existing work
> without confirming.

---

## Phase 0 — Orient

1. Establish the target directory = the user's current working directory. Confirm it with
   the user in one line ("Initializing BuildOS in `<cwd>` — correct?") unless they already
   named a directory as an argument.
2. **Idempotency / safety check.** Look for an existing `CLAUDE.md`, `ISSUES_AND_IMPROVEMENTS.md`,
   or a `loops/` dir in the target.
   - If found, STOP and ask: overwrite, merge (preserve their content, add what's missing),
     or abort. Never overwrite an existing CLAUDE.md silently.
3. Determine **new vs existing codebase**: is the directory essentially empty, or does it
   contain real source? This decides how much Discover relies on code-reading vs interview.

## Phase 1 — Discover

Gather what the templates need to be filled. Three sources: the code, the owner, and any
domain-knowledge dump. If the project has material to absorb (a `knowledge/raw/` folder, or a
body of docs the owner wants ingested), do **1c — Ingest FIRST** — its compiled output sharpens
the interview and grounds Fill/Plan.

### 1a. Read the code (existing projects only)

Detect the stack and shape so you can choose overlays and pre-fill CLAUDE.md. Look for:

- **Language/stack signals:** `package.json`, `pyproject.toml`/`requirements.txt`,
  `Cargo.toml`, `go.mod`, `Gemfile`, `*.csproj`, etc.
- **Web/deploy signals:** a frontend build (`vite`, `next`, `webpack`, a `dist/`/`build/`
  output), a `Procfile`/`Dockerfile`/`vercel.json`/`netlify.toml`, env files.
- **Security signals:** auth code, secret handling, webhook verification, anything that
  brokers credentials or stores user data.
- **Existing docs:** a README, architecture notes, an existing CLAUDE.md to learn voice/facts.
- **Entry points & structure:** how it runs, where the meat is.

For a large/unfamiliar codebase, use the `Explore` agent to map it rather than reading
everything yourself; you only need the conclusions (stack, structure, deploy shape, risk
posture).

### 1b. Interview the owner (always)

Ask only what the code can't tell you. Use a structured question batch (AskUserQuestion) for
the discrete choices, and free-form for the prose. Collect:

- **Project name** + **one-sentence description** (what it is, who it's for).
- **The north-star constraint** — the single lens that resolves most trade-offs
  (e.g. "security is the product", "latency above all", "ship weekly"). This becomes Build
  Session Rule #2 and the top Remember bullet.
- **Current milestone** — what "done enough" means right now (demo, launch, first customer).
- **Owner role & working preferences** — how much to ask vs. default, how they like handoffs.
- **Overlay confirmation** — based on 1a, propose overlays and confirm:
  - `web-saas` if there's a build + deploy pipeline.
  - `security-product` if it handles credentials/customer data or is a security tool.
  - neither for a pure CLI/library/data/script project.
- **Commit enforcement (opt-in)** — ask whether to install the `commit-msg` verification hook
  (`conventions/commit-enforcement.md`). Recommend it for projects that will run sessions
  unattended or where you won't fully trust every session to self-police. Be honest about what
  it is when you ask: a speed-bump that forces a conscious `Verified:` attestation at commit
  time — it does NOT confirm verification actually ran. Default to offering, not forcing.

Keep the interview tight. Infer aggressively from the code; only ask what's genuinely
unknown or a real judgment call.

### 1c. Ingest the knowledge dump (opt-in — only if domain material exists)

Skip this entirely for a greenfield project with no domain material. Run it (and run it FIRST,
before the interview, if the dump is the primary context) when the owner has a body of existing
material to absorb — a client's docs, a complex domain, exports, a prior system. Full convention:
`knowledge/KNOWLEDGE.md`.

1. **Locate the raw material.** Look for `knowledge/raw/` in the target, or ask the owner where
   the dump is / have them drop it there. It can be heterogeneous — PDFs, docs, spreadsheets,
   exports, screenshots, transcripts.
2. **Compile it.** For each source, write a short summary note to `knowledge/compiled/`, then
   build `knowledge/INDEX.md` (every source + a one-line summary + topics → where to look). At
   realistic scale this index + summaries IS the retrieval layer — do NOT reach for a vector
   DB/RAG. For a large dump, summarize-and-index rather than trying to hold it all in context.
3. **Tag provenance/recency and flag conflicts.** Accumulated material has superseded and
   contradictory docs — note what's current vs. uncertain. Don't silently treat old as true.
4. **Privacy is a hard default:** `knowledge/raw/` must be gitignored and never committed
   (PII/business/financial data). Set this up before anything gets staged.

The compiled understanding feeds **Fill** (the CLAUDE.md Domain Context section) and **Plan**
(a roadmap grounded in how the domain actually works).

## Phase 2 — Scaffold

Copy the bundled templates into the target directory. Use `${CLAUDE_SKILL_DIR}/templates/`
as the source so it works from any cwd.

Place files like this (adjust to the project's conventions):

```
<target>/
  CLAUDE.md                         ← from templates/CLAUDE.md
  ISSUES_AND_IMPROVEMENTS.md        ← from templates/tracking/ISSUES_AND_IMPROVEMENTS.template.md
  BUILD_SESSION_PROMPTS.md          ← from templates/tracking/BUILD_SESSION_PROMPTS.template.md
  RESUME_HERE.md                    ← from templates/tracking/RESUME_HERE.template.md
  docs/buildos/
    loops/        ← from templates/loops/   (LOOP_PLAYBOOK + templates + schedules)
    conventions/  ← from templates/conventions/
    overlays/     ← copy ONLY the overlay(s) chosen in Phase 1 (or all, if unsure)
    knowledge/    ← from templates/knowledge/  (KNOWLEDGE.md — the convention doc)
    automation/   ← from templates/automation/  (CATALOG + AUTHORING + recipes; read by Phase 5)
  knowledge/      ← LIVE base, created by Ingest (1c) IF a dump exists: raw/ compiled/ INDEX.md
                    (raw/ gitignored). Omit entirely for a project with no domain material.
```

Notes:
- Strip the `.template` from tracker filenames as you place them.
- Prefer `docs/buildos/` (or the project's existing docs dir) for the loops/conventions/
  overlays reference material, so the repo root stays clean — but adapt to what the project
  already does.
- Do the copying with `cp`/`mkdir -p` via Bash; reference bundled paths as
  `${CLAUDE_SKILL_DIR}/templates/...`.

**If the owner opted into commit enforcement (Phase 1b):** install the hook per
`conventions/commit-enforcement.md` Option A (shareable) — copy `conventions/hooks/commit-msg`
to `.githooks/commit-msg`, `chmod +x` it, run `git config core.hooksPath .githooks`, and stage
it. Then verify it works for real: attempt a commit with no `Verified:` trailer (must be
BLOCKED) and one with it (must be ALLOWED). Tell the owner each contributor must run the
`core.hooksPath` config once locally, and that `--no-verify` is the honest bypass. Only do this
if the target is a git repo; if not, note the hook is staged but inert until `git init`.

## Phase 3 — Fill

Tailor the deployed files to THIS project. This is the core value.

1. **CLAUDE.md** — replace every `<FILL: ...>` with discovered/interviewed content. Remove
   sections that don't apply. Be specific and honest — no aspirational claims about
   capabilities that don't exist.
   - **Domain Context section:** if you ingested a knowledge base (1c), write this from
     `knowledge/INDEX.md` — grounded, cited to the compiled notes, with currency flagged. Point
     to `knowledge/compiled/` for detail beyond a few lines rather than restating it. If there
     is NO knowledge base, delete the Domain Context section.
2. **Merge overlays.** For each chosen overlay, fold its rules into the relevant CLAUDE.md
   sections (e.g. the web-saas deploy rules into a "Deployment Pipeline" section; the
   security table into a "Security Requirements" section) AND keep the overlay file under
   `docs/buildos/overlays/` for reference. Fill the overlay's own `<FILL>` blanks with the
   project's specifics (exact env vars, build dir, deploy host, schema mechanism).
3. **Tracker** — leave the format intact; clear the example BUG-001/IMP-001 stubs unless
   Discover surfaced real items (see Phase 4).
4. **RESUME_HERE.md** — fill the header (repo, entry point, services) and the pre-flight
   checks with the project's actual commands.

## Phase 4 — Plan (seed the first work)

Turn discovery into a starting plan so the project is immediately actionable.

1. **Seed the tracker.** If 1a surfaced obvious gaps, risks, or tech debt, log them as real
   IMP/BUG entries (proper format, honest "what's built vs not"). For a brand-new project,
   leave the tracker empty but ready.
2. **Seed the Build Session map.** In `BUILD_SESSION_PROMPTS.md`, draft the first 1-3 build
   sessions toward the current milestone — each as a real, self-contained prompt following
   the file's checklist. This applies the two-phase model from session one. **If a knowledge
   base exists, ground these in it** — the domain's real workflows, entities, and constraints,
   not a generic template; have the prompts point to the relevant `knowledge/compiled/` notes.
3. **Fill RESUME_HERE "Next steps"** with the concrete immediate action, so a cold session
   (or the owner tomorrow) can pick up.
4. Offer to run a deeper discovery loop if the codebase is large and the owner wants a real
   audit to seed the tracker — but don't force it.

## Phase 5 — Generate (Automation, opt-in)

Propose and scaffold real automation tailored to THIS project, from the catalog at
`${CLAUDE_SKILL_DIR}/templates/automation/` (`CATALOG.md` + `recipes/`). Skip this phase entirely
for a throwaway/exploratory project, or if the owner just wants the discipline scaffolding. The
catalog is **trial-seeded** — only propose what a recipe genuinely fits; do not invent automation
the catalog doesn't contain (that's an `AUTHORING.md` job for after a real trial surfaces the need).

1. **Match.** Read `CATALOG.md` and select the recipes whose "when it applies" fits the project's
   signals (does it use the plan→work model? is there a `knowledge/` base? does it ship external
   deliverables?). Most projects match `control-center` and — if a knowledge base exists —
   `session-capture`.
2. **Entry-Gate each candidate.** Run the recipe's own gate (mechanism named · floor test ·
   earns-its-keep · manual form proven). Drop any that fail. Be honest: a recipe whose manual
   process the owner hasn't run yet is a `candidate`, not something to install today.
3. **Instantiate the survivors** with the project's discovered specifics (prompt file path, tracker
   path, verification command, `knowledge/` paths). A recipe is generic; the instance is
   project-specific. If a recipe is `spec`-status (its implementation isn't built yet), don't
   hand-roll it — surface its build prompt and queue it as the recommended next build session.
4. **Stage manual-first — never auto-schedule on first run.** Install hooks opt-in (ask, like the
   commit-msg hook), and leave any loop/schedule in a *not-yet-active* state with explicit
   graduation criteria ("run it by hand N times, then turn it on"). The Generate phase proposes and
   scaffolds; it does not flip on autonomy the owner hasn't watched succeed.
   - **`session-capture` (built):** if a `knowledge/` base exists and the owner opts in, install per
     `automation/hooks/session-capture/README.md` — copy `session-capture-prompt.md` to the project's
     `.claude/hooks/`, merge the `SessionEnd` block from `settings.snippet.json` into
     `.claude/settings.json` (merge, don't clobber other hooks), and tell the owner the first real
     session-end is the confirmation run (it's a `type: agent` hook, which the docs flag experimental).

Report what you proposed, what you installed, and what you queued (with the build prompt) in
Phase 6.

## Phase 6 — Confirm & summarize

Report back:
- What was created (tree), and where.
- Which overlay(s) were applied and why.
- **If a knowledge base was ingested:** how many sources, what the Domain Context captures, any
  conflicts/stale material flagged — and how to keep feeding it (drop more into `knowledge/raw/`
  to accrue; file session decisions back; re-run a compile to refresh `INDEX.md`). Remind the
  owner `knowledge/raw/` is gitignored and should stay that way.
- **Automation (Phase 5):** what was proposed, what was installed (opt-in hooks), and what was
  queued as a build with its prompt. Be explicit that anything `spec`-status is scaffolded/queued,
  not yet built — "planned ≠ built."
- Anything still needing the owner's input (placeholders you couldn't resolve).
- The recommended first build session to run.
- A one-line reminder that the bundled templates live in the skill; if they evolve the
  standalone `BuildOS` dev copy, re-sync it into `${CLAUDE_SKILL_DIR}/templates/`.

---

## Operating principles while running this skill

- **Tailor, don't dump.** A filled, project-specific CLAUDE.md is the whole point. Leaving
  `<FILL>` markers is a failure.
- **Infer from code first, ask second.** Every question you can answer by reading the repo
  is a question you shouldn't ask.
- **Never clobber.** Existing CLAUDE.md / trackers get merge-or-confirm treatment.
- **Be honest in what you write.** Don't describe capabilities the code doesn't have; mark
  unbuilt things as roadmap. (This is the same overclaim discipline the OS itself enforces.)
- **Keep scope tight.** This skill sets up the OS; it doesn't start building features. End by
  handing off the recommended first build session, not by doing it.
