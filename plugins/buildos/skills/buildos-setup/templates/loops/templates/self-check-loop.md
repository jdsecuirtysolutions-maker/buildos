# Self-Check Loop (works in any LLM chat)

A no-tools loop you can run in any chat interface. The model generates, grades its own
output against explicit criteria, and revises — until the criteria are met or the cap hits.
Use it for writing, planning, analysis — anything where "good" can be turned into a checklist.

> Reminder (from the playbook): this only works if your criteria are concrete enough to
> judge objectively. Vague criteria → the loop oscillates. Write the rubric first.

---

## The prompt template

Paste this, filling the three blanks:

```
GOAL: <what a finished, correct result looks like>

CRITERIA (the result must satisfy ALL; this is the verifier):
1. <concrete, checkable criterion>
2. <concrete, checkable criterion>
3. <concrete, checkable criterion>

STOP CONDITION: all criteria pass, OR you have done 4 revision rounds.

Do this loop, and show your work each round:
1. DRAFT: produce the best result you can.
2. VERIFY: score the draft against each criterion. Mark each PASS or FAIL with a one-line
   reason. Be strict — when unsure, mark FAIL.
3. If all PASS → output the final result and stop.
   If any FAIL → REVISE addressing only the failed criteria, then repeat from VERIFY.
4. If you hit the round cap without all-PASS, output the best version AND a short list of
   which criteria still fail and why.

Begin.
```

## Why each part is there

- **GOAL** anchors the loop so revisions don't drift.
- **CRITERIA** is the verifier. Strength here determines whether the loop is worth anything.
- **STOP CONDITION** prevents infinite/expensive spinning and forces an honest "still failing" report instead of a false "done."
- **"Be strict — when unsure, mark FAIL"** biases toward keep-going over stop-too-early
  (premature stopping is the classic loop failure).

## When to escalate to a real loop

If you find yourself running this same self-check shape repeatedly across sessions, and
the verify step could be a script (a test, a linter, a schema check) instead of the model
judging itself — graduate it to a `build-verify-loop` with an objective external check.
Self-judgment is convenient but weaker than a real verifier.
