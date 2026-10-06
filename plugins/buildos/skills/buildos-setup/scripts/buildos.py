#!/usr/bin/env python3
"""BuildOS local helpers. Python 3.10+, standard library only; no network calls."""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import difflib
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import uuid

VERSION = "0.3.1"
SKILLS = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).resolve().parents[1] / "templates"
STATE = ".buildos/install.json"
PRIVATE = "knowledge/private"
HANDOFF_FILES = {"BUILD_SESSION_PROMPTS.md", "ISSUES_AND_IMPROVEMENTS.md", "RESUME_HERE.md"}
BLOCKS = {
    "AGENTS.md": ("<!-- BuildOS:begin -->", "<!-- BuildOS:end -->"),
    "CLAUDE.md": ("<!-- BuildOS:begin -->", "<!-- BuildOS:end -->"),
    ".gitignore": ("# BuildOS:begin", "# BuildOS:end"),
}


class Error(Exception):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def safe(root, relative):
    """Reject traversal, symlinks (including internal ones), and non-file destinations."""
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts or not rel.parts or "\\" in str(relative):
        raise Error(f"Unsafe path: {relative}")
    path = root
    for index, part in enumerate(rel.parts):
        path = path / part
        if path.is_symlink():
            raise Error(f"Symlink is not supported: {relative}")
        if index < len(rel.parts) - 1 and path.exists() and not path.is_dir():
            raise Error(f"Parent path is not a directory: {relative}")
    if path.exists() and not path.is_file():
        raise Error(f"Expected a regular file: {relative}")
    return path


def read(root, relative):
    path = safe(root, relative)
    return path.read_bytes() if path.exists() else None


def json_read(root, relative, default=None):
    data = read(root, relative)
    return json.loads(data) if data is not None else default


