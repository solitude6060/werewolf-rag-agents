#!/usr/bin/env python3
"""Verify likely manual upload CSV aliases match the canonical current upload."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CANONICAL = Path("experiments/final_submission_package/current_upload/submission.csv")
METADATA = Path("experiments/final_submission_package/current_upload/metadata.json")
UPLOAD_ROOT = Path("hw2_D13922024")
CHECKPOINT_DIR = UPLOAD_ROOT / "checkpoints"
DEFAULT_STATIC_ALIASES = [UPLOAD_ROOT / "submission.csv"]
OUT_JSON = Path("experiments/reports/v1902_upload_alias_guard.json")
OUT_MD = Path("experiments/reports/v1902_upload_alias_guard.md")
EXPECTED_ROWS = 397
DEFAULT_SCAN_ROOT = Path(".")


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


def default_aliases() -> list[Path]:
    aliases = list(DEFAULT_STATIC_ALIASES)
    if METADATA.exists():
        data = json.loads(METADATA.read_text(encoding="utf-8"))
        candidate = str(data.get("candidate", "")).strip()
        aliases.append(CHECKPOINT_DIR / "final_current_private.csv")
        if candidate:
            aliases.append(CHECKPOINT_DIR / f"final_{candidate}_private.csv")
    return list(dict.fromkeys(aliases))


def is_inside_git(path: Path) -> bool:
    return ".git" in path.parts


def path_key(path: Path) -> str:
    try:
        return str(path.resolve())
    except FileNotFoundError:
        return str(path)


def find_submission_lookalikes(scan_root: Path, canonical: Path, aliases: list[Path], canonical_sha: str) -> list[dict[str, str]]:
    """Find submission.csv files that a manual file picker might expose."""
    safe_keys = {path_key(canonical)}
    safe_keys.update(path_key(alias) for alias in aliases if alias.exists())
    lookalikes: list[dict[str, str]] = []
    if not scan_root.exists():
        return lookalikes

    for path in sorted(scan_root.rglob("submission.csv")):
        if is_inside_git(path):
            continue
        exists = path.exists()
        rows = row_count(path) if exists else 0
        file_sha = sha256(path) if exists else ""
        is_safe_path = path_key(path) in safe_keys
        sha_matches = bool(canonical_sha) and file_sha == canonical_sha
        if is_safe_path and sha_matches and rows == EXPECTED_ROWS:
            status = "safe_whitelist"
            detail = "safe upload path"
        elif sha_matches and rows == EXPECTED_ROWS:
            status = "unlisted_same_bytes"
            detail = "same bytes as canonical but not in upload alias whitelist"
        else:
            status = "do_not_upload"
            detail = "different SHA or row count from canonical current upload"
        lookalikes.append(
            {
                "path": str(path),
                "exists": "yes" if exists else "no",
                "rows": str(rows),
                "sha256": file_sha,
                "sha_matches": "yes" if sha_matches else "no",
                "status": status,
                "detail": detail,
            }
        )
    return lookalikes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check upload CSV aliases against the canonical current upload.")
    parser.add_argument("--canonical", type=Path, default=CANONICAL)
    parser.add_argument("--alias", type=Path, action="append", default=None)
    parser.add_argument(
        "--scan-root",
        type=Path,
        default=DEFAULT_SCAN_ROOT,
        help="Root to scan for submission.csv lookalikes. Defaults to the repository root.",
    )
    parser.add_argument("--no-lookalike-scan", action="store_true", help="Skip repository-wide submission.csv lookalike scan.")
    parser.add_argument("--out-json", type=Path, default=OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    return parser.parse_args()


def write_outputs(payload: dict[str, Any], out_json: Path, out_md: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v1902 Upload Alias Guard",
        "",
        f"Generated UTC: `{payload['generated_at_utc']}`",
        "",
        "## Summary",
        "",
        f"- Alias guard ready: `{payload['alias_guard_ready']}`",
        f"- Canonical upload: `{payload['canonical']}`",
        f"- Canonical rows: `{payload['canonical_rows']}`",
        f"- Canonical SHA-256: `{payload['canonical_sha256']}`",
        "",
        "## Alias results",
        "",
        "| Alias | Exists | Rows | SHA matches | Detail |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for alias in payload["aliases"]:
        detail = str(alias["detail"]).replace("|", "\\|")
        lines.append(
            f"| `{alias['path']}` | {alias['exists']} | `{alias['rows']}` | {alias['sha_matches']} | `{detail}` |"
        )
    lines.extend(
        [
            "",
            "## submission.csv lookalike scan",
            "",
            "| Path | Rows | SHA matches canonical | Status | Detail |",
            "| --- | ---: | --- | --- | --- |",
        ]
    )
    for item in payload["lookalikes"]:
        detail = str(item["detail"]).replace("|", "\\|")
        lines.append(
            f"| `{item['path']}` | `{item['rows']}` | {item['sha_matches']} | `{item['status']}` | `{detail}` |"
        )
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | OK | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for check in payload["checks"]:
        detail = str(check["detail"]).replace("|", "\\|")
        lines.append(f"| {check['name']} | {check['ok']} | `{detail}` |")
    lines.extend(
        [
            "",
            "## Completion boundary",
            "",
            "This guard only prevents wrong-file manual upload risk. The active goal is complete only after a real private score greater than `0.52380` is recorded.",
            "",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    aliases = args.alias if args.alias is not None else default_aliases()
    checks: list[dict[str, str]] = []
    alias_payloads: list[dict[str, str]] = []

    add_check(checks, "canonical_exists", args.canonical.exists(), str(args.canonical))
    canonical_sha = ""
    canonical_rows = 0
    if args.canonical.exists():
        canonical_sha = sha256(args.canonical)
        canonical_rows = row_count(args.canonical)
    add_check(checks, "canonical_rows_397", canonical_rows == EXPECTED_ROWS, str(canonical_rows))

    for idx, alias in enumerate(aliases, start=1):
        exists = alias.exists()
        rows = row_count(alias) if exists else 0
        alias_sha = sha256(alias) if exists else ""
        sha_matches = exists and bool(canonical_sha) and alias_sha == canonical_sha
        rows_match = exists and rows == canonical_rows == EXPECTED_ROWS
        add_check(checks, f"alias_{idx}_exists", exists, str(alias))
        add_check(checks, f"alias_{idx}_rows_match", rows_match, f"alias={rows} canonical={canonical_rows}")
        add_check(checks, f"alias_{idx}_sha_matches", sha_matches, alias_sha)
        alias_payloads.append(
            {
                "path": str(alias),
                "exists": "yes" if exists else "no",
                "rows": str(rows),
                "sha256": alias_sha,
                "sha_matches": "yes" if sha_matches else "no",
                "detail": "ok" if exists and rows_match and sha_matches else "mismatch_or_missing",
            }
        )

    lookalikes = [] if args.no_lookalike_scan else find_submission_lookalikes(args.scan_root, args.canonical, aliases, canonical_sha)
    add_check(checks, "lookalike_scan_completed", True, "skipped" if args.no_lookalike_scan else str(args.scan_root))

    ready = all(check["ok"] == "yes" for check in checks)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "alias_guard_ready": "yes" if ready else "no",
        "canonical": str(args.canonical),
        "canonical_rows": canonical_rows,
        "canonical_sha256": canonical_sha,
        "aliases": alias_payloads,
        "lookalikes": lookalikes,
        "checks": checks,
    }
    write_outputs(payload, args.out_json, args.out_md)

    print("UPLOAD_ALIAS_GUARD")
    print(f"ALIAS_GUARD_READY={'yes' if ready else 'no'}")
    print(f"CANONICAL={args.canonical}")
    print(f"CANONICAL_ROWS={canonical_rows}")
    print(f"CANONICAL_SHA256={canonical_sha}")
    for alias in alias_payloads:
        print(f"ALIAS={alias['path']} rows={alias['rows']} sha_matches={alias['sha_matches']}")
    for item in lookalikes:
        print(f"LOOKALIKE={item['path']} rows={item['rows']} sha_matches={item['sha_matches']} status={item['status']}")
    print(f"REPORT={args.out_md}")
    print(f"JSON={args.out_json}")
    if not ready:
        failed = ",".join(check["name"] for check in checks if check["ok"] != "yes")
        raise SystemExit(f"upload alias guard failed: {failed}")


if __name__ == "__main__":
    main()
