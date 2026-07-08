# session-capture hook (built)

A `SessionEnd` hook that distills each work session into a 5–8 line note in `knowledge/sessions/`,
feeding the knowledge base's "live feedback" loop automatically. Built for **Claude Code CLI**.

## Files

- `settings.snippet.json` — the `SessionEnd` hook block to merge into a project's
  `.claude/settings.json`. Uses `type: agent` (a subagent with Write access — the only native hook
  type that can produce a file).
- `session-capture-prompt.md` — the detailed capture instruction the agent follows. Installed into
  the project at `.claude/hooks/session-capture-prompt.md`. Edit *this* to tune capture behavior;
  the settings snippet just points at it.

## Install (opt-in, per project)

The `buildos-setup` Generate phase installs this when the owner opts in. Manually:

1. Copy `session-capture-prompt.md` → `<project>/.claude/hooks/session-capture-prompt.md`.
2. Merge `settings.snippet.json`'s `hooks.SessionEnd` block into `<project>/.claude/settings.json`
   (create the file if absent; merge, don't clobber other hooks).
3. Ensure `<project>/knowledge/sessions/` will exist (the hook creates it on first write).

Because it lives in the project's `.claude/settings.json`, it's opt-in and scoped to that project.

## Verify on first real run (do this on the next project)

End a real session and confirm a correctly-shaped note appears in `knowledge/sessions/<date>.md`
capturing the actual decisions and ignoring the noise. Then start a second session the same day and
confirm it **appends** (after a `---`) rather than overwriting.

## Honest caveats

- **`type: agent` hooks are experimental** per the Claude Code docs — the config/behavior may change.
  If a future CLI version breaks it, the fallback is a `type: command` hook that pipes
  `transcript_path` into `claude -p` and writes the result — but that needs a re-entrancy guard
  (an env flag so the spawned `claude` doesn't re-fire this same SessionEnd hook in a loop). Prefer
  the agent hook until it breaks.
- **Placeholder substitution** (`${cwd}`, `${transcript_path}`) for agent-hook prompts is the one
  bit not yet confirmed against a live run; the prompt is written to degrade gracefully (it tells
  the agent to locate the latest transcript if the value isn't supplied). First real run confirms it.
- **Privacy:** session notes are committed by default (they're the durable knowledge feed). For a
  sensitive project, gitignore `knowledge/sessions/` too — same call as `knowledge/raw/`.
- **Cost:** the agent runs once per session end. Trivial sessions produce no note but still spawn the
  agent. Acceptable for v1; scope the matcher later if it's noisy.
