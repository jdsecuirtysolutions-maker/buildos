# Knowledge Base — the project's domain context

The knowledge base is how the agent becomes *fluent in this project's domain* instead of
building generically. You feed it material; the agent compiles that into a navigable, queryable
set of notes; and the rest of BuildOS (the tailored CLAUDE.md, the roadmap, build sessions)
draws on it. It is an **input** the whole system reads — not a place you hand-maintain.

> Opt-in. A greenfield project with no existing domain material doesn't need one. A project
> where you're absorbing someone's accumulated context (a client's 15 years of docs, a complex
> domain, a prior system) is exactly where it earns its place.

---

## Structure (created per project)

```
<project>/knowledge/
  raw/          # what YOU feed in — dumps, docs, exports, screenshots, transcripts, post-mortems
  compiled/     # what the AGENT writes — one short summary note per source
  INDEX.md      # the map — every source + a one-line summary + topics → where to look
```

`raw/` is **gitignored by default** (see "Privacy" below). `compiled/` and `INDEX.md` are the
agent-maintained layer — you rarely touch them directly.

## Three ways to feed it (mix freely)

1. **Dump** — drop a body of existing material at once (e.g. a client's documentation). One-time
   or periodic. This is the most common starting mode for a domain-heavy project.
2. **Accrue** — knowledge builds up as the project runs: resolved issues, decisions, post-mortems,
   discovered conventions get filed into `raw/` over time.
3. **Live feedback** — outputs and decisions from build sessions file back in, so the next session
   starts smarter.

Most real projects are a **hybrid**: an initial dump, then accrual + live feedback on top.

## How the agent uses it

- **Ingest (at setup):** the agent reads each source in `raw/`, writes a summary per source to
  `compiled/`, and builds `INDEX.md`. That compiled understanding then feeds the tailored
  **CLAUDE.md** (a *Domain Context* section) and the **roadmap** (grounded in how the domain
  actually works, not a generic template).
- **Query (during build):** sessions consult `INDEX.md` and pull only the relevant compiled notes
  — they don't re-read everything. At realistic scale this beats fancy retrieval (an index +
  good summaries is enough; see "Scale").
- **File back:** new decisions/learnings get written into `raw/` (or `raw/sessions/`), and a
  periodic re-compile keeps `INDEX.md` current. This is what makes explorations "add up."

## Defaults & boundaries (do not skip these)

- **Privacy — `raw/` is gitignored and never committed by default.** Client/business data,
  PII, and financials must not end up in version control. Be deliberate about what you dump;
  redact where appropriate. For a security-sensitive project this is non-negotiable.
- **Scale — index-and-retrieve, not read-everything.** Large dumps don't fit in one context.
  The `INDEX.md` + per-source summaries are the mechanism; pull relevant notes on demand. Do
  NOT reach for a vector DB / RAG until a project genuinely outgrows markdown — most never do.
- **Freshness — flag stale and contradictory material on compile.** Years of accumulated docs
  contain superseded processes and conflicts. Tag provenance/recency; never silently treat an
  old doc as current. This is the verification ethos applied to knowledge: don't trust, verify.
- **You supply the goal; the knowledge supplies the context.** Ingest informs *how* to build;
  the interview still captures *what* to build.

## What "good" looks like

A build session can ask "how does X work in this domain?" and the agent answers from the
compiled knowledge in seconds — correctly, with provenance — instead of guessing or
re-reading raw files. The CLAUDE.md's Domain Context section reads like it was written by
someone who knows the business. New learnings reliably land back in the base.
