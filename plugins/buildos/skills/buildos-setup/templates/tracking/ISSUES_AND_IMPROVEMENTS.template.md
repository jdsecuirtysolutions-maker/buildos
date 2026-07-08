# <FILL: PROJECT> — Issues & Improvements Tracker

Captured during build and testing. Items are categorized by type and prioritized relative
to the current milestone (e.g. demo, launch, customer #1).

> Conventions:
> - IDs increment and are never reused: `BUG-001`, `IMP-001`, ...
> - Don't delete entries — annotate their status in the heading.
> - Status markers: `[SHIPPED (commit-hash)]`, `[OBSOLETE (SEE BUG-XXX)]`.
> - Log a defect the moment you discover it — fresh context writes the best entry.
> - For bugs: always distinguish **what's built** from **what isn't**. "Engine exists" is
>   not "feature works."

---

## Improvements

### IMP-001: <Title>

**Priority:** <Critical | High | Medium | Low> (+ "post-<milestone>" if deferred)
**Category:** <area>

**Current state:** <what exists today>

**What needs to happen:** <the change, concretely>

**Why it matters:** <impact; what breaks or stays clunky without it>

**Approximate effort:** <rough estimate + the chunks>

---

## Bugs

### BUG-001: <Title>

**Priority:** <Critical | High | Medium | Low>
**Category:** <area>
**Discovered:** <date + how — which test/flow surfaced it>

**Steps to reproduce:**
1. <step>
2. <step>
3. <observed failure, with exact error text/log line>

**Root cause:** <the actual mechanism, traced — not "seems like">

**What works (do not rebuild):** <the parts that are correct, so the fix stays surgical>

**What does NOT work:** <the precise broken piece>

**Required fix:** <the change, with file:line pointers where known>

**Workaround (if any):** <interim unblock, clearly marked as not the real fix>

**Demo/milestone impact:** <does this block the current milestone? be specific>

**Approximate effort:** <estimate>

---

## Issue Log

| ID | Type | Summary | Priority | Status |
|----|------|---------|----------|--------|
| IMP-001 | Improvement | <summary> | <pri> | Open |
| BUG-001 | Bug | <summary> | <pri> | Open |
