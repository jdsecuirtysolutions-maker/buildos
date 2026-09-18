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

Local environment inspected: Codex CLI 0.154.0, Claude Code 2.1.245, Python 3.14.2. The Python
helper requires 3.10+ and Git for evidence binding. No credentials or model API calls are needed
for its test suite. Local package/skill validation is separate from runtime model effectiveness.

Codex plugin metadata is included and validated with the Plugin Creator validator. This release
uses the repository-skill install route by default. No marketplace entry or personal plugin
installation is created; app-store discovery is not claimed as tested.

Claude's manifest remains for secondary use. `init --claude` adds a CLAUDE.md pointer to AGENTS.md.
Skills and scripts can be followed manually; live Claude behavior has not been retested. Version
0.2's SessionEnd agent-hook recipe was removed: that event does not support prompt/agent handlers
in the [official hook reference](https://code.claude.com/docs/en/hooks#prompt-based-hooks).
Existing project hooks are not automatically removed; see MIGRATION.md.

No session hooks, scheduler, or multi-agent runtime is part of this release. Future adapters must
name supported host versions, capabilities, permissions, and executed lifecycle tests before
being described as supported. Do not translate a Claude hook name into a guessed Codex equivalent.
