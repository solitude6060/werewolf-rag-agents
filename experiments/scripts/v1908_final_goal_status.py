#!/usr/bin/env python3
"""Combine completion gate and upload preflight into one final-goal status."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

COMPLETION_GATE = Path("experiments/scripts/v1906_goal_completion_gate.py")
PREFLIGHT = Path("experiments/scripts/v1888_final_upload_preflight.py")
OUT_JSON = Path("experiments/reports/v1908_final_goal_status.json")
OUT_MD = Path("experiments/reports/v1908_final_goal_status.md")


def parse_kv(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show final score-goal status from completion and upload-readiness gates.")
    parser.add_argument("--completion-gate", type=Path, default=COMPLETION_GATE)
    parser.add_argument("--preflight", type=Path, default=PREFLIGHT)
    parser.add_argument("--out-json", type=Path, default=OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    return parser.parse_args()


def write_outputs(payload: dict[str, Any], out_json: Path, out_md: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v1908 Final Goal Status",
        "",
        f"Generated UTC: `{payload['generated_at_utc']}`",
        "",
        "## Summary",
        "",
        f"- Action: `{payload['action']}`",
        f"- Goal complete: `{payload['goal_complete']}`",
        f"- Ready to manual upload: `{payload['ready_to_manual_upload']}`",
        f"- Records consistent: `{payload['records_consistent']}`",
        f"- Best score: `{payload['best_score']}`",
        f"- Upload path: `{payload['upload_path']}`",
        "",
        "## Next command",
        "",
        "```bash",
        payload["next_command"],
        "```",
        "",
        "## Completion gate output",
        "",
        "```text",
        payload["completion_output"],
        "```",
        "",
        "## Preflight output",
        "",
        "```text",
        payload["preflight_output"],
        "```",
        "",
        "## Completion boundary",
        "",
        "Only `ACTION=MARK_GOAL_COMPLETE` from this status command is sufficient local evidence to proceed to the final completion audit and `update_goal` call.",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    with tempfile.TemporaryDirectory(prefix="v1908_final_status_") as tmp:
        tmpdir = Path(tmp)
        completion_json = tmpdir / "completion.json"
        completion_md = tmpdir / "completion.md"
        preflight_json = tmpdir / "preflight.json"
        preflight_md = tmpdir / "preflight.md"
        completion = run(
            [
                sys.executable,
                str(args.completion_gate),
                "--out-json",
                str(completion_json),
                "--out-md",
                str(completion_md),
            ]
        )
        completion_output = (completion.stdout + completion.stderr).strip()
        completion_kv = parse_kv(completion_output)

        # The preflight is still useful even after completion for reporting, but
        # completion gate is the decisive action.
        preflight = run(
            [
                sys.executable,
                str(args.preflight),
                "--out-json",
                str(preflight_json),
                "--out-md",
                str(preflight_md),
            ]
        )
        preflight_output = (preflight.stdout + preflight.stderr).strip()
        preflight_kv = parse_kv(preflight_output)

    goal_complete = completion.returncode == 0 and completion_kv.get("GOAL_COMPLETE") == "yes"
    ready = preflight.returncode == 0 and preflight_kv.get("READY_TO_MANUAL_UPLOAD") == "yes"
    records_consistent = completion_kv.get("RECORDS_CONSISTENT", "no")
    best_score = completion_kv.get("BEST_SCORE", "unknown")
    upload_path = preflight_kv.get("RELATIVE_UPLOAD_PATH", "")

    if goal_complete:
        action = "MARK_GOAL_COMPLETE"
        next_command = "perform final audit, then call update_goal(status=complete)"
    elif ready:
        action = "UPLOAD_CURRENT"
        next_command = "upload experiments/final_submission_package/current_upload/submission.csv"
    else:
        action = "BLOCKED"
        next_command = "inspect v1908 report outputs and fix the failing gate before uploading"

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "action": action,
        "goal_complete": "yes" if goal_complete else "no",
        "ready_to_manual_upload": "yes" if ready else "no",
        "records_consistent": records_consistent,
        "best_score": best_score,
        "upload_path": upload_path,
        "next_command": next_command,
        "completion_exit_code": completion.returncode,
        "preflight_exit_code": preflight.returncode,
        "completion_output": completion_output,
        "preflight_output": preflight_output,
    }
    write_outputs(payload, args.out_json, args.out_md)

    print("FINAL_GOAL_STATUS")
    print(f"ACTION={action}")
    print(f"GOAL_COMPLETE={'yes' if goal_complete else 'no'}")
    print(f"READY_TO_MANUAL_UPLOAD={'yes' if ready else 'no'}")
    print(f"RECORDS_CONSISTENT={records_consistent}")
    print(f"BEST_SCORE={best_score}")
    print(f"UPLOAD_PATH={upload_path}")
    print(f"NEXT_COMMAND={next_command}")
    print(f"REPORT={args.out_md}")
    print(f"JSON={args.out_json}")
    if action == "BLOCKED":
        raise SystemExit("final goal status is blocked")


if __name__ == "__main__":
    main()
