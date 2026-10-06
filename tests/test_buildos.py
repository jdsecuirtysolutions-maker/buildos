"""Behavioral integration checks in disposable repositories; no model/network dependency."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HELPER = Path(__file__).resolve().parents[1] / "plugins/buildos/skills/buildos-setup/scripts/buildos.py"
spec = importlib.util.spec_from_file_location("buildos", HELPER)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class BuildOSTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="buildos-test-")
        self.root = Path(self.temp.name).resolve()

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True,
                              capture_output=True, text=True).stdout

    def write(self, relative, text):
        p = self.root / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return p

    def run_cli(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = b.main([args[0], "--target", str(self.root), *args[1:]])
        return code, output.getvalue()

    def install(self, claude=False):
        changes, _ = b.install_plan(self.root, claude=claude)
        code, out = self.run_cli("init", *( ["--claude"] if claude else []),
                                 "--apply", "--expect-plan", b.plan_token(self.root, changes))
        self.assertEqual(code, 0, out)

    def test_preview_is_read_only_and_apply_needs_current_plan(self):
        code, out = self.run_cli("init")
        self.assertEqual(code, 0, out)
        self.assertEqual(list(self.root.iterdir()), [])
        token = out.split("PLAN ")[1].splitlines()[0]
        self.write("AGENTS.md", "User instruction\n")
        code, _ = self.run_cli("init", "--apply", "--expect-plan", token)
        self.assertEqual(code, 2)
        self.assertFalse((self.root / ".buildos").exists())

    def test_install_rerun_preserves_user_docs_hooks_and_staging(self):
        self.git("init", "-q")
        self.git("config", "core.hooksPath", "existing-hooks")
        self.write("existing-hooks/pre-commit", "original hook")
        self.write("AGENTS.md", "User contract without newline")
        self.write("RESUME_HERE.md", "Existing handoff")
        self.write("user.txt", "staged work")
        self.git("add", "user.txt")
        index = self.git("diff", "--cached")
        self.install()
        self.assertTrue((self.root / "AGENTS.md").read_text().startswith("User contract without newline\n"))
        self.assertEqual((self.root / "RESUME_HERE.md").read_text(), "Existing handoff")
        self.assertEqual(self.git("config", "core.hooksPath").strip(), "existing-hooks")
        self.assertEqual(self.git("diff", "--cached"), index)
        self.assertEqual(b.install_plan(self.root)[0], {})
        self.assertEqual(self.run_cli("doctor")[0], 0)

    def test_owned_conflict_and_modified_block_are_refused(self):
        self.write(".agents/skills/buildos-work/SKILL.md", "user skill")
        with self.assertRaises(b.Error):
            b.install_plan(self.root)
        (self.root / ".agents/skills/buildos-work/SKILL.md").unlink()
        self.install()
        path = self.root / "AGENTS.md"
        path.write_text(path.read_text().replace("Preserve existing work", "Changed user rule"))
        with self.assertRaises(b.Error):
            b.install_plan(self.root)

    def test_upgrade_updates_owned_but_preserves_project_edits(self):
        self.install()
        self.write("docs/buildos/PROJECT.md", "Owner's revised milestone")
        changed = self.root / "docs/buildos/LOOPS.md"
        changed.write_text("old owned version")
        state = b.installed(self.root)
        state["files"]["docs/buildos/LOOPS.md"]["sha256"] = b.digest(changed.read_bytes())
        self.write(b.STATE, json.dumps(state))
        changes, _ = b.install_plan(self.root)
        self.assertIn("docs/buildos/LOOPS.md", changes)
        self.assertNotIn("docs/buildos/PROJECT.md", changes)
        b.transact(self.root, changes)
        self.assertEqual(b.install_plan(self.root)[0], {})

    def test_uninstall_restores_blocks_and_preserves_modified_files(self):
        self.write("AGENTS.md", "Original without newline")
        self.write(".gitignore", "user-ignore\n")
        self.install(claude=True)
        self.write("RESUME_HERE.md", "My handoff")
        changes, warnings = b.uninstall_plan(self.root)
        self.assertTrue(any("RESUME_HERE" in w for w in warnings))
        b.transact(self.root, changes)
        self.assertEqual((self.root / "AGENTS.md").read_text(), "Original without newline")
        self.assertEqual((self.root / ".gitignore").read_text(), "user-ignore\n")
        self.assertEqual((self.root / "RESUME_HERE.md").read_text(), "My handoff")
        self.assertFalse((self.root / "CLAUDE.md").exists())

    def test_claude_install_adds_discoverable_skills_and_imports_agents(self):
        self.install()
        self.assertFalse((self.root / ".claude").exists())
        self.assertFalse((self.root / "CLAUDE.md").exists())
        self.write("CLAUDE.md", "User Claude rule\n")
        self.install(claude=True)
        for skill in ("buildos-setup", "buildos-work", "buildos-knowledge", "buildos-capture"):
            claude_copy = self.root / ".claude/skills" / skill / "SKILL.md"
            self.assertEqual(claude_copy.read_bytes(), (self.root / ".agents/skills" / skill / "SKILL.md").read_bytes())
        self.assertTrue((self.root / ".claude/skills/buildos-setup/scripts/buildos.py").is_file())
        lines = (self.root / "CLAUDE.md").read_text().splitlines()
        self.assertEqual(lines[0], "User Claude rule")
        self.assertIn("@AGENTS.md", lines)
        self.assertEqual(b.install_plan(self.root)[0], {})
        self.assertEqual(self.run_cli("doctor")[0], 0)
        b.transact(self.root, b.uninstall_plan(self.root)[0])
        self.assertEqual((self.root / "CLAUDE.md").read_text(), "User Claude rule\n")
        self.assertEqual([p for p in (self.root / ".claude").rglob("*") if p.is_file()], [])

    def test_upgrade_replaces_old_claude_bridge_and_adds_skills(self):
        self.install(claude=True)
        old_block = b.render_block("CLAUDE.md", "Read AGENTS.md for the shared BuildOS contract.\nClaude compatibility is manual; no lifecycle hooks are installed.")
        self.write("CLAUDE.md", old_block)
        state = b.installed(self.root)
        state["files"]["CLAUDE.md"]["sha256"] = b.digest(old_block.encode())
        for relative in [r for r in state["files"] if r.startswith(".claude/")]:
            del state["files"][relative]
            (self.root / relative).unlink()
        self.write(b.STATE, json.dumps(state))
        changes, _ = b.install_plan(self.root)
        self.assertIn(".claude/skills/buildos-work/SKILL.md", changes)
        self.assertIn("@AGENTS.md", changes["CLAUDE.md"].decode())
        b.transact(self.root, changes)
        self.assertEqual(b.install_plan(self.root)[0], {})

    def test_uninstall_retains_privacy_for_retained_knowledge(self):
        self.git("init", "-q")
        self.install()
        self.write("knowledge/private/raw/client.txt", "private")
        b.transact(self.root, b.uninstall_plan(self.root)[0])
        self.assertTrue(self.git("check-ignore", "knowledge/private/raw/client.txt"))

    def test_symlink_destination_and_source_refused(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.root / "docs").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(b.Error):
            b.install_plan(self.root)
        (self.root / "docs").unlink()
        self.install()
        raw = self.root / "knowledge/private/raw"
        raw.mkdir(parents=True)
        (raw / "elsewhere").symlink_to(outside, target_is_directory=True)
        self.assertEqual(self.run_cli("refresh")[0], 2)

    def test_rollback_restores_original_content_on_write_failure(self):
        self.write("first.txt", "original")
        real = b.atomic
        def fail(root, relative, data):
            if relative == "second.txt" and data == b"new":
                raise OSError("simulated disk error")
            return real(root, relative, data)
        with patch.object(b, "atomic", side_effect=fail):
            with self.assertRaises(OSError):
                b.transact(self.root, {"first.txt": b"changed", "second.txt": b"new"})
        self.assertEqual((self.root / "first.txt").read_text(), "original")
        self.assertFalse((self.root / "second.txt").exists())

    def test_monorepo_subdirectory_scoping(self):
        self.git("init", "-q")
        self.write("AGENTS.md", "Parent instructions")
        child = self.root / "apps/api"
        child.mkdir(parents=True)
        b.transact(child, b.install_plan(child)[0])
        self.assertEqual((self.root / "AGENTS.md").read_text(), "Parent instructions")
        self.assertTrue(b.git(child, "check-ignore", "knowledge/private/raw/x.txt"))

    def test_tracked_sensitive_data_rejected(self):
        self.git("init", "-q")
        self.write("knowledge/raw/client.txt", "private")
        self.git("add", "knowledge/raw/client.txt")
        self.install()
        self.assertEqual(self.run_cli("doctor")[0], 1)
        self.assertEqual(self.run_cli("refresh")[0], 2)

    def test_knowledge_hashes_changes_deletions_and_unsupported_files(self):
        self.install()
        source = self.write("knowledge/private/raw/a.md", "Original fact\n")
        self.write("knowledge/private/raw/scan.pdf", "not extracted")
        self.assertEqual(self.run_cli("refresh")[0], 0)
        inv = b.inventory(self.root)["sources"]
        sid, entry = next((k, v) for k, v in inv.items() if v["path"].endswith("a.md"))
        self.assertEqual(next(v for v in inv.values() if v["path"].endswith("pdf"))["status"], "needs-extraction")
        note = self.write(".buildos/local/summary.json", json.dumps({"summary": "Original fact", "citations": ["line 1"], "as_of": "unknown", "conflicts": [], "uncertainties": []}))
        args = ("summarize", "--source", sid, "--source-hash", entry["sha256"], "--input", str(note))
        self.assertEqual(self.run_cli(*args)[0], 0)
        self.assertEqual(b.inventory(self.root)["sources"][sid]["status"], "current")
        source.write_text("Changed fact")
        self.assertEqual(b.inventory(self.root)["sources"][sid]["status"], "stale")
        self.assertEqual(self.run_cli(*args)[0], 2)
        source.unlink()
        self.assertEqual(b.inventory(self.root)["sources"][sid]["status"], "deleted")

    def test_summary_revision_history(self):
        self.install()
        self.write("knowledge/private/raw/a.txt", "Fact")
        sid, entry = next(iter(b.inventory(self.root)["sources"].items()))
        note = self.write(".buildos/local/note.json", json.dumps({"summary": "Fact", "citations": ["line 1"], "as_of": "unknown", "conflicts": [], "uncertainties": []}))
        args = ("summarize", "--source", sid, "--source-hash", entry["sha256"], "--input", str(note))
        self.assertEqual(self.run_cli(*args)[0], 0)
        payload = json.loads(note.read_text()); payload["summary"] = "Corrected interpretation"
        note.write_text(json.dumps(payload))
        self.assertEqual(self.run_cli(*args)[0], 0)
        self.assertEqual(len(list((self.root / "knowledge/private/history").glob("*.json"))), 1)

    def capture_input(self):
        return self.write(".buildos/local/capture.json", json.dumps({"goal": "Fix auth", "source": "current-session", "next_action": "Review", "decisions": ["Use existing middleware to preserve semantics"], "corrections": [], "verified_facts": [], "open_questions": []}))

    def test_capture_idempotent_conflicting_and_traversal_rejected(self):
        self.install()
        note = self.capture_input()
        args = ("capture", "--session", "session-1", "--input", str(note))
        self.assertEqual(self.run_cli(*args)[0], 0)
        self.assertEqual(self.run_cli(*args)[0], 0)
        self.assertEqual(len(list((self.root / "knowledge/private/sessions").glob("*"))), 1)
        payload = json.loads(note.read_text()); payload["goal"] = "Different"
        note.write_text(json.dumps(payload))
        self.assertEqual(self.run_cli(*args)[0], 2)
        self.assertEqual(self.run_cli("capture", "--session", "../escape", "--input", str(note))[0], 2)

    def test_simultaneous_captures_do_not_clobber(self):
        self.install()
        note = self.capture_input()
        cmd = [sys.executable, str(HELPER), "capture", "--target", str(self.root), "--input", str(note)]
        processes = [subprocess.Popen(cmd + ["--session", f"s-{i}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) for i in range(4)]
        for i, proc in enumerate(processes):
            proc.communicate()
            if proc.returncode == 2:  # Explicit lock contention: safe retry, not silent loss.
                self.assertEqual(self.run_cli("capture", "--session", f"s-{i}", "--input", str(note))[0], 0)
            else:
                self.assertEqual(proc.returncode, 0)
        self.assertEqual(len(list((self.root / "knowledge/private/sessions").glob("*"))), 4)

    def test_empty_capture_skips_write(self):
        self.install()
        note = self.capture_input()
        payload = json.loads(note.read_text()); payload["decisions"] = []
        note.write_text(json.dumps(payload))
        self.assertEqual(self.run_cli("capture", "--session", "empty", "--input", str(note))[0], 0)
        self.assertFalse((self.root / "knowledge/private/sessions").exists())

    def test_verify_records_real_result_staleness_and_log_integrity(self):
        self.git("init", "-q")
        self.install()
        self.write("app.py", "print('hello')\n")
        code, out = self.run_cli("verify", "--", sys.executable, "app.py")
        self.assertEqual(code, 0, out)
        record_path = next((self.root / ".buildos/local/evidence").glob("*/result.json"))
        result = json.loads(record_path.read_text())
        self.assertEqual(result["status"], "passed")
        self.assertEqual((record_path.parent / "stdout.log").read_text(), "hello\n")
        self.write("app.py", "print('changed')\n")
        self.assertIn("stale evidence", self.run_cli("doctor")[1])
        (record_path.parent / "stdout.log").write_text("forged")
        self.assertEqual(self.run_cli("doctor")[0], 1)

    def test_failing_timeout_and_unbound_checks(self):
        self.git("init", "-q")
        self.install()
        self.assertEqual(self.run_cli("verify", "--", sys.executable, "-c", "raise SystemExit(7)")[0], 7)
        self.assertEqual(self.run_cli("verify", "--timeout", "0.05", "--", sys.executable, "-c", "import time; time.sleep(5)")[0], 124)
        self.assertEqual(self.run_cli("verify", "--", sys.executable, "-c", "open('new.txt','w').write('change')")[0], 3)

    def test_missing_argument_not_success(self):
        self.install()
        self.assertEqual(self.run_cli("verify")[0], 2)

    def test_override_and_missing_contract_reference_are_reported(self):
        self.install()
        self.write("AGENTS.override.md", "Other instructions")
        self.assertEqual(self.run_cli("doctor")[0], 1)
        (self.root / "AGENTS.override.md").unlink()
        (self.root / "docs/buildos/ACTION_REQUIRED.md").unlink()
        self.assertIn("Missing contract reference", self.run_cli("doctor")[1])

    def test_file_in_parent_position_refused_before_writes(self):
        self.write("docs", "not a directory")
        with self.assertRaises(b.Error):
            b.install_plan(self.root)
        self.assertEqual(list(self.root.iterdir()), [self.root / "docs"])

    def test_private_commands_require_ignore_rules_before_git_init(self):
        self.assertEqual(self.run_cli("refresh")[0], 2)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_malformed_capture_and_nonfinite_timeout(self):
        self.install()
        note = self.write(".buildos/local/invalid.json", "[]")
        self.assertEqual(self.run_cli("capture", "--session", "x", "--input", str(note))[0], 2)
        self.assertEqual(self.run_cli("verify", "--timeout", "nan", "--", "true")[0], 2)

    def test_installed_helper_self_contained(self):
        self.install()
        helper = self.root / ".agents/skills/buildos-setup/scripts/buildos.py"
        result = subprocess.run([sys.executable, str(helper), "init", "--target", str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("FILES 0", result.stdout)

    def test_setup_build_verify_capture_and_cold_resume_lifecycle(self):
        self.git("init", "-q")
        self.install()
        self.write("app.py", "def double(value):\n    return value\n")
        self.write("acceptance.py", "from app import double\nassert double(3) == 6\nassert double(-2) == -4\n")
        self.write("BUILD_SESSION_PROMPTS.md", "TASK-001: double handles positive and negative integers. Status: in-progress.\n")
        command = ("verify", "--", sys.executable, "-B", "acceptance.py")
        self.assertEqual(self.run_cli(*command)[0], 1)
        self.write("app.py", "def double(value):\n    return value * 2\n")
        self.assertEqual(self.run_cli(*command)[0], 0)
        records = [json.loads(p.read_text()) for p in (self.root / ".buildos/local/evidence").glob("*/result.json")]
        passed = next(r for r in records if r["status"] == "passed")
        self.write("BUILD_SESSION_PROMPTS.md", f"TASK-001 complete: evidence {passed['id']}; positive and negative cases pass.\n")
        self.write("RESUME_HERE.md", f"TASK-001 complete; evidence {passed['id']}. Next action: review the change.\n")
        note = self.capture_input()
        self.assertEqual(self.run_cli("capture", "--session", "lifecycle", "--input", str(note))[0], 0)
        self.assertEqual(self.run_cli("refresh")[0], 0)
        # A separate process reads the persisted handoff/records: no Python module state needed.
        helper = self.root / ".agents/skills/buildos-setup/scripts/buildos.py"
        fresh = subprocess.run([sys.executable, str(helper), "doctor", "--target", str(self.root)], capture_output=True, text=True)
        self.assertEqual(fresh.returncode, 0, fresh.stderr)
        self.assertNotIn(f"stale evidence {passed['id']}", fresh.stdout)
        self.assertIn("lifecycle.json", (self.root / "knowledge/private/INDEX.md").read_text())


if __name__ == "__main__":
    unittest.main()
