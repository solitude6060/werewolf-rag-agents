#!/usr/bin/env python3
"""Regression-check cockpit score handoff prefers the no-edit v1898 bridge."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

COCKPIT = Path("experiments/scripts/v1871_final_attempt_cockpit.py")
CARD = Path("experiments/final_submission_package/current_upload/ATTEMPT_CARD.md")
METADATA = Path("experiments/final_submission_package/current_upload/metadata.json")
OUT_CSV = Path("experiments/reports/v1929_cockpit_noedit_bridge_regression.csv")
OUT_MD = Path("experiments/reports/v1929_cockpit_noedit_bridge_regression.md")
DRY = "python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE>"
CONFIRM = "python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE> --confirm-real-score"
FALLBACK = "python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>"


def add(rows: list[dict[str, str]], name: str, ok: bool, detail: str) -> None:
    rows.append({"name": name, "ok": "yes" if ok else "no", "detail": detail})


def main() -> None:
    proc = subprocess.run([sys.executable, str(COCKPIT), "--no-write"], text=True, capture_output=True, check=False)
    output = (proc.stdout + proc.stderr).strip()
    card = CARD.read_text(encoding="utf-8") if CARD.exists() else ""
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    fallback_confirm = (
        "python3 experiments/scripts/v1872_post_score_command_center.py "
        f"--group {metadata['group']} --order {metadata['order']} --score <REAL_SCORE> --confirm-real-score"
    )
    rows: list[dict[str, str]] = []
    add(rows, "cockpit_no_write_exit_zero", proc.returncode == 0, f"exit={proc.returncode}")
    add(rows, "no_write_output_has_v1898_dry", DRY in output, DRY)
    add(rows, "no_write_output_has_v1898_confirm", CONFIRM in output, CONFIRM)
    add(rows, "no_write_output_keeps_v1872_fallback", FALLBACK in output and fallback_confirm in output, fallback_confirm)
    add(rows, "tracked_card_has_v1898_dry", DRY in card, DRY)
    add(rows, "tracked_card_has_v1898_confirm", CONFIRM in card, CONFIRM)
    add(rows, "tracked_card_keeps_v1872_fallback", FALLBACK in card and fallback_confirm in card, fallback_confirm)
    add(rows, "card_mentions_completion_boundary", "Only a real private score greater than `0.52380`" in card, "completion boundary")

    failures = [row for row in rows if row["ok"] != "yes"]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "ok", "detail"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# v1929 Cockpit No-Edit Bridge Regression",
        "",
        "## Summary",
        "",
        f"- Failures: `{len(failures)}`",
        "",
        "## Checks",
        "",
        "| Check | OK | Detail |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        detail = row["detail"].replace("|", "\\|")
        lines.append(f"| {row['name']} | {row['ok']} | `{detail}` |")
    lines.extend(
        [
            "",
            "## Completion boundary",
            "",
            "This regression verifies cockpit handoff wording only. The active goal is complete only after a real private score greater than `0.52380` is recorded.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("V1929_COCKPIT_NOEDIT_BRIDGE_REGRESSION")
    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"FAILURES={len(failures)}")
    for failure in failures:
        print(f"FAIL={failure['name']} detail={failure['detail']}")
    if failures:
        raise SystemExit("cockpit no-edit bridge regression failed")


if __name__ == "__main__":
    main()
