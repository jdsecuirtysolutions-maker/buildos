# <FILL: PROJECT> — Resume Here

A cold-start runbook. Written so that you (or a fresh AI session) can pick up after days or
weeks away without re-deriving context. Update it at the end of any session that changes the
project's state.

**Last touched:** <date>
**Resuming after:** <gap / why you stepped away>
**HEAD commit:** <hash + one-line>
**Live URL / entry point:** <where the running thing lives>
**Key services:** <DB / host / auth / etc. with project IDs>

---

## TL;DR — where things stand

<2-4 sentences: what was just done, what's working, what the single next action is.>

---

## Pre-flight (do this before any new work)

Quick checks that the system is in a known-good state. Each with a verification.

1. **<service> is up / not paused.** <how to check> → <expected>
2. **Deploy is on the expected commit.** <how to check> → <expected>
3. **Test account / fixtures intact.** <how to check> → <expected>
4. **Local env staged** (env vars, venv, creds). <commands> → <expected prompt/state>

If any check fails, fix it before proceeding. Don't build on a broken base.

---

## Next steps (in priority order)

### Step 1 — <the immediate next action>

<Concrete, step-by-step, assume-nothing instructions. Include exact commands and the
expected result at each step, plus "if X fails, check Y" troubleshooting. Write it as if
for someone who has never seen this project.>

### Step 2 — <after that>

<...>

### Backlog / strategic (not the immediate path)

| Item | Why it matters | Status |
|------|----------------|--------|
| <FILL> | <FILL> | Open |

---

## Reference

- **Files you'll touch most:** <list with one-line purpose each>
- **Build discipline reminders:** <the project-specific gotchas — env vars, dist rebuild,
  migrations, etc.>
- **How to run locally:** <commands>
- **Open issues that affect this work:** <BUG/IMP IDs + one-line>
- **Known workarounds currently in play:** <anything staged manually that a fix will remove>

---

## When you hit a snag

1. What does the log/observability surface say? (Get the decisive piece of evidence first.)
2. What does the actual response/state show vs. what you expected?
3. Cross-check the source of truth (DB row, config, artifact) against what the code returns.
4. Trace root cause before changing code. One hypothesis, one decisive check, one change.
   (See CLAUDE.md → Debugging Protocol.)
