#!/usr/bin/env python3
"""Verify current_upload is consistent with score-feedback attempt state."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MANIFEST = Path("experiments/final_submission_package/manifests/final_submission_pack_manifest.csv")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
METADATA = Path("experiments/final_submission_package/current_upload/metadata.json")
UPLOAD = Path("experiments/final_submission_package/current_upload/submission.csv")
OUT_JSON = Path("experiments/reports/v1904_attempt_state_guard.json")
OUT_MD = Path("experiments/reports/v1904_attempt_state_guard.md")
MAX_FINAL_ATTEMPTS = 15
EXPECTED_ROWS = 397
DEFAULT_GROUP = "scoreonly_safe_queue"
DEFAULT_ORDER = "1"


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def row_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def add_check(checks: list[dict[str, str]], name: str, ok: bool, detail: str) -> None:
    checks.append({"name": name, "ok": "yes" if ok else "no", "detail": detail})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate current_upload against final-attempt score-feedback state.")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--records", type=Path, default=RECORDS)
    parser.add_argument("--metadata", type=Path, default=METADATA)
    parser.add_argument("--upload", type=Path, default=UPLOAD)
    parser.add_argument("--out-json", type=Path, default=OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    return parser.parse_args()


def manifest_row_by_output(manifest: list[dict[str, str]], output_path: str) -> dict[str, str] | None:
    target = str(Path(output_path))
    for row in manifest:
        if str(Path(row.get("output_path", ""))) == target:
            return row
    return None


def manifest_row_by_group_order(manifest: list[dict[str, str]], group: str, order: str) -> dict[str, str] | None:
    for row in manifest:
        if row.get("group") == group and row.get("order") == str(order):
            return row
    return None


def write_outputs(payload: dict[str, Any], out_json: Path, out_md: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v1904 Attempt State Guard",
        "",
        f"Generated UTC: `{payload['generated_at_utc']}`",
        "",
        "## Summary",
        "",
        f"- Attempt state ready: `{payload['attempt_state_ready']}`",
        f"- State: `{payload['state']}`",
        f"- Records count: `{payload['records_count']}`",
        f"- Recommended next: `{payload['recommended_next']}`",
        f"- Current upload source: `{payload['current_source_path']}`",
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
            "## Completion boundary",
            "",
            "This guard only verifies upload attempt-state consistency. The active goal is complete only after a real private score greater than `0.52380` is recorded.",
            "",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    checks: list[dict[str, str]] = []
    add_check(checks, "manifest_exists", args.manifest.exists(), str(args.manifest))
    add_check(checks, "metadata_exists", args.metadata.exists(), str(args.metadata))
    add_check(checks, "upload_exists", args.upload.exists(), str(args.upload))

    manifest = read_csv_rows(args.manifest)
    records = read_csv_rows(args.records)
    metadata = json.loads(args.metadata.read_text(encoding="utf-8")) if args.metadata.exists() else {}
    upload_sha = sha256(args.upload) if args.upload.exists() else ""
    upload_rows = row_count(args.upload) if args.upload.exists() else 0
    source_path = str(metadata.get("source_path", ""))
    override_reason = str(metadata.get("attempt_state_override_reason", "")).strip()
    recommended_next = records[-1].get("recommended_next", "") if records else ""
    state = "no_records_first_upload" if not records else "records_present"

    add_check(checks, "upload_rows_397", upload_rows == EXPECTED_ROWS, str(upload_rows))
    add_check(checks, "attempt_budget_not_exhausted", len(records) < MAX_FINAL_ATTEMPTS, str(len(records)))
    add_check(checks, "no_prior_top3_hit", not any(row.get("top3_hit") == "yes" for row in records), "top3_hit_present" if any(row.get("top3_hit") == "yes" for row in records) else "none")

    expected_row: dict[str, str] | None = None
    if not records:
        expected_row = manifest_row_by_group_order(manifest, DEFAULT_GROUP, DEFAULT_ORDER)
        add_check(checks, "first_upload_default_context", str(metadata.get("group", "")) == DEFAULT_GROUP and str(metadata.get("order", "")) == DEFAULT_ORDER, f"{metadata.get('group', '')}#{metadata.get('order', '')}")
        add_check(checks, "first_upload_manifest_row_found", expected_row is not None, f"{DEFAULT_GROUP}#{DEFAULT_ORDER}")
    else:
        concrete = recommended_next.endswith(".csv")
        if override_reason:
            add_check(
                checks,
                "latest_recommended_next_concrete_or_manual_override",
                True,
                f"manual_override; concrete={concrete}; recommended_next={recommended_next}",
            )
            if not concrete:
                add_check(checks, "manual_override_from_non_concrete_latest", True, recommended_next)
            expected_row = manifest_row_by_group_order(
                manifest,
                str(metadata.get("group", "")),
                str(metadata.get("order", "")),
            )
            uploaded_paths = {str(Path(row.get("uploaded_path", ""))) for row in records}
            add_check(checks, "manual_override_reason_present", True, override_reason)
            add_check(checks, "manual_override_row_found", expected_row is not None, f"{metadata.get('group', '')}#{metadata.get('order', '')}")
            if expected_row is not None:
                add_check(checks, "manual_override_not_already_uploaded", str(Path(expected_row.get("output_path", ""))) not in uploaded_paths, expected_row.get("output_path", ""))
            state = "manual_override_from_records"
        else:
            add_check(checks, "latest_recommended_next_concrete", concrete, recommended_next)
            recommended_row = manifest_row_by_output(manifest, recommended_next) if concrete else None
            add_check(checks, "latest_recommended_next_in_manifest", recommended_row is not None, recommended_next)
            if not concrete:
                state = "no_concrete_next_upload"
            expected_row = recommended_row

    if expected_row is not None:
        expected_path = expected_row.get("output_path", "")
        expected_sha = expected_row.get("sha256", "")
        add_check(checks, "current_source_matches_expected", source_path == expected_path, f"current={source_path} expected={expected_path}")
        add_check(checks, "current_group_matches_expected", str(metadata.get("group", "")) == expected_row.get("group", ""), f"current={metadata.get('group', '')} expected={expected_row.get('group', '')}")
        add_check(checks, "current_order_matches_expected", str(metadata.get("order", "")) == expected_row.get("order", ""), f"current={metadata.get('order', '')} expected={expected_row.get('order', '')}")
        add_check(checks, "current_candidate_matches_expected", str(metadata.get("candidate", "")) == expected_row.get("candidate", ""), f"current={metadata.get('candidate', '')} expected={expected_row.get('candidate', '')}")
        add_check(checks, "current_upload_sha_matches_expected", upload_sha == expected_sha, f"upload={upload_sha} expected={expected_sha}")
        add_check(checks, "metadata_sha_matches_expected", str(metadata.get("sha256", "")) == expected_sha, f"metadata={metadata.get('sha256', '')} expected={expected_sha}")
        if records and state == "records_present":
            state = "staged_latest_recommended"

    ready = all(check["ok"] == "yes" for check in checks)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "attempt_state_ready": "yes" if ready else "no",
        "state": state,
        "records_count": len(records),
        "recommended_next": recommended_next,
        "override_reason": override_reason,
        "current_source_path": source_path,
        "upload_rows": upload_rows,
        "upload_sha256": upload_sha,
        "checks": checks,
    }
    write_outputs(payload, args.out_json, args.out_md)

    print("ATTEMPT_STATE_GUARD")
    print(f"ATTEMPT_STATE_READY={'yes' if ready else 'no'}")
    print(f"STATE={state}")
    print(f"RECORDS_COUNT={len(records)}")
    print(f"RECOMMENDED_NEXT={recommended_next}")
    print(f"CURRENT_SOURCE_PATH={source_path}")
    print(f"UPLOAD_ROWS={upload_rows}")
    print(f"UPLOAD_SHA256={upload_sha}")
    print(f"REPORT={args.out_md}")
    print(f"JSON={args.out_json}")
    if not ready:
        failed = ",".join(check["name"] for check in checks if check["ok"] != "yes")
        raise SystemExit(f"attempt state guard failed: {failed}")


if __name__ == "__main__":
    main()
