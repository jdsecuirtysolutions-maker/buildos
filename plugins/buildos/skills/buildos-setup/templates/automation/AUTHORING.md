# Authoring a Recipe

The catalog grows from trials, not speculation. When a real project surfaces a repeated friction
or a "I wish it just did X" moment, that's a recipe candidate. Add it here so the next project
gets it.

## When something earns a recipe

A friction earns a recipe when **all** are true (this is the recipe's own Entry Gate):
- It **repeated** — you hit it more than once, in this project or across projects.
- It has a **clear mechanism** — you can name the harness primitive that solves it (`Workflow`,
  subagents, `/loop`, `schedule`, a hook, a skill). If you can't, it's a candidate, not a recipe.
- It **earns its keep** — what it saves is concrete and worth the build + maintenance.
- The manual version was **proven first** (LOOP_PLAYBOOK manual-first rule). Don't catalog an
  automation whose manual form nobody has run.

If it fails any, log it in `CATALOG.md` as a `candidate` with the observed need — don't design it yet.

## Recipe format

Each recipe is one file in `recipes/<name>.md`:

```
# <name> — one-line purpose

**Tier:** build-time | run-time
**Primitive:** the harness mechanism (Workflow / subagents / /loop / schedule / hook / skill)
**Status:** spec | building | built (ref) | candidate
**Earned by:** which project/trial surfaced the need (+ what it cost manually)

## What it does
<concrete behavior>

## How it's wired (instantiation)
<what the Generate phase emits, and which discovered specifics it needs — test command, paths,
the repeating task. Type alone can't wire it; the recipe is generic, the instance is project-specific.>

## Honest boundaries
<what it does NOT do; any structural limit; the manual-first staging — propose + scaffold, do not
auto-schedule on day one.>

## Build prompt
<a ready-to-run, self-contained build-session prompt (Entry Gate + ceiling + verify steps) so the
implementation is one paste away. Include any tool-behavior that must be VERIFIED before building —
do not bake unverified harness mechanics into the build.>
```

## The status lifecycle

`candidate` (need observed) → `spec` (designed, build-prompt written) → `building` → `built (ref)`
(points at the installed skill/hook/script). Keep `CATALOG.md`'s status column in sync.

## Manual-first, always

A recipe is the *automation* of a proven manual process. The Generate phase **proposes and
scaffolds** automations in a not-yet-scheduled state with graduation criteria; it never
auto-schedules on first run. The trial earns the recipe; the recipe doesn't get to skip the trial.
