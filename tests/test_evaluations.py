import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

PATH = Path(__file__).resolve().parents[1] / "evals/report.py"
spec = importlib.util.spec_from_file_location("report", PATH)
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


class EvaluationTest(unittest.TestCase):
    def aggregate(self, rows):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "results.jsonl"
            path.write_text("\n".join(json.dumps(r) for r in rows))
            return report.aggregate(path)

    def row(self, **changes):
        result = dict(case="tenant-boundary", variant="full", trial=1, model="fixture-model",
                      revision="abc", success=True, false_completion=False, regressions=0,
                      human_interventions=0, seconds=10, tokens=None, evidence="fixture-only")
        result.update(changes)
        return result

    def test_missing_trials_are_not_invented(self):
        result = self.aggregate([])
        self.assertTrue(result["no_trials"])
        self.assertEqual(result["groups"], [])
        result = self.aggregate([self.row()])
        self.assertEqual(len(result["incomplete"]), 9)
        self.assertIsNone(result["groups"][0]["median_tokens"])

    def test_failures_are_included_and_cohorts_separate(self):
        result = self.aggregate([self.row(), self.row(trial=2, success=False, false_completion=True),
                                 self.row(model="different-model")])
        original = next(g for g in result["groups"] if g["model"] == "fixture-model")
        self.assertEqual(original["success_rate"], 0.5)
        self.assertEqual(original["false_completions"], 1)
        self.assertEqual(len(result["groups"]), 2)

    def test_duplicate_and_missing_evidence_rejected(self):
        with self.assertRaises(ValueError):
            self.aggregate([self.row(), self.row()])
        with self.assertRaises(ValueError):
            self.aggregate([self.row(evidence="")])
