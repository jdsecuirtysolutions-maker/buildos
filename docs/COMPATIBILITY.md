# Compatibility contract

Checked 2026-09-18. Primary path: Codex project AGENTS.md plus repository skills under
`.agents/skills/`. These are documented by OpenAI:

- [Project instructions](https://developers.openai.com/es-419/docs/agent-configuration/agents-md)
- [Customization and repository skills](https://developers.openai.com/es-419/docs/customization/overview)
- [Skill creation](https://developers.openai.com/es-419/docs/build-skills)

Skills resolve bundled helper paths from their loaded location. They do not assume Claude
variables or tool names. The root contract respects the host instruction hierarchy. A fresh
session is needed for reliable pickup; AGENTS.override.md and nested instructions can change
which guidance applies and require inspection.

Local environment inspected: Codex CLI 0.154.0 (0.160.0 at 0.3.1), Claude Code 2.1.291, Python 3.14.2. The Python
helper requires 3.10+ and Git for evidence binding. No credentials or model API calls are needed
for its test suite. Local package/skill validation is separate from runtime model effectiveness.

Codex plugin metadata is included and validated with the Plugin Creator validator. This release
uses the repository-skill install route by default. No marketplace entry or personal plugin
installation is created; app-store discovery is not claimed as tested.

Claude Code (checked 2026-10-06 against 2.1.291 and the official
[skills](https://code.claude.com/docs/en/skills) and [memory](https://code.claude.com/docs/en/memory)
docs) discovers project skills only under `.claude/skills/` and reads nothing under `.agents/`.
It reads AGENTS.md natively (2.1.277+) only when no CLAUDE.md exists. `init --claude` therefore
copies the skills to `.claude/skills/` and adds a CLAUDE.md block importing `@AGENTS.md`.
The Claude plugin manifest and repository marketplace pass `claude plugin validate`; the plugin
installs from a local checkout with `claude plugin marketplace add` and exposes
`/buildos:<skill>`. One headless Claude Code session in a disposable `--claude` project listed
both the project and plugin skills and loaded the AGENTS.md contract. Full Claude workflow
behavior has not been tested. Shared skill frontmatter stays within the Agent Skills spec, so
Claude-only fields (for example `disable-model-invocation`) are not used. Version 0.2's
SessionEnd agent-hook recipe was removed: SessionEnd still supports only command, HTTP, and MCP
tool handlers in the [official hook reference](https://code.claude.com/docs/en/hooks#prompt-based-hooks).
Existing project hooks are not automatically removed; see MIGRATION.md.

No session hooks, scheduler, or multi-agent runtime is part of this release. Future adapters must
name supported host versions, capabilities, permissions, and executed lifecycle tests before
being described as supported. Do not translate a Claude hook name into a guessed Codex equivalent.
