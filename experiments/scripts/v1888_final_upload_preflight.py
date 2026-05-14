#!/usr/bin/env python3
"""One-command local preflight before the manual final Kaggle upload."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UPLOAD = Path("experiments/final_submission_package/current_upload/submission.csv")
METADATA = Path("experiments/final_submission_package/current_upload/metadata.json")
MANIFEST = Path("experiments/final_submission_package/manifests/final_submission_pack_manifest.csv")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
GUARD = Path("experiments/scripts/v1883_pre_upload_guard.py")
COVERAGE = Path("experiments/scripts/v1884_candidate_pool_coverage_scan.py")
VALIDATOR = Path("werewolf-project/assert/validate_submission.py")
OUT_JSON = Path("experiments/reports/v1888_final_upload_preflight.json")
OUT_MD = Path("experiments/reports/v1888_final_upload_preflight.md")
TOP3 = 0.50671


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def parse_kv(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def add_check(checks: list[dict[str, str]], name: str, ok: bool, detail: str) -> None:
    checks.append({"name": name, "ok": "yes" if ok else "no", "detail": detail})


def manifest_match(group: str, order: str) -> dict[str, str] | None:
    if not MANIFEST.exists():
        return None
    for row in read_rows(MANIFEST):
        if row.get("group") == group and row.get("order") == str(order):
            return row
    return None


def write_outputs(payload: dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# v1888 Final Upload Preflight",
        "",
        f"Generated UTC: `{payload['generated_at_utc']}`",
        "",
        "## Summary",
        "",
        f"- Ready to manually upload: `{payload['ready_to_manual_upload']}`",
        f"- Relative upload path: `{payload['relative_upload_path']}`",
        f"- Absolute upload path: `{payload['absolute_upload_path']}`",
        f"- Candidate: `{payload['group']}` order `{payload['order']}` (`{payload['candidate']}`)",
        f"- Rows: `{payload['rows']}`",
        f"- SHA-256: `{payload['sha256']}`",
        f"- Stop threshold: `>{TOP3:.5f}`",
        "",
        "## Checks",
        "",
        "| Check | OK | Detail |",
        "| --- | --- | --- |",
    ]
    for check in payload["checks"]:
        detail = str(check["detail"]).replace("|", "\\|")
        lines.append(f"| {check['name']} | {check['ok']} | `{detail}` |")
    lines.extend(
        [
            "",
            "## Manual upload instruction",
            "",
            "Upload exactly this file in the browser:",
            "",
            "```text",
            payload["relative_upload_path"],
            "```",
            "",
            "After the real private score appears:",
            "",
            "```bash",
            "python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>",
            "python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE> --confirm-real-score",
            "```",
            "",
            "## Completion boundary",
            "",
            "This preflight only proves local upload readiness. The active objective still requires a real Kaggle private score greater than `0.50671`.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    checks: list[dict[str, str]] = []

    metadata = json.loads(METADATA.read_text(encoding="utf-8")) if METADATA.exists() else {}
    group = str(metadata.get("group", ""))
    order = str(metadata.get("order", ""))
    candidate = str(metadata.get("candidate", ""))
    expected_sha = str(metadata.get("sha256", ""))

    add_check(checks, "metadata_exists", METADATA.exists(), str(METADATA))
    add_check(checks, "current_upload_exists", UPLOAD.exists(), str(UPLOAD))

    rows: list[dict[str, str]] = []
    actual_sha = ""
    if UPLOAD.exists():
        rows = read_rows(UPLOAD)
        actual_sha = sha256(UPLOAD)
    add_check(checks, "current_upload_rows_397", len(rows) == 397, str(len(rows)))
    add_check(checks, "current_upload_sha_matches_metadata", bool(expected_sha) and actual_sha == expected_sha, actual_sha)

    row = manifest_match(group, order)
    add_check(checks, "manifest_row_found", row is not None, f"{group}#{order}:{candidate}")
    if row is not None:
        source = Path(row.get("output_path", ""))
        add_check(checks, "manifest_candidate_matches", row.get("candidate") == candidate, row.get("candidate", ""))
        add_check(checks, "manifest_status_pass", row.get("validation_status") == "pass", row.get("validation_status", ""))
        add_check(checks, "manifest_sha_matches_upload", row.get("sha256") == actual_sha, row.get("sha256", ""))
        add_check(checks, "manifest_output_exists", source.exists(), str(source))
        if source.exists():
            add_check(checks, "manifest_output_sha_matches_upload", sha256(source) == actual_sha, str(source))

    validator = run([sys.executable, str(VALIDATOR), str(UPLOAD)])
    validator_text = (validator.stdout + validator.stderr).strip()
    add_check(checks, "validator_ok", validator.returncode == 0 and "OK: 397 predictions validated" in validator_text, validator_text)

    guard = run([sys.executable, str(GUARD)])
    guard_text = (guard.stdout + guard.stderr).strip()
    guard_kv = parse_kv(guard_text)
    add_check(checks, "pre_upload_guard_ready", guard.returncode == 0 and guard_kv.get("UPLOAD_READY") == "yes", guard_text.replace("\n", "; "))

    coverage = run([sys.executable, str(COVERAGE)])
    coverage_text = (coverage.stdout + coverage.stderr).strip()
    coverage_kv = parse_kv(coverage_text)
    add_check(checks, "candidate_pool_review_zero", coverage.returncode == 0 and coverage_kv.get("REVIEW_CANDIDATES") == "0", coverage_text.replace("\n", "; "))

    add_check(checks, "score_records_absent_for_first_upload", not RECORDS.exists(), str(RECORDS))

    ready = all(check["ok"] == "yes" for check in checks)
    payload: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ready_to_manual_upload": "yes" if ready else "no",
        "relative_upload_path": str(UPLOAD),
        "absolute_upload_path": str(UPLOAD.resolve()),
        "group": group,
        "order": order,
        "candidate": candidate,
        "rows": len(rows),
        "sha256": actual_sha,
        "top3_threshold": TOP3,
        "checks": checks,
    }
    write_outputs(payload)

    print("FINAL_UPLOAD_PREFLIGHT")
    print(f"READY_TO_MANUAL_UPLOAD={'yes' if ready else 'no'}")
    print(f"RELATIVE_UPLOAD_PATH={UPLOAD}")
    print(f"ABSOLUTE_UPLOAD_PATH={UPLOAD.resolve()}")
    print(f"CANDIDATE={candidate}")
    print(f"GROUP={group}")
    print(f"ORDER={order}")
    print(f"ROWS={len(rows)}")
    print(f"SHA256={actual_sha}")
    print(f"REPORT={OUT_MD}")
    print(f"JSON={OUT_JSON}")
    if not ready:
        failed = ",".join(check["name"] for check in checks if check["ok"] != "yes")
        raise SystemExit(f"preflight failed: {failed}")


if __name__ == "__main__":
    main()
