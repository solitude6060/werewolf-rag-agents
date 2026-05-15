#!/usr/bin/env python3
"""Fill the current SCORE_REPORT template with a score and run the v1895 bridge."""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TEMPLATE = Path("experiments/final_submission_package/current_upload/SCORE_REPORT.txt")
BRIDGE = Path("experiments/scripts/v1895_score_report_command_center.py")
OUT_JSON = Path("experiments/reports/v1898_current_score_report_bridge.json")
OUT_MD = Path("experiments/reports/v1898_current_score_report_bridge.md")
PLACEHOLDER = "<REAL_PRIVATE_SCORE_DECIMAL>"


def parse_score(text: str) -> float:
    try:
        score = float(text)
    except ValueError as exc:
        raise SystemExit(f"Invalid --score: not a number: {text!r}") from exc
    if not math.isfinite(score) or score < 0.0 or score > 1.0:
        raise SystemExit(
            f"Invalid --score: expected decimal score in [0, 1], got {text!r}. "
            "Use values like 0.47119, not 47.119."
        )
    return score


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fill current SCORE_REPORT.txt and run the v1895 score bridge.")
    parser.add_argument("--score", required=True, help="Real Kaggle private score as a decimal in [0, 1].")
    parser.add_argument("--template", type=Path, default=TEMPLATE)
    parser.add_argument("--confirm-real-score", action="store_true", help="Pass confirmation to v1895/v1872 record path.")
    parser.add_argument("--skip-stage", action="store_true", help="Pass --skip-stage to v1895/v1872.")
    parser.add_argument("--out-json", type=Path, default=OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    parser.add_argument("--filled-report", type=Path, default=None, help="Optional path for the filled SCORE_REPORT.")
    args = parser.parse_args()
    args.score_value = parse_score(args.score)
    return args


def fill_template(template: Path, score: float) -> str:
    if not template.exists():
        raise SystemExit(f"SCORE_REPORT template not found: {template}")
    text = template.read_text(encoding="utf-8")
    if PLACEHOLDER not in text:
        raise SystemExit(f"SCORE_REPORT template is missing placeholder {PLACEHOLDER!r}: {template}")
    return text.replace(PLACEHOLDER, f"{score:.5f}")


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def write_summary(payload: dict[str, Any], out_json: Path, out_md: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v1898 Current Score Report Bridge",
        "",
        f"Generated UTC: `{payload['generated_at_utc']}`",
        "",
        "## Summary",
        "",
        f"- Template: `{payload['template']}`",
        f"- Score: `{payload['score']}`",
        f"- Write mode: `{payload['write_mode']}`",
        f"- Synthetic dry-run score only: `{'yes' if payload['write_mode'] == 'dry_run' else 'no'}`",
        f"- Bridge exit code: `{payload['bridge_exit_code']}`",
        f"- Filled report persisted: `{payload['filled_report_persisted']}`",
        "",
        "## Bridge command",
        "",
        "```bash",
        payload["bridge_command"],
        "```",
        "",
        "## Bridge output",
        "",
        "```text",
        payload["bridge_output"],
        "```",
        "",
        "## v1895 report",
        "",
        payload["bridge_report"],
        "",
        "## Completion boundary",
        "",
        "This wrapper only reduces score-entry handling risk. The active goal is complete only after a real private score greater than `0.52380` is recorded.",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    filled_text = fill_template(args.template, args.score_value)
    with tempfile.TemporaryDirectory(prefix="v1898_score_report_") as tmp:
        if args.filled_report is None:
            report_path = Path(tmp) / "SCORE_REPORT.txt"
            persisted = "no"
        else:
            report_path = args.filled_report
            report_path.parent.mkdir(parents=True, exist_ok=True)
            persisted = "yes"
        report_path.write_text(filled_text, encoding="utf-8")

        bridge_json = Path(tmp) / "v1895_bridge.json"
        bridge_md = Path(tmp) / "v1895_bridge.md"
        bridge_cmd = [
            sys.executable,
            str(BRIDGE),
            str(report_path),
            "--out-json",
            str(bridge_json),
            "--out-md",
            str(bridge_md),
        ]
        if args.confirm_real_score:
            bridge_cmd.append("--confirm-real-score")
        if args.skip_stage:
            bridge_cmd.append("--skip-stage")
        bridge = run(bridge_cmd)
        bridge_output = (bridge.stdout + bridge.stderr).strip()
        bridge_report = bridge_md.read_text(encoding="utf-8") if bridge_md.exists() else ""

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "template": str(args.template),
        "score": f"{args.score_value:.5f}",
        "write_mode": "confirmed" if args.confirm_real_score else "dry_run",
        "bridge_command": " ".join(bridge_cmd),
        "bridge_exit_code": bridge.returncode,
        "bridge_output": bridge_output,
        "bridge_report": bridge_report,
        "filled_report_persisted": persisted,
    }
    write_summary(payload, args.out_json, args.out_md)

    print("CURRENT_SCORE_REPORT_BRIDGE")
    print(f"TEMPLATE={args.template}")
    print(f"SCORE={args.score_value:.5f}")
    print(f"WRITE_MODE={payload['write_mode']}")
    print(f"BRIDGE_EXIT_CODE={bridge.returncode}")
    print(f"FILLED_REPORT_PERSISTED={persisted}")
    print(f"REPORT={args.out_md}")
    print(f"JSON={args.out_json}")
    if bridge_output:
        print("BRIDGE_OUTPUT_BEGIN")
        print(bridge_output)
        print("BRIDGE_OUTPUT_END")
    if bridge.returncode != 0:
        raise SystemExit(bridge_output)


if __name__ == "__main__":
    main()
