# Build-Verify Loop (coding agent)

The bread-and-butter coding loop: make a change, run an **objective external check**, and
if it fails, read the output and fix — repeat until green or capped. This is the strongest
kind of loop because the verifier is a real command, not the model's own opinion.

> Sequencing rule still applies: run this by hand a few times on real tasks before you
> wrap it in any automation or schedule.

---

## Define the five parts before you start

```
GOAL:    <the objective end state, e.g. "`<test command>` exits 0 with no skips">
DO:      <the change action, e.g. "implement <feature> / fix the failing case">
VERIFY:  <the exact command whose exit code / output is the judge, e.g. `npm test`,
          `pytest -q`, `cargo build`, `tsc --noEmit`, a curl + status-code check>
STATE:   <what to carry: remaining failures, approaches already tried, files touched>
STOP:    success = VERIFY passes; failure = N iterations reached OR no progress for 2 rounds
         OR effort ceiling crossed (see below)
```

## The agent instruction

```
Loop until the GOAL is met. Each iteration:

1. RUN the VERIFY command. Capture its full output.
2. If it passes the GOAL → stop and report what changed.
3. If it fails → read the output, form ONE hypothesis about the single most likely cause,
   make the smallest change that tests that hypothesis (no shotgun edits), and note it in STATE.
4. Re-run VERIFY. Never assume a fix worked — confirm with the command.
5. Track progress. If 2 consecutive iterations make no progress toward the GOAL, STOP and
   report: what you tried, why you think it's stuck, and what you'd need to proceed.

Hard cap: <N> iterations. On cap, STOP and report remaining failures honestly — do NOT
declare success unless VERIFY actually passes.

Constraints:
- Change one thing at a time, with a stated reason (debugging discipline).
- Don't weaken the VERIFY check to make it pass. Fix the code, not the test, unless the
  test is provably wrong — and say so explicitly if it is.
- Match the surrounding code's style.
```

## Guardrails baked in (and why)

| Guardrail | Failure mode it prevents |
|-----------|--------------------------|
| Hard iteration cap | Runaway token spend |
| "No progress for 2 rounds → stop" | Thrashing on an unsolvable approach |
| "Confirm with the command, never assume" | False "done" / premature stop |
| "One change at a time, with a reason" | Shotgun debugging hiding the real cause |
| "Don't weaken VERIFY to pass" | Loop gaming its own success metric |
| "Report remaining failures honestly on cap" | Confidently shipping broken work |
| "Stop at the effort ceiling, log, re-plan" | Grinding a wrong approach past the point an overrun should have triggered a reassessment |

## Scaling it (only once the single loop is reliable)

- **Fan-out:** one sub-agent per file/finding/module, each running its own build-verify
  loop, results gathered at the end. Good for migrations and broad sweeps.
- **Adversarial verify:** after the loop reports success, a second agent tries to break the
  result (edge cases, security, "does it actually reproduce"). Keep only what survives.
- **Loop-until-dry:** for "find and fix all X," keep spawning finder loops until K rounds
  surface nothing new, rather than guessing a fixed count.
