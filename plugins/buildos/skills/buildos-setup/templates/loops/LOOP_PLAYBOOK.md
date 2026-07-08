# Loop Playbook

Most people use AI the slowest way: type a request, wait, fix it by hand, ask again —
every step routed through a human. A **loop** removes the human from the inner cycle:
you give a goal and a way to check the result, and the agent keeps working until it's done.

This playbook is the methodology. Runnable scaffolding is in `templates/` and `schedules/`.

---

## What a loop is

A loop is five parts. If you can't name all five, you don't have a loop — you have a wish.

| Part | Question it answers | Example (fix failing tests) |
|------|---------------------|------------------------------|
| **Goal** | What does success look like? | All tests in `suite/` pass. |
| **Do** | What action runs each iteration? | Read the failure, edit the code. |
| **Verify** | How is the result judged — automatically? | Run the test command; read exit code. |
| **State** | What carries between iterations? | Which tests still fail; what was already tried. |
| **Stop** | When does it end (success AND failure)? | All green, OR 8 iterations, OR no progress for 2 rounds. |

A **prompt** is a single instruction you evaluate yourself. A **loop** is a recursive
goal the agent evaluates against the Verify step until the Stop condition fires.

---

## Do you even need one? (the decision test)

Build a loop only if **all four** are true. If any is false, just prompt by hand.

1. **It repeats.** You'll run this shape of task many times, not once.
2. **Bad output can be rejected automatically.** There's a check — a test, a schema, a
   diff, a lint, a numeric threshold — that says pass/fail without you eyeballing it.
3. **The agent can do the work end-to-end.** It has the tools/context to actually finish,
   not just draft something you must complete.
4. **"Done" is objective.** You can state the success condition precisely enough that a
   machine could check it.

If you're tempted to loop something that fails #2 or #4, you'll spend more time refereeing
the loop than the task would have taken by hand.

---

## The sequencing rule (the part people skip)

**Build a reliable manual process → harden it → then automate. In that order.**

1. **Manual.** Do the task by hand, with the agent, several times. Watch where it fails.
2. **Harden.** Tighten the Verify step and the prompt until the manual run succeeds
   consistently. Fix the failure modes you saw.
3. **Automate / schedule.** Only now wrap it in a loop or put it on a schedule.

Never schedule a loop you haven't watched succeed by hand. A scheduled unreliable loop
doesn't save work — it generates a stream of broken output you have to clean up, often
silently, often expensively.

> This mirrors the project-level discipline: *manual-first, verify everything.* A loop is
> just that discipline applied to a repeating task.

---

## The cost nobody mentions

- **Tokens compound.** Each iteration usually carries growing context. A 10-iteration loop
  can cost far more than 10× a single call. Cap iterations.
- **Accept rate is everything.** If the Verify step accepts 1 in 5 attempts, you're paying
  for 5 to get 1. Improve the prompt/verify before scaling the loop, not after.
- **Premature stopping is a real failure mode.** A loop that declares victory before the
  goal is met is worse than no loop — it ships broken work confidently. Make the Verify
  step strict; prefer false negatives (keep going) over false positives (stop too early).
- **Runaway loops.** Always set a hard iteration cap and a "no progress" detector
  (stop if N rounds produce no change toward the goal).

---

## Loop building blocks (for coding agents)

Coding is the ideal loop domain because verification is cheap and objective (compile,
test, lint, type-check). Compose loops from:

- **Automation** — the trigger and the runner (a command, a watch, a schedule).
- **Skill / instruction** — the reusable "how to do this task" the agent follows.
- **Sub-agents** — fan work out (e.g. one agent per file/finding) and gather results.
- **Connectors / tools** — what the agent can actually touch (repo, tests, APIs).
- **Verifier** — the judge. The single most important block. A weak verifier makes every
  other block worthless. Invest here first.

---

## Patterns worth knowing

- **Self-check loop** — generate → critique own output against criteria → revise → repeat
  until criteria met or cap hit. Works in any chat. See `templates/self-check-loop.md`.
- **Build-verify loop** — change code → run the objective check → if fail, read output and
  fix → repeat. The bread-and-butter coding loop. See `templates/build-verify-loop.md`.
- **Loop-until-dry** — for unknown-size discovery (find all bugs/edge cases): keep running
  finders until K consecutive rounds find nothing new. Beats a fixed count.
- **Adversarial verify** — for high-stakes findings, a second agent tries to *refute* each
  result; keep only what survives. Prevents plausible-but-wrong output from shipping.

---

## Anti-patterns (when a loop is a trap)

- **Subjective "done."** "Make the copy better" has no machine-checkable goal — loop will
  oscillate. Define a rubric first, or keep it manual.
- **Looping a one-off.** If you'll do it once, a loop is pure overhead.
- **No automatic verify.** If you must read every output to judge it, the human is still in
  the inner cycle — that's not a loop, it's manual work with extra steps.
- **Scheduling before trust.** Covered above; the most expensive mistake.
- **Chasing loops for their own sake.** Start with what's already free and manual. Only
  build a loop once you genuinely feel the manual way isn't keeping up.

---

## In this OS

- Project rules live in `CLAUDE.md` → "Working in Loops".
- The **build-session model** (`tracking/BUILD_SESSION_PROMPTS.template.md`) is itself a
  human-paced loop: a planning session writes a verified prompt → a build session executes
  and verifies → results feed the next prompt. Treat it as the default loop for feature work.
- Reach for runnable loop scaffolding in `templates/` and `schedules/` only after the
  manual version of that task is proven.
