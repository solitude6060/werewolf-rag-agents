#!/usr/bin/env python3
"""Summarize remaining final-attempt budget from score-feedback records."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
TOP3 = 0.52380
BASELINE = 0.47119


def read_records(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def score_value(row: dict[str, str]) -> float:
    return float(row.get("score", "nan"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize final Kaggle attempt budget from score feedback records.")
    parser.add_argument("--records", type=Path, default=RECORDS)
    parser.add_argument("--max-attempts", type=int, default=15)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_records(args.records)
    used = len(rows)
    remaining = max(args.max_attempts - used, 0)
    print("ATTEMPT_BUDGET")
    print(f"records_path={args.records}")
    print(f"max_attempts={args.max_attempts}")
    print(f"attempts_used={used}")
    print(f"attempts_remaining={remaining}")
    if not rows:
        print("best_score=none")
        print("top3_hit=no")
        print("next_action=RUN_FIRST_UPLOAD_RUNBOOK")
        print("next_command=python3 experiments/scripts/v1866_final_attempt_runbook.py")
        print("stage_command=python3 experiments/scripts/v1870_stage_current_upload.py")
        return

    best = max(rows, key=score_value)
    latest = rows[-1]
    best_score = score_value(best)
    latest_score = score_value(latest)
    top3_hit = best_score > TOP3
    print(f"best_score={best_score:.5f}")
    print(f"best_candidate={best.get('candidate', '')}")
    print(f"best_group={best.get('group', '')}")
    print(f"delta_vs_current_best={best_score - BASELINE:+.5f}")
    print(f"latest_score={latest_score:.5f}")
    print(f"latest_recommended_next={latest.get('recommended_next', '')}")
    print(f"top3_hit={'yes' if top3_hit else 'no'}")
    if top3_hit:
        print("next_action=STOP_GOAL_CANDIDATE_COMPLETE")
        return
    if remaining <= 0:
        print("next_action=NO_ATTEMPTS_REMAINING")
        return
    recommended = latest.get("recommended_next", "")
    if recommended.startswith("STOP"):
        print("next_action=STOP_RECOMMENDED_BY_ROUTER")
    elif recommended.endswith(".csv"):
        print("next_action=VALIDATE_AND_UPLOAD_RECOMMENDED_NEXT")
        print("next_command=python3 experiments/scripts/v1866_final_attempt_runbook.py --from-records")
        print("stage_command=python3 experiments/scripts/v1870_stage_current_upload.py --from-records")
    else:
        print("next_action=MANUAL_REVIEW")


if __name__ == "__main__":
    main()
