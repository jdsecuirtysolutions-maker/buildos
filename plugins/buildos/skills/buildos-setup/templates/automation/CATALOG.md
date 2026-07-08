# Automation Catalog

The automation layer **proposes, builds, and wires** real automation (skills / loops / workflows /
schedules / hooks) tailored to a project, so the work goes faster. This catalog is the menu the
`Generate` phase of `buildos-setup` reads: it matches recipes to a project's signals, runs each
through the Entry Gate, and instantiates the survivors.

> **Trial-seeded, not speculative.** Every recipe here was earned by a real project surfacing the
> need — it is not a guessed-at wishlist. The catalog starts small and grows from trials
> (see `AUTHORING.md`). A recipe that no project has actually needed does not belong here yet.

## How to read a recipe row

- **Tier** — *build-time* (speeds building the project) vs *run-time* (part of the deliverable).
  Build-time is lower-risk and where the early wins are.
- **Primitive** — the real harness mechanism it's built on (`Workflow`, subagents, `/loop`,
  `schedule`, a hook, a skill).
- **Status** — `spec` (designed, not built) · `building` · `built (ref)` · `candidate` (need
  observed, not yet designed).

## The catalog

| Recipe | What it does | When it applies | Tier | Primitive | Status |
|--------|--------------|-----------------|------|-----------|--------|
| **control-center** | Orchestrator skill: dispatch a work-session prompt as a real run (no copy/paste), fan out independent items in parallel, advance *internal* tasks via a "default next action" policy | Any project using the two-phase plan→work model — i.e. all of them | build-time | `Workflow` + subagents (a skill) | spec → see `recipes/control-center.md` |
| **session-capture** | SessionEnd hook: write a ~5–8 line capture note (decisions/conflicts/verified-facts/open-questions, source-stamped) into `knowledge/` so the base compounds | Any project with a `knowledge/` base | build-time | SessionEnd `type: agent` hook | **built** → `hooks/session-capture/` |
| format-by-audience | Pick deliverable format from the recipient (broker → PDF/OM; family/email → paste-able md) | Projects that produce external deliverables | build-time | skill/convention | candidate |
| html-pdf-helper | Hardened HTML→PDF step (the trial lost turns to Chrome-headless/timeout fragility) | Projects that render PDFs | build-time | skill/script | candidate |
| external-state-intake | Advance tasks from real-world events (broker replied, filing confirmed) without manual prodding | Projects with external-world dependencies | run-time | inbox/event hook + integration | candidate (bounded — see note) |
| dependency-ready-signal | Flag a skeleton prompt as "ready to fill" once its dependency (e.g. prior session's numbers) has landed | Multi-session projects with chained prompts | build-time | tracker convention + check | candidate |

## Honest boundary on `external-state-intake`

The orchestrator can advance *internal* work (analysis, drafts) autonomously, but it cannot know
that a broker replied or a filing cleared — that state lives in the world, not the repo. Advancing
those tasks needs human input or a real integration (email/calendar). Do not design automation that
pretends to know external state; surface "waiting on <who>" and let the human feed the update.
