#!/usr/bin/env python3
"""Safely run the post-score final-attempt workflow."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

MANIFEST = Path("experiments/final_submission_package/manifests/final_submission_pack_manifest.csv")
ROUTER = Path("experiments/scripts/v1836_score_feedback_router.py")
BUDGET = Path("experiments/scripts/v1869_attempt_budget_guard.py")
RUNBOOK = Path("experiments/scripts/v1866_final_attempt_runbook.py")
STAGER = Path("experiments/scripts/v1870_stage_current_upload.py")
COCKPIT = Path("experiments/scripts/v1871_final_attempt_cockpit.py")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
METADATA = Path("experiments/final_submission_package/current_upload/metadata.json")
DEFAULT_GROUP = "scoreonly_safe_queue"
DEFAULT_ORDER = 1
TOP3 = 0.50671


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if check and proc.returncode != 0:
        raise SystemExit((proc.stdout + proc.stderr).strip())
    return proc


def print_block(title: str, content: str) -> None:
    print(title)
    text = content.strip()
    if text:
        print(text)


def recommended_next(router_output: str) -> str:
    for line in router_output.splitlines():
        if line.startswith("recommended_next="):
            return line.split("=", 1)[1].strip()
    return ""


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def row_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def validate_recommended_next(recommendation: str) -> str:
    if not recommendation:
        return "fail_missing_recommended_next"
    if not recommendation.endswith(".csv"):
        return "non_concrete_ok"
    if not MANIFEST.exists():
        return f"fail_manifest_missing:{MANIFEST}"

    target = str(Path(recommendation))
    rows = read_csv_rows(MANIFEST)
    row = next((item for item in rows if str(Path(item.get("output_path", ""))) == target), None)
    if row is None:
        return "fail_not_in_manifest"

    path = Path(row["output_path"])
    if not path.exists():
        return "fail_missing_file"
    rows_count = row_count(path)
    if rows_count != 397:
        return f"fail_bad_row_count:{rows_count}"
    actual_sha = sha256(path)
    if row.get("sha256") and actual_sha != row["sha256"]:
        return "fail_hash_mismatch"
    if row.get("validation_status") != "pass":
        return f"fail_manifest_status_{row.get('validation_status')}"
    return f"concrete_ok:{row['group']}#{row['order']}:{row['candidate']}"


def read_current_upload_metadata(path: Path) -> dict[str, str] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"metadata is not an object: {path}")
    return {str(k): str(v) for k, v in data.items()}


def resolve_upload_context(args: argparse.Namespace) -> tuple[str, int, str]:
    if (args.group is None) != (args.order is None):
        raise SystemExit("Pass both --group and --order, or neither to use current_upload/metadata.json.")
    if args.group is not None and args.order is not None:
        return args.group, args.order, "explicit_args"
    if not args.ignore_current_upload_metadata:
        metadata = read_current_upload_metadata(args.metadata)
        if metadata is not None:
            try:
                return metadata["group"], int(metadata["order"]), str(args.metadata)
            except KeyError as exc:
                raise SystemExit(f"metadata missing required key {exc}: {args.metadata}") from exc
    return DEFAULT_GROUP, DEFAULT_ORDER, "default_scoreonly_safe_queue_order1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run post-score routing, optional recording, budget, staging, and cockpit.")
    parser.add_argument("--group", default=None, help="Uploaded candidate group. Defaults to current_upload metadata.")
    parser.add_argument("--order", type=int, default=None, help="Uploaded candidate order. Defaults to current_upload metadata.")
    parser.add_argument("--score", type=float, required=True)
    parser.add_argument("--previous-score", type=float, default=None)
    parser.add_argument("--metadata", type=Path, default=METADATA)
    parser.add_argument(
        "--ignore-current-upload-metadata",
        action="store_true",
        help="Ignore current_upload metadata and fall back to scoreonly_safe_queue order 1 if group/order are omitted.",
    )
    parser.add_argument(
        "--confirm-real-score",
        action="store_true",
        help="Write the score-feedback record. Only use with a real Kaggle private score.",
    )
    parser.add_argument(
        "--skip-stage",
        action="store_true",
        help="Do not refresh current_upload/submission.csv after recording.",
    )
    return parser.parse_args()


def router_cmd(args: argparse.Namespace, *, confirm: bool) -> list[str]:
    group, order, _ = resolve_upload_context(args)
    cmd = [
        sys.executable,
        str(ROUTER),
        "--group",
        group,
        "--order",
        str(order),
        "--score",
        f"{args.score:.5f}",
    ]
    if args.previous_score is not None:
        cmd.extend(["--previous-score", f"{args.previous_score:.5f}"])
    if confirm:
        cmd.append("--confirm-real-score")
    else:
        cmd.append("--dry-run")
    return cmd


def main() -> None:
    args = parse_args()
    group, order, context_source = resolve_upload_context(args)
    print("UPLOAD_CONTEXT")
    print(f"group={group}")
    print(f"order={order}")
    print(f"source={context_source}")
    preview = run(router_cmd(args, confirm=False))
    preview_text = preview.stdout + preview.stderr
    next_path = recommended_next(preview_text)
    print_block("ROUTER_DRY_RUN", preview_text)
    next_status = validate_recommended_next(next_path)
    print(f"NEXT_PATH_STATUS={next_status}")
    if next_status.startswith("fail_"):
        raise SystemExit(f"recommended_next validation failed: {next_status}")

    if not args.confirm_real_score:
        print("WRITE_STATUS=dry_run_only")
        print("NEXT_CONFIRM_COMMAND")
        print(
            "python3 "
            f"experiments/scripts/v1872_post_score_command_center.py --group {group} --order {order} "
            f"--score {args.score:.5f} --confirm-real-score"
        )
        return

    confirmed = run(router_cmd(args, confirm=True))
    print_block("ROUTER_CONFIRMED_WRITE", confirmed.stdout + confirmed.stderr)

    budget = run([sys.executable, str(BUDGET)])
    print_block("ATTEMPT_BUDGET_AFTER_WRITE", budget.stdout + budget.stderr)

    if args.score > TOP3:
        print("STOP_STATUS=top3_hit_no_next_stage")
        cockpit = run([sys.executable, str(COCKPIT)])
        print_block("COCKPIT_AFTER_STOP", cockpit.stdout + cockpit.stderr)
        return

    if not next_path.endswith(".csv"):
        print(f"STAGE_STATUS=skipped_non_concrete_next recommended_next={next_path}")
        cockpit = run([sys.executable, str(COCKPIT)])
        print_block("COCKPIT_AFTER_MANUAL_STATE", cockpit.stdout + cockpit.stderr)
        return

    runbook = run([sys.executable, str(RUNBOOK), "--from-records"])
    print_block("NEXT_UPLOAD_RUNBOOK", runbook.stdout + runbook.stderr)

    if args.skip_stage:
        print("STAGE_STATUS=skipped_by_flag")
    else:
        staged = run([sys.executable, str(STAGER), "--from-records"])
        print_block("STAGED_NEXT_UPLOAD", staged.stdout + staged.stderr)

    cockpit = run([sys.executable, str(COCKPIT)])
    print_block("COCKPIT_REFRESHED", cockpit.stdout + cockpit.stderr)
    print(f"RECORDS_PATH={RECORDS}")


if __name__ == "__main__":
    main()
