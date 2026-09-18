---
name: buildos-capture
description: Save substantive decisions, corrections, verified facts, and open questions from a known BuildOS work session into a private, replay-safe capture.
---

# BuildOS capture

Use the current conversation or an explicitly supplied transcript. Never search for the latest
ambient transcript. Resolve `../buildos-setup/scripts/buildos.py` relative to this skill.
Capture is explicit session work, not a lifecycle hook.

Use the known session ID, or generate a UUID once and retain it with the handoff. Prepare JSON
in `.buildos/local/` with `goal`, `next_action`, `source` (session identity or exact transcript),
and string lists `decisions`, `corrections`, `verified_facts`, `open_questions`. Each decision
includes rationale; each fact includes actual evidence and currency. Numbers need basis/source.
Hypotheses stay labeled. Exclude credentials, personal identifiers, and irrelevant noise.

Run `python3 <helper> capture --target <project> --session <id> --input <private-json>`.
It writes an immutable record to `knowledge/private/sessions/`. Identical retries are harmless;
different content under an existing ID is rejected. Corrections use a new ID referencing the
earlier record. Empty substantive lists produce no note. Run `refresh` to update the index.

Update `RESUME_HERE.md` separately with public next-action pointers. Capture does not declare
tasks complete or promote its interpretation to verified knowledge.
