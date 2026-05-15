#!/usr/bin/env python3
"""Regression-check score bridge after a v1826a low-score contingency stage."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path.cwd()
COMMAND_CENTER = Path("experiments/scripts/v1872_post_score_command_center.py")
CURRENT_BRIDGE = Path("experiments/scripts/v1898_current_score_report_bridge.py")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
CURRENT_UPLOAD = Path("experiments/final_submission_package/current_upload/submission.csv")
CURRENT_METADATA = Path("experiments/final_submission_package/current_upload/metadata.json")
OUT_CSV = Path("experiments/reports/v1927_contingency_score_bridge_regression.csv")
OUT_MD = Path("experiments/reports/v1927_contingency_score_bridge_regression.md")


def normalize_output(text: str) -> str:
    text = re.sub(r"/tmp/v1898_score_report_[^/\s`]+", "<TEMP_SCORE_REPORT_DIR>", text)
    text = re.sub(r"2026-05-15T[0-9:]+\+00:00", "<UTC_TIMESTAMP>", text)
    return text


def sha256(path: Path) -> str:
    if not path.exists():
        return "missing"
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def copy_fixture(tmpdir: Path) -> None:
    def ignore(_dir: str, names: list[str]) -> set[str]:
        return {name for name in names if name in {"__pycache__", ".pytest_cache"} or name.endswith(".pyc")}

    (tmpdir / "experiments").mkdir(parents=True, exist_ok=True)
    shutil.copytree(REPO_ROOT / "experiments/scripts", tmpdir / "experiments/scripts", ignore=ignore)
    shutil.copytree(REPO_ROOT / "experiments/final_submission_package", tmpdir / "experiments/final_submission_package", ignore=ignore)
    shutil.copytree(REPO_ROOT / "werewolf-project/assert", tmpdir / "werewolf-project/assert", ignore=ignore)
    shutil.copytree(REPO_ROOT / "werewolf-project/src", tmpdir / "werewolf-project/src", ignore=ignore)


def main() -> None:
    before_real = {"records_sha": sha256(REPO_ROOT / RECORDS), "upload_sha": sha256(REPO_ROOT / CURRENT_UPLOAD)}
    with tempfile.TemporaryDirectory(prefix="v1927_contingency_bridge_") as raw_tmp:
        tmpdir = Path(raw_tmp)
        copy_fixture(tmpdir)
        stage_proc = subprocess.run(
            [
                sys.executable,
                str(COMMAND_CENTER),
                "--group",
                "queue",
                "--order",
                "1",
                "--score",
                "0.47150",
                "--confirm-real-score",
            ],
            cwd=tmpdir,
            text=True,
            capture_output=True,
            check=False,
        )
        stage_output = (stage_proc.stdout + stage_proc.stderr).strip()
        metadata = json.loads((tmpdir / CURRENT_METADATA).read_text(encoding="utf-8"))
        staged_candidate = str(metadata.get("candidate", ""))
        staged_group = str(metadata.get("group", ""))
        bridge_proc = subprocess.run(
            [sys.executable, str(CURRENT_BRIDGE), "--score", "0.47000"],
            cwd=tmpdir,
            text=True,
            capture_output=True,
            check=False,
        )
        bridge_output = (bridge_proc.stdout + bridge_proc.stderr).strip()
        bridge_report = tmpdir / "experiments/reports/v1898_current_score_report_bridge.md"
        if bridge_report.exists():
            bridge_output += "\n" + bridge_report.read_text(encoding="utf-8")
        bridge_output = normalize_output(bridge_output)
        records_after = read_csv(tmpdir / RECORDS)
        sandbox_latest = records_after[-1] if records_after else {}

    after_real = {"records_sha": sha256(REPO_ROOT / RECORDS), "upload_sha": sha256(REPO_ROOT / CURRENT_UPLOAD)}
    checks = [
        ("stage_exit_zero", stage_proc.returncode == 0, f"exit={stage_proc.returncode}"),
        ("stage_recommends_contingency", "contingency/01_v1825c_diagnostic_neutral_private.csv" in stage_output, "v1825c recommendation"),
        ("metadata_group_contingency", staged_group == "contingency", staged_group),
        ("metadata_candidate_v1825c", staged_candidate == "v1825c", staged_candidate),
        ("bridge_exit_zero", bridge_proc.returncode == 0, f"exit={bridge_proc.returncode}; {bridge_output[:500]}"),
        ("bridge_routes_manual_review", "MANUAL_REVIEW: contingency/rollback score recorded" in bridge_output, "manual review fallback"),
        ("bridge_candidate_v1825c", "candidate=v1825c" in bridge_output, "candidate=v1825c"),
        ("official_repo_unchanged", before_real == after_real, f"before={before_real}; after={after_real}"),
        ("sandbox_latest_is_v1826a", sandbox_latest.get("candidate") == "v1826a", f"candidate={sandbox_latest.get('candidate', '')} score={sandbox_latest.get('score', '')} next={sandbox_latest.get('recommended_next', '')}"),
    ]
    rows = [
        {"name": name, "ok": "yes" if ok else "no", "detail": detail.replace("\n", "\\n")}
        for name, ok, detail in checks
    ]
    failures = [row for row in rows if row["ok"] != "yes"]

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "ok", "detail"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# v1927 Contingency Score Bridge Regression",
        "",
        "## Summary",
        "",
        f"- Failures: `{len(failures)}`",
        f"- Real repo unchanged: `{'yes' if before_real == after_real else 'no'}`",
        f"- Staged sandbox candidate after low v1826a score: `{staged_group}#{staged_candidate}`",
        f"- Bridge exit code: `{bridge_proc.returncode}`",
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
            "## Bridge output excerpt",
            "",
            "```text",
            bridge_output[:2000],
            "```",
            "",
            "## Completion boundary",
            "",
            "This regression proves the contingency score bridge path only. The active goal remains incomplete until a real private score greater than `0.52380` is recorded.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("V1927_CONTINGENCY_SCORE_BRIDGE_REGRESSION")
    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"FAILURES={len(failures)}")
    print(f"REAL_REPO_UNCHANGED={'yes' if before_real == after_real else 'no'}")
    for failure in failures:
        print(f"FAIL={failure['name']} detail={failure['detail']}")
    if failures:
        raise SystemExit("contingency score bridge regression failed")


if __name__ == "__main__":
    main()
