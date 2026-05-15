#!/usr/bin/env python3
"""One-command guard for the fixed final-attempt upload file."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

MANIFEST = Path("experiments/final_submission_package/manifests/final_submission_pack_manifest.csv")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
CURRENT_UPLOAD = Path("experiments/final_submission_package/current_upload/submission.csv")
CURRENT_METADATA = Path("experiments/final_submission_package/current_upload/metadata.json")
VALIDATOR = Path("werewolf-project/assert/validate_submission.py")
BUDGET = Path("experiments/scripts/v1869_attempt_budget_guard.py")
COMMAND_CENTER_REGRESSION = Path("experiments/scripts/v1882_command_center_dry_run_regression.py")
ATTEMPT_STATE_GUARD = Path("experiments/scripts/v1904_attempt_state_guard.py")
OUT_JSON = Path("experiments/reports/v1883_pre_upload_guard.json")
OUT_MD = Path("experiments/reports/v1883_pre_upload_guard.md")
TOP3 = 0.50671
EXPECTED_FIRST_GROUP = "scoreonly_safe_queue"
EXPECTED_FIRST_ORDER = 1
EXPECTED_FIRST_CANDIDATE = "v1856g"
EXPECTED_SHA = "468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def row_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def find_manifest_row(rows: list[dict[str, str]], group: str, order: int) -> dict[str, str] | None:
    for row in rows:
        if row.get("group") == group and int(row.get("order", "0")) == order:
            return row
    return None


def run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def validator(path: Path) -> tuple[bool, str]:
    code, output = run([sys.executable, str(VALIDATOR), str(path)])
    return code == 0, output


def parse_budget(output: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in output.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip()
    return data


def parse_kv(output: str) -> dict[str, str]:
    return parse_budget(output)


def main() -> None:
    checks: list[dict[str, str]] = []

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append({"check": name, "ok": "yes" if ok else "no", "detail": detail})

    manifest_rows = read_rows(MANIFEST) if MANIFEST.exists() else []
    add("manifest_exists", MANIFEST.exists(), str(MANIFEST))
    add("current_upload_exists", CURRENT_UPLOAD.exists(), str(CURRENT_UPLOAD))
    add("metadata_exists", CURRENT_METADATA.exists(), str(CURRENT_METADATA))

    metadata = json.loads(CURRENT_METADATA.read_text(encoding="utf-8")) if CURRENT_METADATA.exists() else {}
    group = str(metadata.get("group", ""))
    order = int(str(metadata.get("order", "0")) or "0")
    candidate = str(metadata.get("candidate", ""))
    metadata_sha = str(metadata.get("sha256", ""))
    source_path = Path(str(metadata.get("source_path", "")))
    record_rows = read_rows(RECORDS) if RECORDS.exists() else []
    attempt_context = "followup_from_records" if record_rows else "first_upload"

    if attempt_context == "first_upload":
        add(
            "metadata_context_is_first_upload",
            group == EXPECTED_FIRST_GROUP and order == EXPECTED_FIRST_ORDER and candidate == EXPECTED_FIRST_CANDIDATE,
            f"{group}#{order}:{candidate}",
        )
    else:
        latest_recommended = record_rows[-1].get("recommended_next", "").strip()
        add("score_records_present_for_followup", True, str(len(record_rows)))
        add("latest_recommended_next_is_csv", latest_recommended.endswith(".csv"), latest_recommended)
        attempt_code, attempt_output = run([sys.executable, str(ATTEMPT_STATE_GUARD)])
        attempt_state = parse_kv(attempt_output)
        add(
            "attempt_state_guard_ready",
            attempt_code == 0 and attempt_state.get("ATTEMPT_STATE_READY") == "yes",
            attempt_output.replace("\n", "; "),
        )

    row = find_manifest_row(manifest_rows, group, order) if manifest_rows else None
    add("manifest_row_found", row is not None, f"{group}#{order}")
    if row is not None:
        add("manifest_candidate_matches", row.get("candidate") == candidate, str(row.get("candidate", "")))
        add("manifest_status_pass", row.get("validation_status") == "pass", str(row.get("validation_status", "")))
        add("metadata_source_matches_manifest", str(Path(row.get("output_path", ""))) == str(source_path), str(source_path))

    source_exists = source_path.exists()
    add("source_exists", source_exists, str(source_path))

    upload_sha = sha256(CURRENT_UPLOAD) if CURRENT_UPLOAD.exists() else ""
    upload_rows = row_count(CURRENT_UPLOAD) if CURRENT_UPLOAD.exists() else -1
    add("current_upload_rows_397", upload_rows == 397, str(upload_rows))
    if attempt_context == "first_upload":
        add("current_upload_sha_matches_expected", upload_sha == EXPECTED_SHA, upload_sha)
    add("current_upload_sha_matches_metadata", upload_sha == metadata_sha, f"upload={upload_sha} metadata={metadata_sha}")
    if row is not None:
        add("current_upload_sha_matches_manifest", upload_sha == row.get("sha256", ""), f"upload={upload_sha} manifest={row.get('sha256', '')}")
    if source_exists:
        source_sha = sha256(source_path)
        add("current_upload_sha_matches_source", upload_sha == source_sha, f"upload={upload_sha} source={source_sha}")

    valid_ok, valid_output = validator(CURRENT_UPLOAD) if CURRENT_UPLOAD.exists() else (False, "missing upload")
    add("validator_ok", valid_ok, valid_output)

    if attempt_context == "first_upload":
        add("score_records_absent_for_first_upload", not record_rows, str(RECORDS))

    budget_code, budget_output = run([sys.executable, str(BUDGET)])
    budget = parse_budget(budget_output)
    add("attempt_budget_command_ok", budget_code == 0, budget_output.replace("\n", "; "))
    if attempt_context == "first_upload":
        add("attempts_remaining_5", budget.get("attempts_remaining") == "5", str(budget.get("attempts_remaining", "")))
    else:
        try:
            attempts_remaining = int(budget.get("attempts_remaining", "0"))
        except ValueError:
            attempts_remaining = 0
        add("attempts_remaining_positive", attempts_remaining > 0, str(budget.get("attempts_remaining", "")))
    add("top3_not_already_hit", budget.get("top3_hit") == "no", str(budget.get("top3_hit", "")))

    regression_code, regression_output = run([sys.executable, str(COMMAND_CENTER_REGRESSION)])
    add("command_center_regression_ok", regression_code == 0 and "FAILURES=0" in regression_output and "MUTATION_OK=yes" in regression_output, regression_output.replace("\n", "; "))

    ready = all(item["ok"] == "yes" for item in checks)
    result = {
        "upload_ready": ready,
        "upload_path": str(CURRENT_UPLOAD),
        "attempt_context": attempt_context,
        "candidate": candidate,
        "group": group,
        "order": order,
        "sha256": upload_sha,
        "rows": upload_rows,
        "stop_if_score_greater_than": TOP3,
        "checks": checks,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# v1883 Pre-Upload Guard",
        "",
        "Date: 2026-05-15",
        "",
        "## Summary",
        "",
        f"- Upload ready: `{'yes' if ready else 'no'}`",
        f"- Attempt context: `{attempt_context}`",
        f"- Upload path: `{CURRENT_UPLOAD}`",
        f"- Candidate: `{group}` order `{order}` (`{candidate}`)",
        f"- SHA-256: `{upload_sha}`",
        f"- Rows: `{upload_rows}`",
        f"- Stop if real score is greater than: `{TOP3:.5f}`",
        "",
        "## Checks",
        "",
        "| Check | OK | Detail |",
        "| --- | --- | --- |",
    ]
    for item in checks:
        detail = item["detail"].replace("|", "\\|")
        lines.append(f"| {item['check']} | {item['ok']} | `{detail}` |")
    lines.extend(
        [
            "",
            "## Upload instruction",
            "",
            "Upload exactly this file:",
            "",
            "```text",
            str(CURRENT_UPLOAD),
            "```",
            "",
            "After the real private score appears, run:",
            "",
            "```bash",
            "python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>",
            "```",
            "",
            "## Completion boundary",
            "",
            "This guard only proves the upload file is ready.  The active score goal still requires a real Kaggle private score greater than `0.50671`.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("PRE_UPLOAD_GUARD")
    print(f"UPLOAD_READY={'yes' if ready else 'no'}")
    print(f"ATTEMPT_CONTEXT={attempt_context}")
    print(f"UPLOAD_PATH={CURRENT_UPLOAD}")
    print(f"CANDIDATE={candidate}")
    print(f"GROUP={group}")
    print(f"ORDER={order}")
    print(f"SHA256={upload_sha}")
    print(f"ROWS={upload_rows}")
    print(f"REPORT={OUT_MD}")
    print(f"JSON={OUT_JSON}")
    if not ready:
        failed = [item for item in checks if item["ok"] != "yes"]
        for item in failed:
            print(f"FAILED_CHECK={item['check']} detail={item['detail']}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
