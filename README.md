# BuildOS

**A lightweight operating system for working with AI coding agents** — project discipline,
reusable context, and repeatable build sessions.

> **Status: early public release.** The core workflow and templates are usable today. The knowledge
> layer is tested; the automation/orchestration pieces are newer and partly experimental.
> **Try it in a test repo first.**

The promise of AI was to *offload* work. The reality, for a lot of us, is *babysitting* it —
impressive-looking output that doesn't actually work, or hours of fine-tuning to get it right.

BuildOS is what fixed that for me: the rules, scaffolding, and automation I extracted after using an
AI coding agent to ship a real product — the difference between "a demo that passes once" and "a
thing that actually works." The core idea: **the bottleneck isn't the model, it's context and
process.** BuildOS engineers both.

Built for **Claude Code (CLI)**.

---

## The three layers

Each is optional on top of the last.

1. **Discipline** — the core. Scoped, two-phase build sessions; an effort ceiling (stop and re-plan
   instead of grinding); an Entry Gate (*should this even be built?* before code); a verify-the-real-
   -thing loop; a BUG/IMP tracker. Works for any project, alone.
2. **Knowledge** — an *input*. Drop a domain's material into `knowledge/`; BuildOS compiles it into a
   cited index so the AI reasons with *your* context instead of generic priors. Index-and-retrieve by
   default — no heavyweight vector DB or RAG layer required.
3. **Automation** — an *output*. A trial-seeded catalog of real automations the setup proposes and
   wires for your project (a session-capture hook, an orchestrator, …). Manual-first: nothing gets
   automated until its manual form is proven.

## Who this is for

- Solo builders using Claude Code
- Non-traditional developers building with AI
- Technical founders who need better continuity between sessions
- Teams experimenting with AI-assisted development workflows

## What this is *not*

- Not a replacement for engineering judgment
- Not a full agent framework
- Not a security sandbox
- Not production governance for enterprise teams — yet

## Honest status

BuildOS is used, not theoretical — but it's early and not finished, and pretending otherwise would
betray the whole point ("planned ≠ built"). It's the working method of one builder, published so
others can use and pressure-test it — not a validated framework with a track record behind it yet.

| Layer | State |
|-------|-------|
| Discipline | **Built** — used to ship a real product end-to-end |
| Knowledge | **Built & tested** (incl. on a non-software project — analyzing a real building) |
| Automation → session-capture hook | **Built.** Distillation logic verified against a real transcript. `SessionEnd` `type: agent` hooks are experimental; first live run confirms the plumbing. |
| Automation → Control Center (orchestrator) | **Specced**, built against the next real project (a dispatcher needs sessions to dispatch) |

## Install (Claude Code CLI)

```
/plugin marketplace add jdsecuirtysolutions-maker/buildos
/plugin install buildos@buildos
```

Then, in any project directory:

```
/buildos:buildos-setup
```

It detects your stack, interviews for what code can't tell it, ingests any domain knowledge you
drop in, fills a tailored `CLAUDE.md` + tracker, and proposes automation that fits the project.

> **Heads-up — this is developer tooling, not a passive markdown guide.** `buildos-setup` declares
> and uses `Bash, Read, Write, Edit, Grep, Glob`: it runs shell commands and reads/writes files in
> your project to scaffold `CLAUDE.md`, the tracker, and hooks. Skim what it does and **run it in a
> throwaway/test repo first.** See [SECURITY.md](SECURITY.md).

## Or just borrow the methodology

Not on Claude Code? The whole system is readable markdown under
[`plugins/buildos/skills/buildos-setup/templates/`](plugins/buildos/skills/buildos-setup/templates/) —
the core rules (`CLAUDE.md`), the loop playbook, the two-phase build model, the knowledge convention,
and the automation catalog. Copy what's useful.

## Why "operating system"

Because it's the layer *between* you and the model that decides what the model can see and do at any
moment — its context, its constraints, its verification. That's context engineering, and right now
it's the whole game.

## Security

BuildOS installs developer tooling that executes shell commands and writes files in your project.
Review before running, prefer a test repo, and see [SECURITY.md](SECURITY.md) for scope and how to
report an issue.

## License

MIT — see [LICENSE](LICENSE).
