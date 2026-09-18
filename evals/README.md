# Evaluating BuildOS outcomes

Deterministic tests validate helper behavior. They do not show that BuildOS improves model
performance. This protocol compares ordinary instructions, the compact contract, and the full
workflow. No comparative model results are claimed in this release.

## Controlled trials

Use at least five independent runs per case/variant on the same pinned model, effort, tool
permissions, and starting repository revision. Randomize order. Start fresh conversations and
fresh fixture copies; do not let later trials see prior solutions. Record versions, elapsed
time, token usage (null if unavailable), human interventions, raw evidence location, and outcome.
Never run trials in a real customer project. Authorize any model charges separately when needed.

Variants:
- `ordinary`: fixture plus its user request; no BuildOS files.
- `compact`: same inputs plus the short AGENTS.md contract; no installed workflow skills.
- `full`: same inputs plus a standard BuildOS installation and its task/knowledge workflow.

Cases in cases.json include their fixture, request, and observable acceptance criteria. For the
code case, run acceptance.py independently after the agent finishes and inspect whether tests
were weakened. For the knowledge case, a reviewer checks source fidelity, conflict treatment,
and resistance to embedded instructions. For stale-resume, inspect the actual resulting code
and plan handling. Do not use another model's agreement as the sole judge.

Put one JSON object per trial in a private JSONL results file:

```json
{"case":"tenant-boundary","variant":"full","trial":1,"model":"exact-model-version","revision":"fixture-revision","success":true,"false_completion":false,"regressions":0,"human_interventions":0,"seconds":120,"tokens":null,"evidence":"private-run-directory"}
```

Run `python3 evals/report.py /path/to/results.jsonl` to aggregate. Missing cases/variants/trials
are reported as incomplete, not filled with synthetic successes. Compare success and false
completion first, then cost, latency, and interventions. Report uncertainty and failures; tiny
samples are exploratory, not statistically conclusive. Retain redacted public reports and keep
raw transcripts private. Adoption feedback should drive the next rule, not hypothetical failures.
