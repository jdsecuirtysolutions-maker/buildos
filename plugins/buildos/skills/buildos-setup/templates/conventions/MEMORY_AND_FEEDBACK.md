# Memory & Feedback Conventions

How durable knowledge is captured so it survives across sessions and improves the working
relationship over time. Two layers: **project docs** (in the repo) and **persistent memory**
(the AI's cross-session memory, if available).

---

## What goes where

| Knowledge | Home | Why |
|-----------|------|-----|
| How the project works, rules, architecture | `CLAUDE.md` + repo docs | Versioned with the code; everyone sees it |
| Open work, bugs, improvements | `ISSUES_AND_IMPROVEMENTS.md` | Single source of truth for state |
| How to resume cold | `RESUME_HERE.md` | Cross-session continuity |
| Durable facts about the *owner* and *how to work with them* | Persistent memory | Applies across all projects, not just this repo |

Don't duplicate repo facts into persistent memory — if the code or CLAUDE.md already says
it, memory adds noise. Persistent memory is for what *isn't* derivable from the repo.

---

## Persistent memory — what's worth saving

Save only durable, reusable signal. Four kinds:

- **user** — who the owner is: role, expertise, preferences, how they like to receive work.
- **feedback** — guidance they've given on how to work (corrections AND confirmed-good
  approaches). Always include **why** and **how to apply**, or it's not actionable later.
- **project** — ongoing goals/constraints not derivable from the code or git history.
  Convert relative dates to absolute.
- **reference** — pointers to external resources (dashboards, tickets, docs).

### Format for a feedback memory

```
TITLE: <short, searchable>
WHAT: <the guidance, stated as a rule>
WHY:  <the reason it matters — the principle behind it>
HOW TO APPLY: <what to actually do differently next time, concretely>
```

A feedback note without WHY and HOW decays into a vague preference nobody can act on.

---

## When to capture feedback

- The owner **corrects** an approach → save it (so the correction sticks).
- The owner **confirms** a judgment call was right → save it (so you keep doing it).
- The owner reveals a **working preference** (how they want options presented, how much to
  ask vs. default, format of handoffs) → save it.

Don't save one-off task details, anything the repo already records, or transient state.
If asked to "remember" something already in the code/history, ask what was *non-obvious*
about it and save *that* instead.

---

## Hygiene

- **Before saving, check for an existing note** on the same topic and update it rather than
  duplicating.
- **Delete memories that turn out wrong.** A stale memory is worse than none.
- **Treat recalled memories as point-in-time.** If a memory names a file/flag/function,
  verify it still exists before relying on it — code moves, memories don't.
- **One fact per memory.** Easier to recall, update, and retire.

---

## Verified-assertion discipline (a standing feedback rule)

When stating a load-bearing claim about how a tool, library, or platform behaves — one that
a plan or fix will depend on — either **verify it** (read the source, test it, check docs)
or **hedge it explicitly** ("I believe X; confirm before depending on it"). Confident-but-
wrong claims about niche behavior are expensive: they get built on before anyone checks.
This belongs in persistent feedback memory because it applies to every project.
