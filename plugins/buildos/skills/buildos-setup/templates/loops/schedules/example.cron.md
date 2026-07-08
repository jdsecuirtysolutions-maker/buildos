# Scheduled Loop — Stub

A scheduled loop runs a proven task on a recurring cadence with no human in the inner
cycle. **Only create one after the task's manual and build-verify versions are reliable**
(playbook sequencing rule). A scheduled unreliable loop is the most expensive mistake in
this whole system — it silently produces broken output on a timer.

---

## Pre-flight checklist (all must be true before scheduling)

- [ ] The task has run **manually** to success multiple times.
- [ ] The **Verify** step is an objective, automatic check (not human eyeballing).
- [ ] There is a **hard iteration cap** and a **no-progress stop**.
- [ ] Failures are **visible** — the loop reports somewhere you'll actually see it, not
      into a void.
- [ ] The **blast radius is bounded** — a bad run can't corrupt prod data, spam people,
      or spend unbounded tokens/money.
- [ ] You've estimated the **token/cost per run × runs per period** and accepted it.

If any box is unchecked, keep it manual.

---

## Stub (fill in, then wire to your scheduler of choice)

```
NAME:        <short-name>
CADENCE:     <e.g. every 30 min / daily 09:00 / on push to main>
GOAL:        <objective end state for one run>
DO:          <the task>
VERIFY:      <the automatic pass/fail check>
STATE:       <what persists between runs, and where it's stored>
STOP (per run): success = VERIFY passes; failure = <cap> iterations or no progress
ON FAILURE:  <where the alert/report goes so a human notices>
COST BUDGET: <max tokens/$ per run; abort if exceeded>
KILL SWITCH: <how to disable it fast if it misbehaves>
```

## Picking a cadence

- Match the cadence to **how fast the watched state actually changes**, not a round number.
  Polling something every 5 minutes that changes daily just burns money.
- For "watch an external job" loops, pick a delay matched to that job's real duration.
- Prefer being **event-triggered** over time-polling when the platform supports it.

## Notes

- Start with the **longest** safe cadence and shorten only if you're genuinely missing
  events. Over-frequent scheduling is the common waste.
- Revisit scheduled loops periodically — tasks that were worth automating can become
  obsolete; a loop quietly running against a dead goal is pure cost.
