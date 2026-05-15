#!/usr/bin/env python3
"""Validate a SCORE_REPORT file and pass its score to the command center."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INTAKE = Path("experiments/scripts/v1894_score_report_intake.py")
COMMAND_CENTER = Path("experiments/scripts/v1872_post_score_command_center.py")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
RECORDS_MD = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.md")
OUT_JSON = Path("experiments/reports/v1895_score_report_command_center.json")
OUT_MD = Path("experiments/reports/v1895_score_report_command_center.md")


def file_state(path: Path) -> str:
    if not path.exists():
        return "missing"
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    return f"present:{h}"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate SCORE_REPORT and run the post-score command center.")
    parser.add_argument("report", type=Path)
    parser.add_argument("--confirm-real-score", action="store_true", help="Write the score record after validation.")
    parser.add_argument("--skip-stage", action="store_true", help="Pass --skip-stage to the command center.")
    parser.add_argument("--out-json", type=Path, default=OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    return parser.parse_args()


def write_outputs(payload: dict[str, Any], out_json: Path, out_md: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v1895 Score Report Command Center",
        "",
        f"Generated UTC: `{payload['generated_at_utc']}`",
        "",
        "## Summary",
        "",
        f"- Intake ready: `{payload['intake_ready']}`",
        f"- Score: `{payload['score']}`",
        f"- Score status: `{payload['score_status']}`",
        f"- Write mode: `{payload['write_mode']}`",
        f"- Command-center exit code: `{payload['command_center_exit_code']}`",
        f"- Official records mutated: `{payload['official_records_mutated']}`",
        "",
        "## Command",
        "",
        "```bash",
        payload["command_center_command"],
        "```",
        "",
        "## Command-center output",
        "",
        "```text",
        payload["command_center_output"],
        "```",
        "",
        "## Completion boundary",
        "",
        "This bridge validates and routes a score report. The active goal is complete only after a real private score greater than `0.52380` is recorded.",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    before_state = {"csv": file_state(RECORDS), "md": file_state(RECORDS_MD)}
    with tempfile.TemporaryDirectory(prefix="v1895_intake_") as tmp:
        tmpdir = Path(tmp)
        intake_json = tmpdir / "intake.json"
        intake_md = tmpdir / "intake.md"
        intake_cmd = [sys.executable, str(INTAKE), str(args.report), "--out-json", str(intake_json), "--out-md", str(intake_md)]
        intake = run(intake_cmd)
        intake_output = (intake.stdout + intake.stderr).strip()
        if intake.returncode != 0:
            payload = {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "intake_ready": "no",
                "score": "",
                "score_status": "intake_failed",
                "write_mode": "confirmed" if args.confirm_real_score else "dry_run",
                "command_center_command": "not_run",
                "command_center_exit_code": intake.returncode,
                "command_center_output": intake_output,
                "official_records_mutated": "no",
            }
            write_outputs(payload, args.out_json, args.out_md)
            print("SCORE_REPORT_COMMAND_CENTER")
            print("INTAKE_READY=no")
            print(f"REPORT={args.out_md}")
            print(f"JSON={args.out_json}")
            raise SystemExit(intake_output)
        intake_payload = json.loads(intake_json.read_text(encoding="utf-8"))

    score = str(intake_payload["score"])
    cmd = [sys.executable, str(COMMAND_CENTER), "--score", score]
    if args.confirm_real_score:
        cmd.append("--confirm-real-score")
    if args.skip_stage:
        cmd.append("--skip-stage")
    center = run(cmd)
    output = (center.stdout + center.stderr).strip()
    after_state = {"csv": file_state(RECORDS), "md": file_state(RECORDS_MD)}
    mutated = before_state != after_state
    if not args.confirm_real_score and mutated:
        raise SystemExit("dry-run command center mutated official records")

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "intake_ready": intake_payload.get("ready_for_command_center", "no"),
        "score": score,
        "score_status": intake_payload.get("score_status", ""),
        "write_mode": "confirmed" if args.confirm_real_score else "dry_run",
        "command_center_command": " ".join(cmd),
        "command_center_exit_code": center.returncode,
        "command_center_output": output,
        "official_records_before": before_state,
        "official_records_after": after_state,
        "official_records_mutated": "yes" if mutated else "no",
    }
    write_outputs(payload, args.out_json, args.out_md)

    print("SCORE_REPORT_COMMAND_CENTER")
    print(f"INTAKE_READY={payload['intake_ready']}")
    print(f"SCORE={score}")
    print(f"SCORE_STATUS={payload['score_status']}")
    print(f"WRITE_MODE={payload['write_mode']}")
    print(f"COMMAND_CENTER_EXIT_CODE={center.returncode}")
    print(f"OFFICIAL_RECORDS_MUTATED={payload['official_records_mutated']}")
    print(f"REPORT={args.out_md}")
    print(f"JSON={args.out_json}")
    if center.returncode != 0:
        raise SystemExit(output)


if __name__ == "__main__":
    main()