def atomic(root, relative, data):
    path = safe(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o600
    fd, temporary = tempfile.mkstemp(prefix=".buildos-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextlib.contextmanager
def lock(root):
    path = safe(root, ".buildos/write.lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise Error("Another BuildOS writer holds .buildos/write.lock; inspect it before removing a stale lock.")
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(f"pid={os.getpid()} time={now()}\n")
        yield
    finally:
        path.unlink()


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    return result.stdout if result.returncode == 0 else None


def block_span(data, start, end):
    text = (data or b"").decode("utf-8")
    if start not in text and end not in text:
        return text, None
    if text.count(start) != 1 or text.count(end) != 1:
        raise Error("Malformed or duplicate BuildOS markers; merge manually.")
    a, b = text.index(start), text.index(end) + len(end)
    if b < a or (a and text[a - 1] != "\n") or (b < len(text) and text[b] != "\n"):
        raise Error("Malformed BuildOS block boundaries.")
    if b < len(text):
        b += 1
    return text, (a, b)


def render_block(relative, body):
    start, end = BLOCKS[relative]
    return f"{start}\n{body.rstrip()}\n{end}\n"


def replace_block(relative, data, body, previous=None):
    text, span = block_span(data, *BLOCKS[relative])
    if span:
        a, b = span
        if previous is None or digest(text[a:b].encode()) != previous["sha256"]:
            raise Error(f"User-edited or unowned BuildOS block in {relative}; merge it manually.")
        return (text[:a] + body + text[b:]).encode(), previous.get("separator", "")
    if previous is not None:
        raise Error(f"Managed block removed from {relative}; resolve manually before upgrading.")
    separator = "" if not text or text.endswith("\n") else "\n"
    return (text + separator + body).encode(), separator


def profile_load(path, root, old):
    profile = json.loads(Path(path).read_text()) if path else old.get("profile", {})
    defaults = {"name": root.name, "purpose": "Not established; ask the owner before planning product work.",
                "milestone": "Not established.", "constraint": "Preserve working behavior and verify the requested change.",
                "verify": [], "overlays": []}
    if not isinstance(profile, dict) or set(profile) - set(defaults):
        raise Error("Profile accepts only name, purpose, milestone, constraint, verify, overlays.")
    defaults.update(profile)
    for key in ("name", "purpose", "milestone", "constraint"):
        if not isinstance(defaults[key], str) or not defaults[key].strip():
            raise Error(f"Profile {key} must be a nonempty string.")
        if "BuildOS:" in defaults[key] or "<FILL" in defaults[key]:
            raise Error(f"Profile {key} contains reserved markers.")
    commands = defaults["verify"]
    if not isinstance(commands, list) or any(not isinstance(c, list) or not c or
            any(not isinstance(x, str) or not x for x in c) for c in commands):
        raise Error("verify must be a list of nonempty argv lists; no shell interpolation.")
    if not isinstance(defaults["overlays"], list) or any(x not in ("web-saas", "security-product") for x in defaults["overlays"]):
        raise Error("Unknown overlay.")
    return defaults


def installed(root):
    state = json_read(root, STATE, {})
    if state and (state.get("schema") != 1 or not isinstance(state.get("files"), dict)):
        raise Error("Unsupported installation record; do not overwrite it.")
    return state


def install_plan(root, profile_path=None, claude=False):
    old = installed(root)
    profile = profile_load(profile_path, root, old)
    files, desired, warnings = {}, {}, []
    claude = claude or "CLAUDE.md" in old.get("files", {})
    # Claude Code discovers project skills only under .claude/skills/, never .agents/.
    skill_roots = [".agents/skills/"] + ([".claude/skills/"] if claude else [])
    # Fully owned assets update only when unchanged; project documents are seed-once.
    for path in sorted(SKILLS.glob("buildos-*/*")):
        candidates = sorted(path.rglob("*")) if path.is_dir() else [path]
        for source in candidates:
            if not source.is_file() or "__pycache__" in source.parts or source.suffix == ".pyc":
                continue
            if source.is_symlink():
                raise Error(f"Symlink in source package: {source}")
            for skill_root in skill_roots:
                desired[skill_root + source.relative_to(SKILLS).as_posix()] = (source.read_bytes(), "owned")
    for source in sorted((TEMPLATES / "project").rglob("*")):
        if source.is_file():
            relative = source.relative_to(TEMPLATES / "project").as_posix()
            desired[relative] = (source.read_bytes(), "seed")
    project = (f"# {profile['name']}\n\n{profile['purpose']}\n\n"
               f"Milestone: {profile['milestone']}\n\nTrade-off constraint: {profile['constraint']}\n\n"
               "Verification commands (argv; review before executing):\n\n```json\n" +
               json.dumps(profile["verify"], indent=2) + "\n```\n\n"
               "Update this file as project facts change. Keep sensitive facts in knowledge/private/.\n")
    desired["docs/buildos/PROJECT.md"] = (project.encode(), "seed")
    for source in sorted((TEMPLATES / "references").rglob("*")):
        if source.is_file():
            desired["docs/buildos/" + source.relative_to(TEMPLATES / "references").as_posix()] = (source.read_bytes(), "owned")
    instructions = (TEMPLATES / "AGENTS.md").read_text()
    for overlay in profile["overlays"]:
        instructions += f"\nFor relevant changes, read docs/buildos/overlays/{overlay}.md.\n"
    desired["AGENTS.md"] = (render_block("AGENTS.md", instructions).encode(), "block")
    desired[".gitignore"] = (render_block(".gitignore", "/knowledge/private/\n/knowledge/raw/\n/knowledge/compiled/\n/knowledge/sessions/\n/knowledge/INDEX.md\n/.buildos/local/\n/.buildos/write.lock\n**/__pycache__/\n").encode(), "block")
    if claude:
        # Any CLAUDE.md stops Claude Code from reading AGENTS.md natively; import it instead.
        desired["CLAUDE.md"] = (render_block("CLAUDE.md", "@AGENTS.md\n\nBuildOS skills for Claude Code are in .claude/skills/; no lifecycle hooks are installed.").encode(), "block")
    changes = {}
    for relative, (content, kind) in desired.items():
        current = read(root, relative)
        previous = old.get("files", {}).get(relative)
        if kind == "block":
            result, separator = replace_block(relative, current, content.decode(), previous)
            files[relative] = {"kind": kind, "sha256": digest(content), "separator": separator,
                               "created": previous.get("created", False) if previous else current is None}
        elif kind == "seed" and current is not None:
            if previous:
                files[relative] = previous
            else:
                warnings.append(f"Preserved existing user document: {relative}")
            continue
        else:
            if current is not None and (not previous or digest(current) != previous["sha256"]):
                raise Error(f"Refusing to replace existing or edited file: {relative}")
            result = content
            files[relative] = {"kind": kind, "sha256": digest(content)}
        if result != current:
            changes[relative] = result
    # Removed package assets are only deleted when they still match the recorded content.
    for relative, previous in old.get("files", {}).items():
        if relative in desired:
            continue
        current = read(root, relative)
        if current is not None and digest(current) == previous["sha256"] and previous["kind"] == "owned":
            changes[relative] = None
        elif current is not None:
            files[relative] = previous
            warnings.append(f"Retained retired, modified file: {relative}")
    state = {"schema": 1, "version": VERSION, "profile": profile, "files": files}
    if read(root, STATE) != encoded(state):
        changes[STATE] = encoded(state)
    return changes, warnings


def uninstall_plan(root):
    old = installed(root)
    if not old:
        raise Error("No BuildOS installation record found.")
    changes, warnings = {}, []
    for relative, entry in old["files"].items():
        current = read(root, relative)
        if current is None:
            continue
        if relative == ".gitignore" and (read(root, "knowledge/INDEX.md") is not None or
                any(walk_files(root, p) for p in
                    (PRIVATE, "knowledge/raw", "knowledge/compiled", "knowledge/sessions", ".buildos/local"))):
            warnings.append("Retained privacy ignore block because local knowledge/evidence remains.")
            continue
        if entry["kind"] == "block":
            text, span = block_span(current, *BLOCKS[relative])
            if not span or digest(text[span[0]:span[1]].encode()) != entry["sha256"]:
                warnings.append(f"Preserved edited block: {relative}")
                continue
            a, b = span
            separator = entry.get("separator", "")
            if separator and text[:a].endswith(separator):
                a -= len(separator)
            result = (text[:a] + text[b:]).encode()
            changes[relative] = None if not result and entry.get("created") else result
        elif digest(current) == entry["sha256"]:
            changes[relative] = None
        else:
            warnings.append(f"Preserved modified file: {relative}")
    changes[STATE] = None
    warnings.append("Knowledge, evidence, and user-created files are retained. Empty directories are retained.")
    return changes, warnings


def plan_token(root, changes):
    records = {p: [digest(read(root, p)) if read(root, p) is not None else None,
                   digest(value) if value is not None else None] for p, value in changes.items()}
    return digest(encoded({"target": str(root), "changes": records}))


def transact(root, changes):
    originals = {p: read(root, p) for p in changes}
    completed = []
    try:
        for relative, data in changes.items():
            completed.append(relative)
            if data is None:
                safe(root, relative).unlink(missing_ok=True)
            else:
                atomic(root, relative, data)
    except BaseException:
        for relative in reversed(completed):
            if originals[relative] is None:
                safe(root, relative).unlink(missing_ok=True)
            else:
                atomic(root, relative, originals[relative])
        raise


def setup(args, root):
    planner = (lambda: uninstall_plan(root)) if args.command == "uninstall" else (lambda: install_plan(root, args.profile, args.claude))
    changes, warnings = planner()
    token = plan_token(root, changes)
    if not args.apply:
        for relative, data in changes.items():
            if relative == STATE:
                print(f"UPDATE installation record: {relative}")
                continue
            before = (read(root, relative) or b"").decode("utf-8")
            after = (data or b"").decode("utf-8")
            print("".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                             fromfile=relative, tofile=relative)), end="")
        for warning in warnings:
            print(f"NOTE: {warning}")
        print(f"PLAN {token}\nFILES {len(changes)}\nNo files written. Apply with --apply --expect-plan {token}")
        return 0
    if args.expect_plan != token:
        raise Error("Missing or stale --expect-plan. Preview again before applying.")
    with lock(root):
        changes, warnings = planner()
        if plan_token(root, changes) != token:
            raise Error("Files changed while acquiring lock; preview again.")
        transact(root, changes)
    print(f"Applied {len(changes)} changes to {root}.")
    for warning in warnings:
        print(f"NOTE: {warning}")
    return 0


def private_check(root):
    patterns = ["knowledge/private/", "knowledge/raw/", "knowledge/compiled/", "knowledge/sessions/", ".buildos/local/"]
    tracked = git(root, "ls-files", "-z")
    if tracked is None:
        ignored = (read(root, ".gitignore") or b"").decode().splitlines()
        if any("/" + p not in ignored for p in patterns):
            raise Error("Install BuildOS privacy ignore rules before recording local data in a non-Git project.")
    if tracked is not None:
        exposed = [x for x in tracked.decode().split("\0") if any(x.startswith(p) for p in patterns) or x == "knowledge/INDEX.md"]
        if exposed:
            raise Error("Private files are tracked by Git; review and untrack explicitly: " + ", ".join(exposed))
        for path in patterns:
            if git(root, "check-ignore", "--no-index", "--", path + "buildos-privacy-probe") is None:
                raise Error(f"Private path is not ignored: {path}")


def walk_files(root, directory):
    base = root / directory
    # Validate ancestors even for an absent directory.
    safe(root, directory + "/.probe")
    if not base.exists():
        return []
    result = []
    for folder, dirs, files in os.walk(base, followlinks=False):
        for name in dirs + files:
            p = Path(folder) / name
            if p.is_symlink():
                raise Error(f"Symlink is not supported: {p.relative_to(root)}")
        result.extend(Path(folder) / name for name in files)
    return sorted(result)


def inventory(root):
    previous = json_read(root, PRIVATE + "/inventory.json", {"sources": {}})["sources"]
    sources = {}
    for path in walk_files(root, PRIVATE + "/raw"):
        rel = path.relative_to(root).as_posix()
        data = path.read_bytes()
        sid = digest(rel.encode())[:24]
        status = "needs-extraction"
        if path.suffix.lower() in (".md", ".txt", ".csv", ".json", ".jsonl"):
            try:
                data.decode("utf-8")
                status = "needs-summary"
            except UnicodeDecodeError:
                status = "unreadable-text"
        note = json_read(root, PRIVATE + f"/compiled/{sid}.json", {})
        if note.get("source_sha256") == digest(data):
            status = "current"
        elif note:
            status = "stale"
        sources[sid] = {"path": rel, "sha256": digest(data), "status": status,
                        "sensitivity": "private", "bytes": len(data)}
    for sid, entry in previous.items():
        if sid not in sources:
            sources[sid] = {**entry, "status": "deleted"}
    return {"schema": 1, "sources": sources}


def refresh(root):
    private_check(root)
    with lock(root):
        result = inventory(root)
        index = "# Private knowledge index\n\nGenerated inventory; summaries are interpretations, not authority.\n\n"
        for sid, entry in result["sources"].items():
            index += f"- {sid}: {entry['path']} — {entry['status']}\n"
        index += "\nSession captures (unreviewed until checked against their evidence):\n"
        for path in walk_files(root, PRIVATE + "/sessions"):
            index += f"- {path.relative_to(root).as_posix()}\n"
        atomic(root, PRIVATE + "/inventory.json", encoded(result))
        atomic(root, PRIVATE + "/INDEX.md", index.encode())
    print(json.dumps(result, indent=2))
    return 0


def summarize(args, root):
    private_check(root)
    note = json.loads(Path(args.input).read_text())
    with lock(root):
        sources = inventory(root)["sources"]
        entry = sources.get(args.source)
        if not entry or entry["status"] == "deleted":
            raise Error("Unknown or deleted source. Refresh and select an existing source ID.")
        if args.source_hash != entry["sha256"]:
            raise Error("Source changed since it was read; re-read before summarizing.")
        if not isinstance(note, dict) or not isinstance(note.get("summary"), str) or not note["summary"].strip():
            raise Error("Summary requires nonempty summary text.")
        if not isinstance(note.get("citations"), list) or not note["citations"] or any(not isinstance(c, str) or not c.strip() for c in note["citations"]):
            raise Error("Summary requires source locators in citations (pages, lines, or cells).")
        for field in ("conflicts", "uncertainties"):
            if not isinstance(note.get(field), list) or any(not isinstance(x, str) for x in note[field]):
                raise Error(f"Summary requires a {field} list; use [] when none are known.")
        if not isinstance(note.get("as_of"), str) or not note["as_of"].strip():
            raise Error("Summary requires as_of; use unknown when source currency is unknown.")
        record = {**note, "schema": 1, "source_id": args.source, "source_path": entry["path"],
                  "source_sha256": entry["sha256"], "sensitivity": "private", "recorded_at": now()}
        path = PRIVATE + f"/compiled/{args.source}.json"
        previous = read(root, path)
        if previous:
            atomic(root, PRIVATE + f"/history/{args.source}-{digest(previous)}.json", previous)
        atomic(root, path, encoded(record))
    return refresh(root)


def capture(args, root):
    private_check(root)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,119}", args.session):
        raise Error("Session ID must be 1–120 letters, digits, underscores, or hyphens.")
    note = json.loads(Path(args.input).read_text())
    if not isinstance(note, dict):
        raise Error("Capture input must be a JSON object.")
    for key in ("goal", "next_action", "source"):
        if not isinstance(note.get(key), str) or not note[key].strip():
            raise Error(f"Capture requires {key}.")
    for key in ("decisions", "corrections", "verified_facts", "open_questions"):
        if not isinstance(note.get(key), list) or any(not isinstance(x, str) for x in note[key]):
            raise Error(f"Capture requires a {key} string list.")
    if not any(note[key] for key in ("decisions", "corrections", "verified_facts", "open_questions")):
        print("No substantive content; no capture written.")
        return 0
    record = {"schema": 1, "session_id": args.session, "sensitivity": "private", "note": note}
    relative = PRIVATE + f"/sessions/{args.session}.json"
    with lock(root):
        previous = read(root, relative)
        if previous is not None and previous != encoded(record):
            raise Error("Session ID already has different content; use a new correction capture referencing it.")
        if previous is None:
            atomic(root, relative, encoded(record))
    print(f"Captured {args.session}; repeat submissions are idempotent. Refresh knowledge to update its index.")
    return 0


