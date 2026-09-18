#!/usr/bin/env python3
"""Aggregate actual trial records without inventing missing outcomes."""
import json
import math
from pathlib import Path
import statistics
import sys


def aggregate(path):
    cases = {x["id"] for x in json.loads(Path(__file__).with_name("cases.json").read_text())}
    variants = ("ordinary", "compact", "full")
    groups, seen = {}, set()
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("case") not in cases or row.get("variant") not in variants:
            raise ValueError("Unknown case or variant")
        for field in ("model", "revision", "evidence"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"Missing {field}")
        if type(row.get("trial")) is not int or row["trial"] < 1:
            raise ValueError("trial must be a positive integer")
        for field in ("success", "false_completion"):
            if type(row.get(field)) is not bool:
                raise ValueError(f"{field} must be boolean")
        for field in ("regressions", "human_interventions", "seconds", "tokens"):
            value = row.get(field)
            if field == "tokens" and value is None:
                continue
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise ValueError(f"Invalid {field}")
        key = row["case"], row["variant"], row["model"], row["revision"]
        identity = key + (row["trial"],)
        if identity in seen:
            raise ValueError("Duplicate trial")
        seen.add(identity)
        groups.setdefault(key, []).append(row)
    output = []
    for key, rows in sorted(groups.items()):
        known_tokens = [r["tokens"] for r in rows if r["tokens"] is not None]
        output.append({"case": key[0], "variant": key[1], "model": key[2], "revision": key[3],
                       "trials": len(rows), "success_rate": sum(r["success"] for r in rows) / len(rows),
                       "false_completions": sum(r["false_completion"] for r in rows),
                       "regressions": sum(r["regressions"] for r in rows),
                       "human_interventions": sum(r["human_interventions"] for r in rows),
                       "median_seconds": statistics.median(r["seconds"] for r in rows),
                       "median_tokens": statistics.median(known_tokens) if known_tokens else None,
                       "tokens_known_for": len(known_tokens)})
    cohorts = {(k[2], k[3]) for k in groups}
    missing = [dict(case=c, variant=v, model=m, revision=r, trials=len(groups.get((c, v, m, r), [])))
               for m, r in sorted(cohorts) for c in sorted(cases) for v in variants
               if len(groups.get((c, v, m, r), [])) < 5]
    return {"groups": output, "incomplete": missing, "no_trials": not groups,
            "note": "Descriptive results only; no causal or statistical significance claim."}


if __name__ == "__main__":
    try:
        print(json.dumps(aggregate(sys.argv[1]), indent=2))
    except (IndexError, OSError, ValueError, KeyError, TypeError) as exc:
        sys.exit(f"Provide a valid trial JSONL file: {exc}")
