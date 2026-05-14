#!/usr/bin/env python3
"""Print a copy/paste template for reporting the real private score."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UPLOAD = Path("experiments/final_submission_package/current_upload/submission.csv")
METADATA = Path("experiments/final_submission_package/current_upload/metadata.json")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
OUT_JSON = Path("experiments/reports/v1893_score_report_template.json")
OUT_MD = Path("experiments/reports/v1893_score_report_template.md")
TOP3 = 0.50671


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def row_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def validate_score(value: float) -> None:
    if not math.isfinite(value) or value < 0.0 or value > 1.0:
        raise SystemExit(
            f"Invalid --score: expected a decimal private score in [0, 1], got {value!r}. "
            "Use values like 0.47119, not 47.119."
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the score-report template for the current upload.")
    parser.add_argument("--score", type=float, default=None, help="Optional real private score to validate/classify.")
    args = parser.parse_args()
    if args.score is not None:
        validate_score(args.score)
    return args


def build_payload(score: float | None) -> dict[str, Any]:
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    upload_sha = sha256(UPLOAD)
    rows = row_count(UPLOAD)
    score_status = "not_provided"
    if score is not None:
        score_status = "top3_completion_candidate" if score > TOP3 else "continue_routing_required"
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "upload_path": str(UPLOAD),
        "absolute_upload_path": str(UPLOAD.resolve()),
        "candidate": metadata.get("candidate", ""),
        "group": metadata.get("group", ""),
        "order": str(metadata.get("order", "")),
        "rows": rows,
        "sha256": upload_sha,
        "metadata_sha256": metadata.get("sha256", ""),
        "sha_matches_metadata": upload_sha == metadata.get("sha256"),
        "records_exists": RECORDS.exists(),
        "top3_threshold": TOP3,
        "score": None if score is None else f"{score:.5f}",
        "score_status": score_status,
        "dry_run_command": "python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>",
        "confirm_command": "python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE> --confirm-real-score",
    }


def write_outputs(payload: dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    score_field = payload["score"] if payload["score"] is not None else "<REAL_PRIVATE_SCORE_DECIMAL>"
    lines = [
        "# v1893 Score Report Template",
        "",
        f"Generated UTC: `{payload['generated_at_utc']}`",
        "",
        "## Upload context to report back",
        "",
        "```text",
        "SCORE_REPORT",
        f"uploaded_path={payload['upload_path']}",
        f"candidate={payload['candidate']}",
        f"group={payload['group']}",
        f"order={payload['order']}",
        f"sha256={payload['sha256']}",
        f"rows={payload['rows']}",
        f"real_private_score={score_field}",
        "score_is_real_kaggle_private=yes",
        "```",
        "",
        "## Current validation",
        "",
        f"- SHA matches metadata: `{payload['sha_matches_metadata']}`",
        f"- Official score records already exist: `{payload['records_exists']}`",
        f"- Stop threshold: `>{payload['top3_threshold']:.5f}`",
        f"- Provided score status: `{payload['score_status']}`",
        "",
        "## Commands after score appears",
        "",
        "Dry-run first:",
        "",
        "```bash",
        payload["dry_run_command"],
        "```",
        "",
        "Validate the pasted block first if you saved it to a file:",
        "",
        "```bash",
        "python3 experiments/scripts/v1894_score_report_intake.py <SCORE_REPORT_FILE>",
        "```",
        "",
        "Then record only after confirming the score is real:",
        "",
        "```bash",
        payload["confirm_command"],
        "```",
        "",
        "## Completion boundary",
        "",
        "This template only structures the score report. The active goal is complete only after a real private score greater than `0.50671` is recorded.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    payload = build_payload(args.score)
    write_outputs(payload)
    print("SCORE_REPORT_TEMPLATE")
    print(f"UPLOAD_PATH={payload['upload_path']}")
    print(f"CANDIDATE={payload['candidate']}")
    print(f"GROUP={payload['group']}")
    print(f"ORDER={payload['order']}")
    print(f"ROWS={payload['rows']}")
    print(f"SHA256={payload['sha256']}")
    print(f"SHA_MATCHES_METADATA={'yes' if payload['sha_matches_metadata'] else 'no'}")
    print(f"RECORDS_EXISTS={'yes' if payload['records_exists'] else 'no'}")
    print(f"SCORE_STATUS={payload['score_status']}")
    print(f"REPORT={OUT_MD}")
    print(f"JSON={OUT_JSON}")
    if not payload["sha_matches_metadata"]:
        raise SystemExit("upload SHA does not match metadata")


if __name__ == "__main__":
    main()
