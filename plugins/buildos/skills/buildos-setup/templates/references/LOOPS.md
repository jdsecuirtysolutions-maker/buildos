# Bounded iteration

Define goal, action, verifier, carried state, and stop conditions before automating repetition.
Prefer an external check to model opinion. Self-critique is not independent verification.

Run the check, diagnose from evidence, make a justified change, and rerun. Track tried approaches.
Reassess after two unsuccessful diagnostic attempts or the task's explicit budget. Do not
silently weaken verification or claim completion at the limit.

Before scheduling, demonstrate repeated manual success, bound cost/side effects, and define
visible failure reporting and a kill switch. BuildOS 0.3 installs no schedules or automatic
session hooks. These conventions are not a runnable scheduler.

Parallel work is optional: require independent tasks, authorized delegation, isolated writes
or ownership, and integration verification. More agents do not guarantee independent errors.
