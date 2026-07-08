# control-center — orchestrator that dispatches work sessions instead of you copy/pasting

**Tier:** build-time
**Primitive:** a skill, driving `Workflow` + subagents (the Agent tool)
**Status:** spec (build-prompt below; implementation queued as the next focused build)
**Earned by:** a live real-estate analysis project. The two-phase plan→work model worked, but every handoff
was a human round-trip: open a fresh session, paste the prompt, run it, copy the result back, tell
the planner, wait for it to write the next prompt. Three *independent* owner-actions (broker BOV /
CPA tax read / attorney cure-scope) were serialized across turns because there was no fan-out at the
handoff layer. In-session compute *was* already parallelized via subagents — the gap is specifically
the **cross-session handoff**.

## What it does

A persistent orchestrator session (the "Control Center") that the owner keeps open. It reads the
project's `BUILD_SESSION_PROMPTS.md` + tracker and can:

1. **Dispatch** — take a ready work-session prompt and run it as a real subagent/`Workflow` run
   (isolated context, like a fresh session), then file the result back into the tracker /
   `knowledge/` itself. Kills the copy/paste round-trip.
2. **Fan out** — when N work-items are independent (no data dependency, different
   recipients/owners), run them in one parallel batch instead of serializing across turns. Maps
   directly onto `Workflow`'s `parallel`/`pipeline`.
3. **Advance (internal only)** — each turn, propose the next action by default ("if you don't
   steer otherwise, I'll draft the remaining two handoffs"). Keep the tracker statuses current.
   The owner steers or confirms; the orchestrator never stalls waiting to be asked "what's next."

## How it's wired (instantiation)

The Generate phase emits a project-scoped `control-center` skill that knows:
- where the prompts live (`BUILD_SESSION_PROMPTS.md`) and the tracker path,
- the project's verification command(s) (so a dispatched build self-verifies),
- the `knowledge/` paths to file results back into.

Dispatch a single prompt → one subagent run. Fan-out → a `Workflow` over the independent items.
The orchestrator presents results + the proposed next action; it does not auto-commit or
auto-send anything outward.

## Honest boundaries

- **External state is not observable.** The orchestrator advances *internal* work (analysis,
  drafts, code). It cannot know a broker replied or a filing cleared — surface "waiting on <who>"
  and let the human feed that update. Do not fake a world-state feed (see
  `CATALOG.md` → external-state-intake, a separate bounded candidate).
- **Manual-first.** The dispatched task must have been run manually at least once (it has — the
  trial + a full security-product build). The orchestrator templatizes a proven handoff; it doesn't invent new
  unproven autonomy.
- **Human stays in the loop.** Fan-out drafts are *staged for the owner's review/send*, not sent.
  The Control Center is a force-multiplier on the owner's judgment, not a replacement for it.

## Build prompt

> **Entry Gate (continuation):** mechanism = a project-scoped orchestrator skill driving `Workflow`
> + subagents; floor test — dispatch/fan-out sit directly on `Workflow`/Agent primitives, the only
> hard limit (external state) is named and bounded; cleared by the the real-estate trial.
> **Effort ceiling: 3–4h.** If the dispatch/result-pipe-back design balloons past it, STOP and
> re-plan — don't grind toward a Rube-Goldberg orchestrator.
>
> **Verify before building (do not skip):**
> 1. Confirm the `Workflow` tool's actual semantics for this use: an orchestrating session spawning
>    subagents whose results return to it, and `parallel`/`pipeline` for fan-out. Confirm a subagent
>    can run a self-contained build/work prompt and return structured output.
> 2. Confirm whether the orchestrator is best as (a) a skill the owner invokes
>    (`/control-center`) that internally calls `Workflow`, or (b) a `Workflow` script template the
>    skill writes and runs. Pick based on what keeps the owner in the loop turn-by-turn.
>
> **Build:**
> - A `control-center` skill scaffolded by the Generate phase, parameterized with the project's
>   prompt file, tracker path, verification command, and `knowledge/` paths.
> - Dispatch one prompt → one subagent run → file result back + update tracker status.
> - Fan-out → run independent items via `Workflow` parallel; present a combined result + the
>   proposed next action.
> - The "default next action" advance policy (propose each turn; never stall).
>
> **Verify (actual flow, not "it compiles"):** dispatch a real WS prompt from a test project and
> confirm the result lands in the tracker without a copy/paste; fan out two genuinely-independent
> items and confirm they run concurrently; confirm an external-dependent task is surfaced as
> "waiting on <who>", not faked.
