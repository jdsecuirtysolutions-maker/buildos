# session-capture — file each session's learnings into knowledge/ at session end

**Tier:** build-time (the knowledge flywheel — automates the Knowledge layer's "live feedback" mode)
**Primitive:** a `SessionEnd` `type: agent` hook (project-scoped, opt-in via `.claude/settings.json`)
**Status:** **built** → `automation/hooks/session-capture/` (settings snippet + capture prompt +
README). Distillation logic verified 2026-07-08 against a real transcript (all key
decisions/corrections/facts captured, correctly shaped). `type: agent` chosen because `type: prompt`
cannot write files. First real session-end on the next project confirms the firing/placeholder
plumbing (agent hooks are experimental).
**Earned by:** the the real-estate trial. Its own `※ recap:` lines, source-stamped facts, and "where that
leaves us" wrap-ups were the most carried-forward artifacts — but writing them was manual and
easily forgotten. The conflicts/corrections (the $52K owner-loan repayment vs. "profit"; DHCR
"in progress, not cleanly cured") are exactly what a base must not lose between sessions.

## Verified hook mechanics (Claude Code, as of 2026-06-30)

- **Event: `SessionEnd`** fires exactly once when a session exits (not per turn — that's `Stop`).
  Right granularity for end-of-session capture.
- **It CANNOT block or enforce.** SessionEnd ignores exit codes; the session terminates regardless.
  → The earlier "enforce a note like the commit-msg hook" idea is **wrong** and abandoned. This hook
  *produces* the note; it can't *gate* on one.
- **It receives the transcript.** Hook input (JSON on stdin) includes `transcript_path` (a JSONL
  file), `session_id`, `cwd`, `reason`. So the capture step can read what actually happened.
- **Intelligent capture is native.** Hook `type` can be `command` (deterministic shell — too dumb
  for semantic capture), or **`prompt`/`agent` (a managed LLM step)** — the right tool for turning a
  transcript into a 5–8 line note. Shelling out to `claude -p` is possible but **not recommended**
  (re-entrancy, cost, blocks cleanup).
- **Opt-in & scoped** by living in the project's `.claude/settings.json` (committable). Global hooks
  go in `~/.claude/settings.json`. `"disableAllHooks": true` is the kill switch.

## What it does

On session end, an LLM hook step reads the transcript and appends a short note to
`knowledge/sessions/<date>.md`, which the next `compile` folds into the base. It captures the
signal and ignores the noise.

**Capture:** decisions (+ rationale) · conflicts/corrections (flag them *as* corrections) ·
facts verified against a source (with the source stamp) · open questions / what's waiting on whom.
**Ignore:** shell/render retries, tool wrangling, restated analysis prose, anything already in a
committed artifact.

## The note shape (model: the trial's own recaps)

~5–8 lines:

```
## <date> — <session label>
**Goal:** <one line — the decision/output this session served>
**Changed/decided:**
- <bullet — with source or rationale; if it overturns a prior belief, mark "CORRECTION:">
- <2–4 bullets max>
**Open / waiting:** <item — blocked on whom>
**Next action:** <the single next concrete step>
```

Any carried number gets the atomic-fact stamp (also from the trial):
`> As-of: <date>. Basis: <what data>. Source: <doc>.`

## Honest boundaries

- Produces, never enforces (verified above). If a session ends mid-thought, the note reflects that.
- LLM capture can mis-summarize — keep notes short, source-stamped, and reviewable; the owner can
  correct in `knowledge/raw/` or the next session (which the *next* capture will record).
- Selective by design. A transcript dump is not a capture; the value is the 5–8 line distillation.

## Build prompt

> **Entry Gate (continuation):** mechanism = `SessionEnd` LLM hook → `knowledge/sessions/`; floor
> test — verified the event exists, fires once, and receives `transcript_path`; the only open item
> is the LLM-step's file I/O. Cleared by the the real-estate trial (manual recaps proved their worth).
> **Effort ceiling: 2–3h.** Small, self-contained.
>
> **Verify before building (the one remaining unknown):**
> 1. Confirm exactly how a `SessionEnd` hook of `type: agent` (or `type: prompt`) is configured and
>    **whether/how its LLM step can write a file** to `knowledge/sessions/` (does it get tool
>    access / Write, or must its stdout be redirected by a wrapping `command` hook?). Decide between:
>    (a) `type: agent` with Write access, or (b) a `type: command` wrapper that pipes the transcript
>    into a `prompt` step and writes the returned markdown itself. Do NOT bake either in until
>    confirmed — this is the load-bearing mechanic.
>
> **Build:**
> - The `SessionEnd` hook block for `.claude/settings.json` (opt-in, project-scoped).
> - The capture instruction (the "capture vs. ignore" rules + the note shape above) as the LLM
>   step's prompt.
> - Append to `knowledge/sessions/<date>.md`; create the dir if absent; never overwrite a prior
>   day's note (append with a divider).
> - Wire the Generate phase to install it opt-in (ask first, like the commit-msg hook) and to make
>   the next `compile` read `knowledge/sessions/`.
>
> **Verify (actual flow):** run a real throwaway session in a test project, end it, and confirm a
> correctly-shaped note appears in `knowledge/sessions/` capturing the real decisions and ignoring
> the noise. Confirm a second session the same day appends rather than clobbers. Confirm the hook is
> inert in projects that didn't opt in.
