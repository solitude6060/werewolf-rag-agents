#!/usr/bin/env python3
"""Print the next final-attempt upload path and post-score router command."""
from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import sys
from pathlib import Path

MANIFEST = Path("experiments/final_submission_package/manifests/final_submission_pack_manifest.csv")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
VALIDATOR = Path("werewolf-project/assert/validate_submission.py")
ROUTER = Path("experiments/scripts/v1836_score_feedback_router.py")
STAGED_UPLOAD = Path("experiments/final_submission_package/current_upload/submission.csv")
DEFAULT_GROUP = "scoreonly_safe_queue"
DEFAULT_ORDER = 1
TOP3 = 0.50671


def read_manifest(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"manifest not found: {path}; run v1835_final_submission_pack.py --preset full first")
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def find_row(rows: list[dict[str, str]], group: str, order: int) -> dict[str, str]:
    for row in rows:
        if row.get("group") == group and int(row.get("order", "0")) == order:
            return row
    raise SystemExit(f"manifest row not found: group={group} order={order}")


def find_row_by_output_path(rows: list[dict[str, str]], output_path: str) -> dict[str, str]:
    normalized = str(Path(output_path))
    for row in rows:
        if str(Path(row.get("output_path", ""))) == normalized:
            return row
    raise SystemExit(f"recommended_next path is not in manifest: {output_path}")


def read_latest_record(path: Path) -> dict[str, str] | None:
    if not path.exists():
        return None
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows[-1] if rows else None


def resolve_record_next(manifest_rows: list[dict[str, str]], records_path: Path) -> dict[str, str]:
    record = read_latest_record(records_path)
    if record is None:
        print(f"RECORD_STATE=no_records path={records_path}")
        return find_row(manifest_rows, DEFAULT_GROUP, DEFAULT_ORDER)
    recommended = record.get("recommended_next", "").strip()
    print("LATEST_RECORD")
    print(f"group={record.get('group', '')}")
    print(f"order={record.get('order', '')}")
    print(f"candidate={record.get('candidate', '')}")
    print(f"score={record.get('score', '')}")
    print(f"recommended_next={recommended}")
    if not recommended:
        raise SystemExit("latest record has empty recommended_next")
    if recommended.startswith("STOP"):
        print("STOP_STATE=top3_hit_or_stop_recommended")
        raise SystemExit(0)
    if recommended.startswith(("NO_", "MANUAL_", "SCOREONLY_", "PORTFOLIO_")):
        print("MANUAL_STATE=latest recommended_next is not a concrete CSV path")
        raise SystemExit(0)
    return find_row_by_output_path(manifest_rows, recommended)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def count_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def validate(path: Path) -> str:
    proc = subprocess.run([sys.executable, str(VALIDATOR), str(path)], text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise SystemExit(proc.stderr + proc.stdout)
    return proc.stdout.strip()


def matching_staged_upload(path: Path, expected_sha: str) -> Path | None:
    """Return the fixed manual-upload path when it mirrors the selected row."""
    if not STAGED_UPLOAD.exists():
        return None
    if path == STAGED_UPLOAD:
        return STAGED_UPLOAD
    if sha256(STAGED_UPLOAD) != expected_sha:
        return None
    return STAGED_UPLOAD


def router_preview(group: str, order: int, score: float, previous_score: float | None) -> str:
    cmd = [sys.executable, str(ROUTER), "--group", group, "--order", str(order), "--score", f"{score:.5f}", "--dry-run"]
    if previous_score is not None:
        cmd.extend(["--previous-score", f"{previous_score:.5f}"])
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise SystemExit(proc.stderr + proc.stdout)
    return proc.stdout.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show final-attempt upload path and router command.")
    parser.add_argument("--group", default=DEFAULT_GROUP, help="Manifest group to upload from.")
    parser.add_argument("--order", type=int, default=DEFAULT_ORDER, help="Manifest order to upload from.")
    parser.add_argument("--score", type=float, default=None, help="Optional real/private score to preview next route.")
    parser.add_argument("--previous-score", type=float, default=None, help="Previous score for order>1 router decisions.")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--records", type=Path, default=RECORDS)
    parser.add_argument("--from-records", action="store_true", help="Use latest score-feedback record's recommended_next as upload row.")
    parser.add_argument("--skip-validation", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_manifest(args.manifest)
    row = resolve_record_next(rows, args.records) if args.from_records else find_row(rows, args.group, args.order)
    path = Path(row["output_path"])
    if not path.exists():
        raise SystemExit(f"recommended file missing: {path}")
    actual_sha = sha256(path)
    manifest_sha = row.get("sha256", "")
    row_count = count_rows(path)
    if manifest_sha and actual_sha != manifest_sha:
        raise SystemExit(f"hash mismatch for {path}: manifest={manifest_sha} actual={actual_sha}")
    if row_count != 397:
        raise SystemExit(f"unexpected row count for {path}: {row_count}")
    validation_result = "skipped"
    if not args.skip_validation:
        validation_result = validate(path)

    print("NEXT_UPLOAD")
    print(f"group={row['group']}")
    print(f"order={row['order']}")
    print(f"candidate={row['candidate']}")
    print(f"path={path}")
    print(f"rows={row_count}")
    print(f"sha256={actual_sha}")
    print(f"manifest_validation_status={row.get('validation_status', '')}")
    print(f"validator={validation_result}")
    staged = matching_staged_upload(path, actual_sha)
    if staged is not None:
        print("STAGED_UPLOAD")
        print(f"path={staged}")
        print(f"sha256={actual_sha}")
    print("POST_SCORE_COMMAND")
    print(f"python3 {ROUTER} --group {row['group']} --order {row['order']} --score <REAL_SCORE> --dry-run")
    print(f"STOP_IF_SCORE_GREATER_THAN={TOP3:.5f}")
    if args.score is not None:
        print("ROUTER_PREVIEW")
        print(router_preview(row["group"], int(row["order"]), args.score, args.previous_score))


if __name__ == "__main__":
    main()
