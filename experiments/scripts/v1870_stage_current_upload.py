#!/usr/bin/env python3
"""Stage the current recommended final-attempt CSV as current_upload/submission.csv."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MANIFEST = Path("experiments/final_submission_package/manifests/final_submission_pack_manifest.csv")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
OUT_DIR = Path("experiments/final_submission_package/current_upload")
VALIDATOR = Path("werewolf-project/assert/validate_submission.py")
ROUTER = Path("experiments/scripts/v1836_score_feedback_router.py")
DEFAULT_GROUP = "scoreonly_safe_queue"
DEFAULT_ORDER = 1
TOP3 = 0.50671


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_manifest(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"manifest not found: {path}")
    return read_csv_rows(path)


def find_row(rows: list[dict[str, str]], group: str, order: int) -> dict[str, str]:
    for row in rows:
        if row.get("group") == group and int(row.get("order", "0")) == order:
            return row
    raise SystemExit(f"manifest row not found: {group} order {order}")


def find_row_by_output_path(rows: list[dict[str, str]], path: str) -> dict[str, str]:
    target = str(Path(path))
    for row in rows:
        if str(Path(row.get("output_path", ""))) == target:
            return row
    raise SystemExit(f"path not found in manifest: {path}")


def latest_recommended_row(rows: list[dict[str, str]], records_path: Path) -> dict[str, str] | None:
    if not records_path.exists():
        return None
    records = read_csv_rows(records_path)
    if not records:
        return None
    recommended = records[-1].get("recommended_next", "").strip()
    if not recommended or not recommended.endswith(".csv"):
        raise SystemExit(f"latest recommended_next is not a concrete CSV path: {recommended}")
    return find_row_by_output_path(rows, recommended)


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stage current recommended upload as current_upload/submission.csv")
    parser.add_argument("--group", default=DEFAULT_GROUP)
    parser.add_argument("--order", type=int, default=DEFAULT_ORDER)
    parser.add_argument("--from-records", action="store_true")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--records", type=Path, default=RECORDS)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_manifest(args.manifest)
    row = latest_recommended_row(rows, args.records) if args.from_records else find_row(rows, args.group, args.order)
    source = Path(row["output_path"])
    if not source.exists():
        raise SystemExit(f"source missing: {source}")
    source_sha = sha256(source)
    if row.get("sha256") and source_sha != row["sha256"]:
        raise SystemExit(f"source hash mismatch: manifest={row['sha256']} actual={source_sha}")
    row_count = count_rows(source)
    if row_count != 397:
        raise SystemExit(f"unexpected source row count: {row_count}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    staged = args.out_dir / "submission.csv"
    shutil.copyfile(source, staged)
    staged_sha = sha256(staged)
    if staged_sha != source_sha:
        raise SystemExit("staged hash differs from source hash")
    validation = validate(staged)
    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_path": str(source),
        "staged_path": str(staged),
        "group": row["group"],
        "order": row["order"],
        "candidate": row["candidate"],
        "rows": row_count,
        "sha256": staged_sha,
        "validator": validation,
        "post_score_command": f"python3 {ROUTER} --group {row['group']} --order {row['order']} --score <REAL_SCORE> --dry-run",
        "stop_if_score_greater_than": TOP3,
    }
    (args.out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    readme = [
        "# Current Upload Staging",
        "",
        "Upload this CSV to Kaggle:",
        "",
        "```text",
        str(staged),
        "```",
        "",
        f"Source: `{source}`",
        f"Candidate: `{row['candidate']}` (`{row['group']}` order `{row['order']}`)",
        f"Rows: `{row_count}`",
        f"SHA-256: `{staged_sha}`",
        f"Validator: `{validation}`",
        "",
        "After the real private score appears, run:",
        "",
        "```bash",
        metadata["post_score_command"],
        "```",
        "",
        f"Stop if the real score is greater than `{TOP3:.5f}`.",
    ]
    (args.out_dir / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
    print("STAGED_UPLOAD")
    print(f"source={source}")
    print(f"staged={staged}")
    print(f"group={row['group']}")
    print(f"order={row['order']}")
    print(f"candidate={row['candidate']}")
    print(f"rows={row_count}")
    print(f"sha256={staged_sha}")
    print(f"validator={validation}")
    print(f"metadata={args.out_dir / 'metadata.json'}")
    print(f"readme={args.out_dir / 'README.md'}")


if __name__ == "__main__":
    main()
