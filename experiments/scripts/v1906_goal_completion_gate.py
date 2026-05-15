#!/usr/bin/env python3
"""Records-based completion gate for the active final leaderboard goal."""
from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
OUT_JSON = Path("experiments/reports/v1906_goal_completion_gate.json")
OUT_MD = Path("experiments/reports/v1906_goal_completion_gate.md")
TOP3 = 0.52380
MAX_FINAL_ATTEMPTS = 5


def read_records(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_score(row: dict[str, str], index: int, errors: list[str]) -> float | None:
    raw = row.get("score", "")
    try:
        score = float(raw)
    except ValueError:
        errors.append(f"row_{index}_score_not_number:{raw}")
        return None
    if not math.isfinite(score) or score < 0.0 or score > 1.0:
        errors.append(f"row_{index}_score_out_of_range:{raw}")
        return None
    return score


def add_check(checks: list[dict[str, str]], name: str, ok: bool, detail: str) -> None:
    checks.append({"name": name, "ok": "yes" if ok else "no", "detail": detail})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Decide whether the active leaderboard goal is complete from score records.")
    parser.add_argument("--records", type=Path, default=RECORDS)
    parser.add_argument("--out-json", type=Path, default=OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    return parser.parse_args()


def write_outputs(payload: dict[str, Any], out_json: Path, out_md: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v1906 Goal Completion Gate",
        "",
        f"Generated UTC: `{payload['generated_at_utc']}`",
        "",
        "## Summary",
        "",
        f"- Goal complete: `{payload['goal_complete']}`",
        f"- Records consistent: `{payload['records_consistent']}`",
        f"- Records path: `{payload['records_path']}`",
        f"- Records count: `{payload['records_count']}`",
        f"- Best score: `{payload['best_score']}`",
        f"- Top-3 threshold: `>{payload['top3_threshold']}`",
        "",
        "## Best record",
        "",
        "```json",
        json.dumps(payload["best_record"], indent=2, sort_keys=True),
        "```",
        "",
        "## Checks",
        "",
        "| Check | OK | Detail |",
        "| --- | --- | --- |",
    ]
    for check in payload["checks"]:
        detail = str(check["detail"]).replace("|", "\\|")
        lines.append(f"| {check['name']} | {check['ok']} | `{detail}` |")
    if payload["errors"]:
        lines.extend(["", "## Errors", ""])
        for error in payload["errors"]:
            lines.append(f"- `{error}`")
    lines.extend(
        [
            "",
            "## Completion boundary",
            "",
            "Only `GOAL_COMPLETE=yes` from this records-based gate is sufficient local evidence to allow marking the active goal complete.",
            "",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    records = read_records(args.records)
    errors: list[str] = []
    checks: list[dict[str, str]] = []
    parsed: list[tuple[float, dict[str, str]]] = []

    add_check(checks, "records_exist", args.records.exists(), str(args.records))
    add_check(checks, "records_within_attempt_budget", len(records) <= MAX_FINAL_ATTEMPTS, str(len(records)))

    for index, row in enumerate(records, start=1):
        score = parse_score(row, index, errors)
        if score is None:
            continue
        expected_hit = "yes" if score > TOP3 else "no"
        actual_hit = row.get("top3_hit", "")
        if actual_hit != expected_hit:
            errors.append(f"row_{index}_top3_flag_mismatch:score={score:.5f}:top3_hit={actual_hit}:expected={expected_hit}")
        parsed.append((score, row))

    best_score = max((score for score, _ in parsed), default=None)
    best_record = max(parsed, key=lambda item: item[0])[1] if parsed else {}
    records_consistent = not errors and len(records) <= MAX_FINAL_ATTEMPTS
    goal_complete = records_consistent and best_score is not None and best_score > TOP3

    add_check(checks, "score_values_valid", not any(error for error in errors if "score_" in error), ",".join(errors) if errors else "ok")
    add_check(checks, "top3_flags_consistent", not any("top3_flag_mismatch" in error for error in errors), ",".join(errors) if errors else "ok")
    add_check(checks, "best_score_exceeds_threshold", best_score is not None and best_score > TOP3, "none" if best_score is None else f"{best_score:.5f}")

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "goal_complete": "yes" if goal_complete else "no",
        "records_consistent": "yes" if records_consistent else "no",
        "records_path": str(args.records),
        "records_count": len(records),
        "best_score": "none" if best_score is None else f"{best_score:.5f}",
        "best_record": best_record,
        "top3_threshold": f"{TOP3:.5f}",
        "checks": checks,
        "errors": errors,
    }
    write_outputs(payload, args.out_json, args.out_md)

    print("GOAL_COMPLETION_GATE")
    print(f"GOAL_COMPLETE={'yes' if goal_complete else 'no'}")
    print(f"RECORDS_CONSISTENT={'yes' if records_consistent else 'no'}")
    print(f"RECORDS_PATH={args.records}")
    print(f"RECORDS_COUNT={len(records)}")
    print(f"BEST_SCORE={'none' if best_score is None else f'{best_score:.5f}'}")
    print(f"TOP3_THRESHOLD={TOP3:.5f}")
    print(f"REPORT={args.out_md}")
    print(f"JSON={args.out_json}")
    if errors:
        print("ERRORS=" + ";".join(errors))
        raise SystemExit("goal completion records are inconsistent")


if __name__ == "__main__":
    main()
