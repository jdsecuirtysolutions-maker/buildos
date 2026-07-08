# <FILL: PROJECT> — Build Session Prompts

The two-phase build model. It is a human-paced loop and the default way feature work and
non-trivial fixes get done:

```
   PLAN session                          BUILD session (fresh context)
   ───────────                           ─────────────────────────────
   investigate the real code      →      paste the prompt, execute it
   write a detailed, SELF-         →     run the mandatory verification
   CONTAINED build prompt here            steps, commit, push
        ▲                                         │
        └──────────  results / new findings  ◀────┘
```

**Why split the sessions?** The planning context (full conversation, exploration, dead ends)
is large and noisy. A build session starts clean with only the distilled prompt — cheaper,
more focused, and reproducible. The prompt is the verified interface between the two.

**Loop discipline applies:** the planning session is where you *harden* the task before
automating it. A prompt good enough to hand to a cold session is a task you understand well
enough to trust.

---

## The Entry Gate (front-door check)

BuildOS's verification discipline proves work *works*. The Entry Gate is the other bookend:
it checks the work *should be built* before a session starts. It exists because a structurally
doomed idea can pass every verification check and still have to be killed — the failure was
never something verification could catch, because the floor was wrong at intake.

The gate is **tiered** so it isn't friction theater on small work. Trigger question:
**"Does this introduce a new structural bet, or continue a proven one?"**

- **Continuation** (bug fix, small feature, refactor inside an already-vetted live project):
  one line — *"Continuation of [vetted project]; no new structural bet."* Done. No strategy overhead.
- **New bet** (new project, new product direction, major new feature): state four things —
  - **Mechanism** — the concrete thing that makes this work (the actual approach, not a feature list).
  - **Floor test** — is there a structural reason this *cannot* work? Answer it explicitly; don't reflex "no."
  - **Build-vs-not** — why build this rather than buy, reuse, or ignore it.
  - **Cleared by** — where/when it passed strategic vetting (a strategy doc, planning session, or decision record + date).

If a new-bet prompt can't name the mechanism or fails the floor test, it does not enter build —
it goes back to strategy. **The build machine refuses un-vetted input; it does not do the vetting
itself.** That separation is deliberate: keep strategy and build distinct.

**What the gate does and doesn't do:** it makes *skipping the floor question impossible*; it does
**not** make a *wrong answer* impossible. A lazy "no floor" still clears it. The gate forces a
conscious confrontation, not a correct conclusion — which is the most a front-door check can do.

---

## How to write a build prompt (checklist)

A good build prompt is self-contained — the build session should need nothing but this file
and the repo.

- [ ] **Entry Gate cleared** — continuation one-liner, OR a new-bet gate with mechanism +
      floor test + build-vs-not + cleared-by. A new bet that can't name its mechanism or fails
      the floor test does not get a prompt; it goes back to strategy.
- [ ] **Effort ceiling set** — `<estimate> · hard stop at <Nx>` (default 2x). The point where
      the session stops and re-plans instead of grinding.
- [ ] **Context paragraph** — what's broken/needed and why, in plain language.
- [ ] **"Read X and Y first"** — point at the files/docs to load before changing anything.
- [ ] **Verified facts** — any tool/library/codebase facts the plan depends on, *confirmed*
      (not assumed). Include `file:line` anchors. (Don't bake unverified tool behavior into
      the prompt — verify or hedge it.)
- [ ] **Numbered parts** — each part a coherent chunk of the change.
- [ ] **Explicit non-goals** — what NOT to touch/refactor, so scope stays tight.
- [ ] **Mandatory verification section** — the actual end-to-end flow to run, not "it
      compiles." This is the build session's Stop condition.
- [ ] **Commit message** — pre-written, explaining *why*.
- [ ] **Pre-requisites the human must do first** — in Action Required format, if any
      (secrets, service setup, manual steps). Tell the build session to STOP and ask if a
      prerequisite is missing.

---

## Session Map

Keep this table current so anyone can see what's done, in flight, and queued.

| Session | Focus | Depends on | Status |
|---------|-------|-----------|--------|
| <ID> | <what it builds> | <dep> | Not started / In progress / Complete (commit) |

---

## Prompt: <SESSION ID — TITLE>

See: `ISSUES_AND_IMPROVEMENTS.md` → <BUG/IMP-XXX> for the full diagnosis.

**Why this session / why now:** <one or two lines>

**Effort ceiling:** `<estimate, e.g. 2h> · hard stop at <Nx, default 2x>`

**Pre-requisites (human, before running):** <Action Required steps, or "none">

```
Read CLAUDE.md and <relevant files> before starting.

Entry Gate (clear this BEFORE anything else):
Trigger: "Does this introduce a NEW structural bet, or continue a proven one?"
- CONTINUATION → one line: "Continuation of [vetted project]; no new structural bet."
- NEW bet → state all four:
    • Mechanism — the concrete thing that makes this work (the approach, not a feature list).
    • Floor test — is there a structural reason this CANNOT work? Answer explicitly.
    • Build-vs-not — why build rather than buy, reuse, or ignore.
    • Cleared by — where/when it passed strategic vetting (strategy doc / planning session / decision record + date).
If a NEW-bet gate can't name the mechanism or fails the floor test → STOP. Back to strategy,
not into build. (The gate forces confronting the floor question; it does not make your answer
correct — a lazy "no floor" still clears it. Confront it honestly.)

Effort ceiling: <estimate> · hard stop at <Nx, default 2x>. If actual effort crosses it, STOP —
do not grind through. Log what blew up in ISSUES_AND_IMPROVEMENTS.md and re-plan. An overrun is
evidence the approach or scope may be wrong, not a reason to push harder.

Context: <what and why>

Verified facts (confirmed, with anchors):
- <fact> (<file:line>)

Part 1 — <chunk>:
<precise instructions>

Part 2 — <chunk>:
<precise instructions>

Non-goals (do NOT do these):
- <out-of-scope item>

Verification (run every step; this is the definition of done):
1. <exact command / flow>
2. <expected observable result>

Commit:
"<pre-written message explaining why>"

Notes for the builder:
- <gotcha>
- STOP and ask if <prerequisite> is missing rather than guessing.
```
