#!/usr/bin/env python3
"""Offline packaging, reference, and release consistency checks."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/buildos"


def check():
    problems = []
    manifests = [PLUGIN / ".codex-plugin/plugin.json", PLUGIN / ".claude-plugin/plugin.json"]
    loaded = [json.loads(p.read_text()) for p in manifests]
    if any(d["name"] != "buildos" or d["version"] != "0.3.1" for d in loaded):
        problems.append("Release versions/names must agree.")
    if loaded[0].get("skills") != "./skills/":
        problems.append("Codex manifest must expose bundled skills.")
    expected = {"buildos-setup", "buildos-work", "buildos-knowledge", "buildos-capture"}
    actual = {p.parent.name for p in (PLUGIN / "skills").glob("*/SKILL.md")}
    if actual != expected:
        problems.append("Expected all four workflow skills.")
    for p in (PLUGIN / "skills").glob("*/SKILL.md"):
        content = p.read_text()
        match = re.match(r"---\nname: ([a-z0-9-]+)\ndescription: ([^\n]+)\n---\n", content)
        if not match or match[1] != p.parent.name:
            problems.append(f"Invalid skill metadata: {p.relative_to(ROOT)}")
        if "disable-model-invocation" in content or "allowed-tools:" in content:
            problems.append(f"Host-specific frontmatter in shared skill: {p}")
    for p in ROOT.rglob("*.md"):
        if ".git" in p.parts or ".buildos" in p.parts:
            continue
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", p.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            target = target.split("#", 1)[0]
            if target and not (p.parent / target).exists():
                problems.append(f"Broken link in {p.relative_to(ROOT)}: {target}")
    templates = PLUGIN / "skills/buildos-setup/templates"
    for p in templates.rglob("*.md"):
        if re.search(r"<FILL|\[TODO:", p.read_text()):
            problems.append(f"Unfinished template placeholder: {p}")
    if list(PLUGIN.rglob("settings.snippet.json")):
        problems.append("Unsupported legacy automatic capture must not ship.")
    for problem in problems:
        print("FAIL:", problem)
    if not problems:
        print("Package metadata, skill entrypoints, release versions, and local Markdown links passed.")
    return bool(problems)


if __name__ == "__main__":
    sys.exit(check())
