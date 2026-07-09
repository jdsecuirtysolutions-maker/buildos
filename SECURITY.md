# Security

## What BuildOS is (and what it runs)

BuildOS is **developer tooling**, not a passive markdown guide. Its `buildos-setup` skill declares
and uses `Bash, Read, Write, Edit, Grep, Glob` — it runs shell commands and reads/writes files in
whatever project directory you point it at, to scaffold `CLAUDE.md`, the tracker, loops, and hooks.

Treat it accordingly:

- **Review before you run it.** The skill and every template it installs are plain, readable files
  under [`plugins/buildos/skills/buildos-setup/`](plugins/buildos/skills/buildos-setup/).
- **Run it in a throwaway or test repo first**, then use it on real work once you trust what it does.
- It installs an opt-in `SessionEnd` hook (session-capture). Hooks execute automatically — only
  enable it once you've read what it runs.

## Scope — what BuildOS is *not*

- **Not a security sandbox.** It does not isolate or contain the agent; it relies on Claude Code's
  own permissions and your judgment.
- **Not enterprise governance.** No SSO, audit guarantees, or compliance posture. Early public
  release, single maintainer.
- **No warranty.** MIT-licensed, provided as-is.

## Reporting a vulnerability

Please **do not** open a public issue for security-sensitive reports.

- Preferred: open a private report via the repository's **Security → Report a vulnerability**
  (GitHub private advisory).
- For non-sensitive concerns (a broken template, a misleading claim), a normal GitHub issue is fine.

Because this is an early single-maintainer project, expect best-effort, not an SLA.
