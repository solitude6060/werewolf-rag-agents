#!/usr/bin/env python3
"""Regression checks for the stdout-only upload-now console."""
from __future__ import annotations

import subprocess
import sys

SCRIPT = "experiments/scripts/v1921_upload_now_console.py"
EXPECTED_SHA = "e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad"
EXPECTED_UPLOAD = "experiments/final_submission_package/current_upload/submission.csv"
EXPECTED_ALIASES = [
    "hw2_D13922024/submission.csv",
    "hw2_D13922024/checkpoints/final_current_private.csv",
    "hw2_D13922024/checkpoints/final_v1826a_private.csv",
]
EXPECTED_LEGACY_DO_NOT_UPLOAD = "werewolf-project/artifacts/legacy-submissions/hw2_D13922024/submission.csv"


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> None:
    result = subprocess.run([sys.executable, SCRIPT], text=True, capture_output=True, check=False)
    output = result.stdout + result.stderr
    failures: list[str] = []

    require(result.returncode == 0, f"returncode={result.returncode}: {output}", failures)
    require("READY_TO_UPLOAD=yes" in output, "missing ready flag", failures)
    require(f"UPLOAD_PATH={EXPECTED_UPLOAD}" in output, "missing canonical upload path", failures)
    require("CANDIDATE=v1826a" in output, "missing candidate", failures)
    require("GROUP=queue" in output and "ORDER=1" in output, "missing group/order", failures)
    require("ROWS=397" in output, "missing row count", failures)
    require(f"SHA256={EXPECTED_SHA}" in output, "missing sha", failures)
    require("STOP_IF_SCORE_GREATER_THAN=0.52380" in output, "missing top3 threshold", failures)
    require("GOAL_COMPLETE_BY_RECORDS=no" in output, "goal should not be complete", failures)
    require("BEST_SCORE=0.42894" in output, "missing best score", failures)
    for alias in EXPECTED_ALIASES:
        require(f"SAFE_ALIAS={alias} rows=397 sha_matches=yes exists=yes" in output, f"missing safe alias {alias}", failures)
    do_not_upload_lines = [line for line in output.splitlines() if line.startswith("DO_NOT_UPLOAD=")]
    require(len(do_not_upload_lines) >= 2, f"expected at least 2 do-not-upload warnings, got {len(do_not_upload_lines)}", failures)
    require(
        f"DO_NOT_UPLOAD={EXPECTED_LEGACY_DO_NOT_UPLOAD} rows=673 sha_matches=no" in output,
        "missing legacy do-not-upload warning",
        failures,
    )
    require(
        any(line.startswith("DO_NOT_UPLOAD=experiments/worktrees/") and "rows=673 sha_matches=no" in line for line in do_not_upload_lines),
        "missing worktree do-not-upload warning",
        failures,
    )
    require(
        "POST_SCORE_DRY_RUN_COMMAND=python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE>" in output,
        "missing post-score dry-run command",
        failures,
    )
    require(
        "POST_SCORE_CONFIRM_COMMAND=python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE> --confirm-real-score" in output,
        "missing post-score confirm command",
        failures,
    )
    require("FINAL_STATUS_COMMAND=python3 experiments/scripts/v1908_final_goal_status.py" in output, "missing final status command", failures)

    print("V1921_UPLOAD_NOW_CONSOLE_REGRESSION")
    print("SCENARIOS=1")
    print(f"FAILURES={len(failures)}")
    if failures:
        for failure in failures:
            print(f"FAIL={failure}")
        raise SystemExit(1)
    print("STDOUT_ONLY_READY=yes")


if __name__ == "__main__":
    main()
