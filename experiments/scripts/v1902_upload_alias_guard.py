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
DEFAULT_ALIASES = [
    Path("hw2_D13922024/submission.csv"),
    Path("hw2_D13922024/checkpoints/final_v1856g_private.csv"),
]
OUT_JSON = Path("experiments/reports/v1902_upload_alias_guard.json")
OUT_MD = Path("experiments/reports/v1902_upload_alias_guard.md")
EXPECTED_ROWS = 397


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
    parser = argparse.ArgumentParser(description="Check upload CSV aliases against the canonical current upload.")
    parser.add_argument("--canonical", type=Path, default=CANONICAL)
    parser.add_argument("--alias", type=Path, action="append", default=None)
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
            "This guard only prevents wrong-file manual upload risk. The active goal is complete only after a real private score greater than `0.50671` is recorded.",
            "",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    aliases = args.alias if args.alias is not None else DEFAULT_ALIASES
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

    ready = all(check["ok"] == "yes" for check in checks)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "alias_guard_ready": "yes" if ready else "no",
        "canonical": str(args.canonical),
        "canonical_rows": canonical_rows,
        "canonical_sha256": canonical_sha,
        "aliases": alias_payloads,
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
    print(f"REPORT={args.out_md}")
    print(f"JSON={args.out_json}")
    if not ready:
        failed = ",".join(check["name"] for check in checks if check["ok"] != "yes")
        raise SystemExit(f"upload alias guard failed: {failed}")


if __name__ == "__main__":
    main()
