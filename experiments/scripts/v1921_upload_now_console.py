#!/usr/bin/env python3
"""Print the exact current upload path and post-score commands without mutating reports."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

import v1902_upload_alias_guard as alias_guard
import v1906_goal_completion_gate as completion_gate

CANONICAL = Path("experiments/final_submission_package/current_upload/submission.csv")
METADATA = Path("experiments/final_submission_package/current_upload/metadata.json")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
VALIDATOR = "python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/current_upload/submission.csv"
DEFAULT_SCAN_ROOT = Path(".")


def read_records(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_score(value: str) -> float | None:
    try:
        score = float(value)
    except ValueError:
        return None
    if not math.isfinite(score) or score < 0.0 or score > 1.0:
        return None
    return score


def metadata_value(metadata: dict[str, Any], key: str, fallback: str = "") -> str:
    value = metadata.get(key, fallback)
    return str(value)


def collect_payload(scan_root: Path) -> dict[str, Any]:
    metadata = json.loads(METADATA.read_text(encoding="utf-8")) if METADATA.exists() else {}
    aliases = alias_guard.default_aliases()

    canonical_exists = CANONICAL.exists()
    canonical_rows = alias_guard.row_count(CANONICAL) if canonical_exists else 0
    canonical_sha = alias_guard.sha256(CANONICAL) if canonical_exists else ""
    expected_sha = metadata_value(metadata, "sha256")
    expected_rows = int(metadata.get("rows", alias_guard.EXPECTED_ROWS) or alias_guard.EXPECTED_ROWS)

    safe_aliases: list[dict[str, str]] = []
    for alias in aliases:
        exists = alias.exists()
        rows = alias_guard.row_count(alias) if exists else 0
        file_sha = alias_guard.sha256(alias) if exists else ""
        safe_aliases.append(
            {
                "path": str(alias),
                "exists": "yes" if exists else "no",
                "rows": str(rows),
                "sha256": file_sha,
                "sha_matches": "yes" if exists and canonical_sha and file_sha == canonical_sha else "no",
            }
        )

    lookalikes = alias_guard.find_submission_lookalikes(scan_root, CANONICAL, aliases, canonical_sha)
    do_not_upload = [item for item in lookalikes if item["status"] == "do_not_upload"]
    suspicious_same_bytes = [item for item in lookalikes if item["status"] == "unlisted_same_bytes"]

    records = read_records(RECORDS)
    parsed_scores = [(score, row) for row in records if (score := parse_score(row.get("score", ""))) is not None]
    best_score = max((score for score, _ in parsed_scores), default=None)
    records_consistent = len(parsed_scores) == len(records)
    top3 = completion_gate.TOP3
    goal_complete = records_consistent and best_score is not None and best_score > top3

    alias_ready = all(
        item["exists"] == "yes" and item["rows"] == str(canonical_rows) and item["sha_matches"] == "yes"
        for item in safe_aliases
    )
    ready = (
        canonical_exists
        and canonical_rows == expected_rows == alias_guard.EXPECTED_ROWS
        and bool(canonical_sha)
        and canonical_sha == expected_sha
        and alias_ready
        and not suspicious_same_bytes
    )

    return {
        "ready_to_upload": "yes" if ready else "no",
        "upload_path": str(CANONICAL),
        "absolute_upload_path": str(CANONICAL.resolve()) if canonical_exists else "missing",
        "candidate": metadata_value(metadata, "candidate"),
        "group": metadata_value(metadata, "group"),
        "order": metadata_value(metadata, "order"),
        "rows": str(canonical_rows),
        "sha256": canonical_sha,
        "expected_sha256": expected_sha,
        "stop_if_score_greater_than": f"{top3:.5f}",
        "goal_complete_by_records": "yes" if goal_complete else "no",
        "records_consistent": "yes" if records_consistent else "no",
        "records_count": str(len(records)),
        "best_score": "none" if best_score is None else f"{best_score:.5f}",
        "safe_aliases": safe_aliases,
        "do_not_upload": do_not_upload,
        "suspicious_same_bytes": suspicious_same_bytes,
        "post_score_dry_run_command": metadata_value(
            metadata,
            "current_score_bridge_command",
            "python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE>",
        ),
        "post_score_confirm_command": metadata_value(
            metadata,
            "current_score_bridge_confirm_command",
            "python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE> --confirm-real-score",
        ),
        "final_status_command": metadata_value(
            metadata,
            "final_goal_status_command",
            "python3 experiments/scripts/v1908_final_goal_status.py",
        ),
        "validator_command": VALIDATOR,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print the current manual upload path, safety aliases, and post-score commands without writing reports."
    )
    parser.add_argument("--scan-root", type=Path, default=DEFAULT_SCAN_ROOT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = collect_payload(args.scan_root)

    print("UPLOAD_NOW_CONSOLE")
    print(f"READY_TO_UPLOAD={payload['ready_to_upload']}")
    print(f"UPLOAD_PATH={payload['upload_path']}")
    print(f"ABSOLUTE_UPLOAD_PATH={payload['absolute_upload_path']}")
    print(f"CANDIDATE={payload['candidate']}")
    print(f"GROUP={payload['group']}")
    print(f"ORDER={payload['order']}")
    print(f"ROWS={payload['rows']}")
    print(f"SHA256={payload['sha256']}")
    print(f"STOP_IF_SCORE_GREATER_THAN={payload['stop_if_score_greater_than']}")
    print(f"GOAL_COMPLETE_BY_RECORDS={payload['goal_complete_by_records']}")
    print(f"RECORDS_CONSISTENT={payload['records_consistent']}")
    print(f"RECORDS_COUNT={payload['records_count']}")
    print(f"BEST_SCORE={payload['best_score']}")
    for item in payload["safe_aliases"]:
        print(
            "SAFE_ALIAS="
            f"{item['path']} rows={item['rows']} sha_matches={item['sha_matches']} exists={item['exists']}"
        )
    for item in payload["do_not_upload"]:
        print(
            "DO_NOT_UPLOAD="
            f"{item['path']} rows={item['rows']} sha_matches={item['sha_matches']} sha256={item['sha256']}"
        )
    for item in payload["suspicious_same_bytes"]:
        print(
            "SUSPICIOUS_UNLISTED_SAME_BYTES="
            f"{item['path']} rows={item['rows']} sha256={item['sha256']}"
        )
    print(f"POST_SCORE_DRY_RUN_COMMAND={payload['post_score_dry_run_command']}")
    print(f"POST_SCORE_CONFIRM_COMMAND={payload['post_score_confirm_command']}")
    print(f"FINAL_STATUS_COMMAND={payload['final_status_command']}")
    print(f"VALIDATOR_COMMAND={payload['validator_command']}")
    print("NEXT_ACTION=upload UPLOAD_PATH exactly; after score appears, run POST_SCORE_DRY_RUN_COMMAND then POST_SCORE_CONFIRM_COMMAND")

    if payload["ready_to_upload"] != "yes":
        raise SystemExit("upload-now console found a readiness mismatch")


if __name__ == "__main__":
    main()
