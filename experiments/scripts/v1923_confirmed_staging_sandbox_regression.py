#!/usr/bin/env python3
"""Sandbox-regression confirmed v1826a score recording and next-upload staging."""
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
SCRIPT = Path("experiments/scripts/v1872_post_score_command_center.py")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
CURRENT_UPLOAD = Path("experiments/final_submission_package/current_upload/submission.csv")
CURRENT_METADATA = Path("experiments/final_submission_package/current_upload/metadata.json")
MANIFEST = Path("experiments/final_submission_package/manifests/final_submission_pack_manifest.csv")
OUT_CSV = Path("experiments/reports/v1923_confirmed_staging_sandbox_regression.csv")
OUT_MD = Path("experiments/reports/v1923_confirmed_staging_sandbox_regression.md")
EXPECTED_V1826A_SHA = "e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad"
EXPECTED_V1826B_PATH = "experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv"
EXPECTED_TOP3 = "0.52380"


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


def manifest_row(tmpdir: Path, *, candidate: str) -> dict[str, str]:
    rows = read_csv(tmpdir / MANIFEST)
    matches = [row for row in rows if row.get("candidate") == candidate]
    if len(matches) != 1:
        raise AssertionError(f"candidate manifest lookup failed: {candidate} matches={len(matches)}")
    return matches[0]


def run_confirm(tmpdir: Path, score: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--group", "queue", "--order", "1", "--score", score, "--confirm-real-score"],
        cwd=tmpdir,
        text=True,
        capture_output=True,
        check=False,
    )


def run_scenario(score: str, label: str) -> dict[str, str]:
    with tempfile.TemporaryDirectory(prefix=f"v1923_{label}_") as raw_tmp:
        tmpdir = Path(raw_tmp)
        copy_fixture(tmpdir)
        before_records = read_csv(tmpdir / RECORDS)
        before_upload_sha = sha256(tmpdir / CURRENT_UPLOAD)
        proc = run_confirm(tmpdir, score)
        output = (proc.stdout + proc.stderr).strip()
        after_records = read_csv(tmpdir / RECORDS)
        after_upload_sha = sha256(tmpdir / CURRENT_UPLOAD)
        after_metadata = json.loads((tmpdir / CURRENT_METADATA).read_text(encoding="utf-8"))
        latest = after_records[-1] if after_records else {}

        v1826b = manifest_row(tmpdir, candidate="v1826b")
        v1826b_sha = v1826b["sha256"]
        aliases = [Path(path) for path in after_metadata.get("upload_aliases", [])]
        alias_matches = [sha256(tmpdir / alias) == after_upload_sha for alias in aliases]

        if label == "continue_to_v1826b":
            checks = {
                "exit_zero": proc.returncode == 0,
                "record_appended": len(after_records) == len(before_records) + 1,
                "latest_record_current_candidate": latest.get("candidate") == "v1826a",
                "latest_record_top3_no": latest.get("top3_hit") == "no",
                "latest_recommends_v1826b": latest.get("recommended_next") == EXPECTED_V1826B_PATH,
                "staged_candidate_v1826b": str(after_metadata.get("candidate")) == "v1826b",
                "staged_sha_v1826b": after_upload_sha == v1826b_sha,
                "aliases_match_staged": bool(aliases) and all(alias_matches),
                "output_reports_staged_upload": "STAGED_NEXT_UPLOAD" in output and "candidate=v1826b" in output,
            }
            expected_next = EXPECTED_V1826B_PATH
        else:
            checks = {
                "exit_zero": proc.returncode == 0,
                "record_appended": len(after_records) == len(before_records) + 1,
                "latest_record_current_candidate": latest.get("candidate") == "v1826a",
                "latest_record_top3_yes": latest.get("top3_hit") == "yes",
                "latest_recommends_stop": latest.get("recommended_next") == "STOP: score exceeds top-3 threshold.",
                "staged_upload_unchanged": after_upload_sha == before_upload_sha == EXPECTED_V1826A_SHA,
                "metadata_still_v1826a": str(after_metadata.get("candidate")) == "v1826a",
                "output_reports_stop": "STOP_STATUS=top3_hit_no_next_stage" in output,
                "output_uses_live_threshold": EXPECTED_TOP3 in output,
            }
            expected_next = "STOP: score exceeds top-3 threshold."

        failures = [name for name, ok in checks.items() if not ok]
        return {
            "label": label,
            "score": score,
            "exit_code": str(proc.returncode),
            "records_before": str(len(before_records)),
            "records_after": str(len(after_records)),
            "latest_candidate": latest.get("candidate", ""),
            "latest_top3_hit": latest.get("top3_hit", ""),
            "expected_next": expected_next,
            "actual_next": latest.get("recommended_next", ""),
            "metadata_candidate": str(after_metadata.get("candidate", "")),
            "upload_sha_before": before_upload_sha,
            "upload_sha_after": after_upload_sha,
            "failure_count": str(len(failures)),
            "failures": ";".join(failures),
            "pass": "yes" if not failures else "no",
            "output_excerpt": output.replace("\n", "\\n")[:1200],
        }


def main() -> None:
    before_real = {"records_sha": sha256(REPO_ROOT / RECORDS), "upload_sha": sha256(REPO_ROOT / CURRENT_UPLOAD)}
    rows = [
        run_scenario("0.50000", "continue_to_v1826b"),
        run_scenario("0.52381", "top3_stop_no_stage"),
    ]
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
        "expected_next",
        "actual_next",
        "metadata_candidate",
        "upload_sha_before",
        "upload_sha_after",
        "failure_count",
        "failures",
        "pass",
        "output_excerpt",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# v1923 Confirmed Staging Sandbox Regression",
        "",
        "## Summary",
        "",
        f"- Scenarios checked: `{len(rows)}`",
        f"- Failures: `{len(failures)}`",
        f"- Real repo unchanged: `{'yes' if real_repo_unchanged else 'no'}`",
        "",
        "## Matrix",
        "",
        "| Label | Score | Latest top3 | Expected next | Metadata candidate | Pass |",
        "| --- | ---: | --- | --- | --- | --- |",
    ]
    for row in rows:
        expected_next = row["expected_next"].replace("|", "\\|")
        lines.append(
            f"| {row['label']} | `{row['score']}` | {row['latest_top3_hit']} | `{expected_next}` | `{row['metadata_candidate']}` | {row['pass']} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "The confirmed post-score command path records the current v1826a score and, when below the top-3 cutoff, stages the router-recommended next CSV in an isolated sandbox. A strict top-3 hit records the score and does not stage a next upload.",
            "",
            "## Completion boundary",
            "",
            "This sandbox does not prove a real leaderboard score. The active goal remains incomplete until a real private score greater than `0.52380` is recorded in the official ledger.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("V1923_CONFIRMED_STAGING_SANDBOX_REGRESSION")
    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"SCENARIOS={len(rows)}")
    print(f"FAILURES={len(failures)}")
    print(f"REAL_REPO_UNCHANGED={'yes' if real_repo_unchanged else 'no'}")
    for failure in failures:
        print(f"FAIL={failure.get('label', 'unknown')}")
    if failures:
        raise SystemExit("confirmed staging sandbox regression failed")


if __name__ == "__main__":
    main()