def snapshot(root):
    head = git(root, "rev-parse", "HEAD")
    files = git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    if files is None:
        return {"head": None, "tree_sha256": None, "binding": "unavailable (not a Git repository)"}
    hashes = {}
    for relative in sorted(set(files.decode().split("\0")) - {""}):
        if relative in HANDOFF_FILES or relative.startswith((".buildos/local/", PRIVATE + "/")):
            continue
        path = root / relative
        if path.is_symlink():
            hashes[relative] = "symlink:" + os.readlink(path)
        elif path.is_file():
            hashes[relative] = digest(path.read_bytes())
        else:
            hashes[relative] = "absent-or-submodule"
    return {"head": head.decode().strip() if head else None,
            "tree_sha256": digest(encoded(hashes)),
            "binding": "tracked and nonignored files; excludes ignored artifacts, submodule contents, and the three handoff documents",
            "excluded_handoff_files": sorted(HANDOFF_FILES)}


def verify(args, root):
    private_check(root)
    command = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
    if not command:
        raise Error("Supply the approved check after -- (an argv list, not a shell expression).")
    before = snapshot(root)
    run_id = uuid.uuid4().hex
    directory = ".buildos/local/evidence/" + run_id
    start = now()
    stdout = safe(root, directory + "/stdout.log")
    stderr = safe(root, directory + "/stderr.log")
    stdout.parent.mkdir(parents=True, exist_ok=False)
    timeout = False
    with stdout.open("wb") as out, stderr.open("wb") as err:
        os.chmod(stdout, 0o600)
        os.chmod(stderr, 0o600)
        try:
            process = subprocess.Popen(command, cwd=root, stdout=out, stderr=err,
                                       start_new_session=(os.name == "posix"))
            try:
                code = process.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                timeout, code = True, 124
                if os.name == "posix":
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
                process.wait()
            except BaseException:
                if os.name == "posix":
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
                process.wait()
                raise
        except OSError as exc:
            err.write(str(exc).encode())
            code = 127
    after = snapshot(root)
    stable = before == after and before["tree_sha256"] is not None
    record = {"schema": 1, "id": run_id, "command": command, "started_at": start,
              "finished_at": now(), "exit_code": code, "timed_out": timeout,
              "before": before, "after": after, "stable_tree": stable,
              "stdout_sha256": digest(stdout.read_bytes()), "stderr_sha256": digest(stderr.read_bytes()),
              "status": "passed" if code == 0 and stable else "failed" if code else "unbound",
              "limits": "A passing command is evidence for that check only, not proof of task completion. Logs may contain secrets; keep private."}
    atomic(root, directory + "/result.json", encoded(record))
    print(json.dumps(record, indent=2))
    print(f"Evidence: {directory}/result.json")
    return (0 if stable else 3) if code == 0 else code if 0 < code <= 125 else 1


