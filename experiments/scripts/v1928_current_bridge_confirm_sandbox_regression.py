#!/usr/bin/env python3
"""Sandbox-regression the exact v1898 --confirm-real-score handoff command."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path.cwd()
BRIDGE = Path("experiments/scripts/v1898_current_score_report_bridge.py")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
CURRENT_UPLOAD = Path("experiments/final_submission_package/current_upload/submission.csv")
CURRENT_METADATA = Path("experiments/final_submission_package/current_upload/metadata.json")
MANIFEST = Path("experiments/final_submission_package/manifests/final_submission_pack_manifest.csv")
OUT_CSV = Path("experiments/reports/v1928_current_bridge_confirm_sandbox_regression.csv")
OUT_MD = Path("experiments/reports/v1928_current_bridge_confirm_sandbox_regression.md")
V1826A_SHA = "e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad"


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


def manifest_sha(tmpdir: Path, candidate: str) -> str:
    for row in read_csv(tmpdir / MANIFEST):
        if row.get("candidate") == candidate:
            return row.get("sha256", "")
    raise AssertionError(f"candidate not found in manifest: {candidate}")


def run_case(label: str, score: str) -> dict[str, str]:
    with tempfile.TemporaryDirectory(prefix=f"v1928_{label}_") as raw_tmp:
        tmpdir = Path(raw_tmp)
        copy_fixture(tmpdir)
        before_records = read_csv(tmpdir / RECORDS)
        before_upload_sha = sha256(tmpdir / CURRENT_UPLOAD)
        proc = subprocess.run(
            [sys.executable, str(BRIDGE), "--score", score, "--confirm-real-score"],
            cwd=tmpdir,
            text=True,
            capture_output=True,
            check=False,
        )
        output = (proc.stdout + proc.stderr).strip()
        bridge_report = tmpdir / "experiments/reports/v1898_current_score_report_bridge.md"
        if bridge_report.exists():
            output += "\n" + bridge_report.read_text(encoding="utf-8")
        after_records = read_csv(tmpdir / RECORDS)
        latest = after_records[-1] if after_records else {}
        metadata = json.loads((tmpdir / CURRENT_METADATA).read_text(encoding="utf-8"))
        after_upload_sha = sha256(tmpdir / CURRENT_UPLOAD)
        v1826b_sha = manifest_sha(tmpdir, "v1826b")
        aliases = [Path(path) for path in metadata.get("upload_aliases", [])]
        alias_matches = [sha256(tmpdir / alias) == after_upload_sha for alias in aliases]

        if label == "continue_to_v1826b":
            checks = {
                "exit_zero": proc.returncode == 0,
                "bridge_confirmed": "WRITE_MODE=confirmed" in output,
                "record_appended": len(after_records) == len(before_records) + 1,
                "latest_candidate_v1826a": latest.get("candidate") == "v1826a",
                "latest_top3_no": latest.get("top3_hit") == "no",
                "latest_recommends_v1826b": latest.get("recommended_next") == "experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv",
                "metadata_candidate_v1826b": metadata.get("candidate") == "v1826b",
                "upload_sha_v1826b": after_upload_sha == v1826b_sha,
                "aliases_match_staged": bool(alias_matches) and all(alias_matches),
            }
        else:
            checks = {
                "exit_zero": proc.returncode == 0,
                "bridge_confirmed": "WRITE_MODE=confirmed" in output,
                "record_appended": len(after_records) == len(before_records) + 1,
                "latest_candidate_v1826a": latest.get("candidate") == "v1826a",
                "latest_top3_yes": latest.get("top3_hit") == "yes",
                "latest_recommends_stop": latest.get("recommended_next") == "STOP: score exceeds top-3 threshold.",
                "metadata_still_v1826a": metadata.get("candidate") == "v1826a",
                "upload_sha_unchanged": after_upload_sha == before_upload_sha == V1826A_SHA,
                "stop_status_output": "STOP_STATUS=top3_hit_no_next_stage" in output,
            }
        failures = [name for name, ok in checks.items() if not ok]
        return {
            "label": label,
            "score": score,
            "exit_code": str(proc.returncode),
            "records_before": str(len(before_records)),
            "records_after": str(len(after_records)),
            "latest_candidate": latest.get("candidate", ""),
            "latest_top3_hit": latest.get("top3_hit", ""),
            "latest_next": latest.get("recommended_next", ""),
            "metadata_candidate": str(metadata.get("candidate", "")),
            "upload_sha_before": before_upload_sha,
            "upload_sha_after": after_upload_sha,
            "failure_count": str(len(failures)),
            "failures": ";".join(failures),
            "pass": "yes" if not failures else "no",
        }


def main() -> None:
    before_real = {"records_sha": sha256(REPO_ROOT / RECORDS), "upload_sha": sha256(REPO_ROOT / CURRENT_UPLOAD)}
    rows = [run_case("continue_to_v1826b", "0.50000"), run_case("top3_stop_no_stage", "0.52381")]
    after_real = {"records_sha": sha256(REPO_ROOT / RECORDS), "upload_sha": sha256(REPO_ROOT / CURRENT_UPLOAD)}
    real_repo_unchanged = before_real == after_real
    failures = [row for row in rows if row["pass"] != "yes"]
    if not real_repo_unchanged:
        failures.append({"label": "real_repo_unchanged", "pass": "no"})

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "label",
        "score",
        "exit_code",
        "records_before",
        "records_after",
        "latest_candidate",
        "latest_top3_hit",
        "latest_next",
        "metadata_candidate",
        "upload_sha_before",
        "upload_sha_after",
        "failure_count",
        "failures",
        "pass",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# v1928 Current Bridge Confirm Sandbox Regression",
        "",
        "## Summary",
        "",
        f"- Scenarios checked: `{len(rows)}`",
        f"- Failures: `{len(failures)}`",
        f"- Real repo unchanged: `{'yes' if real_repo_unchanged else 'no'}`",
        "",
        "## Matrix",
        "",
        "| Label | Score | Latest top3 | Latest next | Metadata candidate | Pass |",
        "| --- | ---: | --- | --- | --- | --- |",
    ]
    for row in rows:
        latest_next = row["latest_next"].replace("|", "\\|")
        lines.append(
            f"| {row['label']} | `{row['score']}` | {row['latest_top3_hit']} | `{latest_next}` | `{row['metadata_candidate']}` | {row['pass']} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "The exact no-edit current score bridge command can record a real score and either stage the next concrete upload or stop on a strict top-3 hit in an isolated sandbox.",
            "",
            "## Completion boundary",
            "",
            "This sandbox does not prove a real leaderboard score. The active goal remains incomplete until a real private score greater than `0.52380` is recorded in the official ledger.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("V1928_CURRENT_BRIDGE_CONFIRM_SANDBOX_REGRESSION")
    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"SCENARIOS={len(rows)}")
    print(f"FAILURES={len(failures)}")
    print(f"REAL_REPO_UNCHANGED={'yes' if real_repo_unchanged else 'no'}")
    for failure in failures:
        print(f"FAIL={failure.get('label', 'unknown')}")
    if failures:
        raise SystemExit("current bridge confirm sandbox regression failed")


if __name__ == "__main__":
    main()