def doctor(root):
    problems = []
    state = installed(root)
    if not state:
        problems.append("No installation record.")
    if read(root, "AGENTS.override.md"):
        problems.append("AGENTS.override.md can supersede AGENTS.md; reconcile the project contract manually.")
    try:
        private_check(root)
    except Error as exc:
        problems.append(str(exc))
    for relative, entry in state.get("files", {}).items():
        data = read(root, relative)
        if data is None:
            problems.append(f"Missing installed file: {relative}")
        elif entry["kind"] == "owned" and digest(data) != entry["sha256"]:
            problems.append(f"Edited package file (upgrade conflict): {relative}")
        elif entry["kind"] == "block":
            text, span = block_span(data, *BLOCKS[relative])
            if not span or digest(text[span[0]:span[1]].encode()) != entry["sha256"]:
                problems.append(f"Edited or missing managed block: {relative}")
    for relative in ("AGENTS.md", "docs/buildos/PROJECT.md", "RESUME_HERE.md", "BUILD_SESSION_PROMPTS.md", "ISSUES_AND_IMPROVEMENTS.md"):
        data = read(root, relative)
        if data and re.search(r"<FILL|\[TODO:", data.decode()):
            problems.append(f"Unresolved scaffold placeholder: {relative}")
    contract = (read(root, "AGENTS.md") or b"").decode()
    for reference in re.findall(r"`(docs/buildos/[^`]+\.md)`", contract):
        if read(root, reference) is None:
            problems.append(f"Missing contract reference: {reference}")
    for path in walk_files(root, ".buildos/local/evidence"):
        if path.name != "result.json":
            continue
        record = json.loads(path.read_text())
        for stream in ("stdout", "stderr"):
            log = read(root, (path.parent / (stream + ".log")).relative_to(root).as_posix())
            if log is None or digest(log) != record[stream + "_sha256"]:
                problems.append(f"Missing or altered evidence log: {record['id']}/{stream}")
        if not record["after"]["tree_sha256"] or record["after"]["tree_sha256"] != snapshot(root)["tree_sha256"]:
            print(f"NOTE: stale evidence {record['id']}; rerun relevant checks before completion.")
    for sid, entry in inventory(root)["sources"].items():
        if entry["status"] != "current":
            print(f"NOTE: knowledge {sid}: {entry['status']}")
    for problem in problems:
        print("FAIL: " + problem)
    print("Doctor passed." if not problems else f"Doctor found {len(problems)} problem(s).")
    return int(bool(problems))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "uninstall", "doctor", "refresh", "summarize", "capture", "verify"):
        p = subs.add_parser(name)
        p.add_argument("--target", type=Path, default=Path.cwd())
        if name in ("init", "uninstall"):
            p.add_argument("--apply", action="store_true")
            p.add_argument("--expect-plan")
        if name == "init":
            p.add_argument("--profile", help="JSON containing public project facts only")
            p.add_argument("--claude", action="store_true", help="add Claude Code skills and a CLAUDE.md import of AGENTS.md; no hooks")
        if name in ("summarize", "capture"):
            p.add_argument("--input", required=True, help="Private JSON input file")
        if name == "summarize":
            p.add_argument("--source", required=True)
            p.add_argument("--source-hash", required=True)
        if name == "capture":
            p.add_argument("--session", required=True)
        if name == "verify":
            p.add_argument("--timeout", type=float, default=300)
            p.add_argument("argv", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    root = args.target.expanduser().resolve()
    try:
        if not root.is_dir():
            raise Error("Target must be an existing project directory.")
        if args.command in ("init", "uninstall"):
            return setup(args, root)
        if args.command == "verify":
            if not math.isfinite(args.timeout) or args.timeout <= 0:
                raise Error("Timeout must be finite and positive.")
            return verify(args, root)
        if args.command == "doctor":
            return doctor(root)
        if args.command == "refresh":
            return refresh(root)
        if args.command == "summarize":
            return summarize(args, root)
        return capture(args, root)
    except (Error, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"BuildOS: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
