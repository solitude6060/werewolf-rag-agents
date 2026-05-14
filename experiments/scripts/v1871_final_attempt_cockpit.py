#!/usr/bin/env python3
"""Print and write a compact final-attempt cockpit card."""
from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MANIFEST = Path("experiments/final_submission_package/manifests/final_submission_pack_manifest.csv")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
STAGED = Path("experiments/final_submission_package/current_upload/submission.csv")
CARD = Path("experiments/final_submission_package/current_upload/ATTEMPT_CARD.md")
VALIDATOR = Path("werewolf-project/assert/validate_submission.py")
ROUTER = Path("experiments/scripts/v1836_score_feedback_router.py")
DEFAULT_GROUP = "scoreonly_safe_queue"
DEFAULT_ORDER = 1
BASELINE = 0.47119
TOP3 = 0.50671


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_manifest(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"manifest not found: {path}")
    return read_csv_rows(path)


def read_records(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    return read_csv_rows(path)


def find_row(rows: list[dict[str, str]], group: str, order: int) -> dict[str, str]:
    for row in rows:
        if row.get("group") == group and int(row.get("order", "0")) == order:
            return row
    raise SystemExit(f"manifest row not found: {group} order {order}")


def find_row_by_output_path(rows: list[dict[str, str]], path: str) -> dict[str, str]:
    target = str(Path(path))
    for row in rows:
        if str(Path(row.get("output_path", ""))) == target:
            return row
    raise SystemExit(f"path not found in manifest: {path}")


def selected_row(manifest: list[dict[str, str]], records: list[dict[str, str]]) -> tuple[dict[str, str], str]:
    if not records:
        return find_row(manifest, DEFAULT_GROUP, DEFAULT_ORDER), "no_records_default"
    recommended = records[-1].get("recommended_next", "").strip()
    if recommended.endswith(".csv"):
        return find_row_by_output_path(manifest, recommended), "latest_record_recommended_next"
    return records[-1], "latest_record_stop_or_manual"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def row_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def validate(path: Path) -> str:
    proc = subprocess.run([sys.executable, str(VALIDATOR), str(path)], text=True, capture_output=True, check=False)
    output = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0:
        return f"FAIL exit={proc.returncode}: {output}"
    return output


def router_preview(group: str, order: int, score: float, previous_score: float | None) -> str:
    cmd = [sys.executable, str(ROUTER), "--group", group, "--order", str(order), "--score", f"{score:.5f}", "--dry-run"]
    if previous_score is not None:
        cmd.extend(["--previous-score", f"{previous_score:.5f}"])
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    output = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0:
        return f"ROUTER_FAIL exit={proc.returncode}: {output}"
    for line in output.splitlines():
        if line.startswith("recommended_next="):
            return line.split("=", 1)[1]
    return output.replace("\n", " | ")


def best_score(records: list[dict[str, str]]) -> float | None:
    if not records:
        return None
    return max(float(row["score"]) for row in records)


def latest_score(records: list[dict[str, str]]) -> float | None:
    if not records:
        return None
    return float(records[-1]["score"])


def concrete_path_status(manifest: list[dict[str, str]], recommendation: str) -> str:
    if not recommendation.endswith(".csv"):
        return "not_a_csv"
    try:
        row = find_row_by_output_path(manifest, recommendation)
    except SystemExit:
        return "missing_from_manifest"
    path = Path(row["output_path"])
    if not path.exists():
        return "missing_file"
    actual_sha = sha256(path)
    if row.get("sha256") and actual_sha != row["sha256"]:
        return "hash_mismatch"
    if row_count(path) != 397:
        return "bad_row_count"
    return f"ok manifest_status={row.get('validation_status', '')} candidate={row.get('candidate', '')}"


def make_card(
    manifest: list[dict[str, str]],
    records: list[dict[str, str]],
    row: dict[str, str],
    row_source: str,
) -> str:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    used = len(records)
    remaining = max(5 - used, 0)
    best = best_score(records)
    latest = latest_score(records)
    if row_source == "latest_record_stop_or_manual":
        latest_record = records[-1]
        selected_lines = [
            "## Current state",
            "",
            f"Latest record recommends: `{latest_record.get('recommended_next', '')}`",
            f"Best recorded score: `{best:.5f}`" if best is not None else "Best recorded score: `none`",
            f"Top-3 hit: `{'yes' if best is not None and best > TOP3 else 'no'}`",
            "",
        ]
        return "\n".join(
            [
                "# Final Attempt Cockpit",
                "",
                f"Generated UTC: `{now}`",
                "",
                *selected_lines,
                "## Next action",
                "",
                "Do not upload a new file until the manual/stop state is reviewed.",
                "",
            ]
        )

    source = Path(row["output_path"])
    source_sha = sha256(source)
    rows = row_count(source)
    source_validation = row.get("validation_status", "")
    staged_exists = STAGED.exists()
    staged_sha = sha256(STAGED) if staged_exists else ""
    staged_match = staged_exists and staged_sha == source_sha
    staged_validator = validate(STAGED) if staged_exists else "missing"
    previous = latest if records else None

    scenarios = [
        ("hit top-3", 0.50672),
        ("strong positive", 0.48000),
        ("tiny positive", 0.47120),
        ("exact current best", 0.47119),
        ("near baseline", 0.47080),
        ("small regression", 0.46600),
        ("severe regression", 0.46400),
    ]
    scenario_rows: list[str] = []
    for label, score in scenarios:
        recommendation = router_preview(row["group"], int(row["order"]), score, previous)
        scenario_rows.append(
            f"| {label} | `{score:.5f}` | `{recommendation}` | `{concrete_path_status(manifest, recommendation)}` |"
        )

    best_text = f"{best:.5f}" if best is not None else "none"
    latest_text = f"{latest:.5f}" if latest is not None else "none"
    return "\n".join(
        [
            "# Final Attempt Cockpit",
            "",
            f"Generated UTC: `{now}`",
            "",
            "## Upload now",
            "",
            "Use this fixed path:",
            "",
            "```text",
            str(STAGED),
            "```",
            "",
            f"Selected row source: `{row_source}`",
            f"Selected candidate: `{row['candidate']}` (`{row['group']}` order `{row['order']}`)",
            f"Selected source: `{source}`",
            f"Rows: `{rows}`",
            f"SHA-256: `{source_sha}`",
            f"Manifest validation status: `{source_validation}`",
            f"Staged file exists: `{'yes' if staged_exists else 'no'}`",
            f"Staged file matches selected source: `{'yes' if staged_match else 'no'}`",
            f"Staged validator: `{staged_validator}`",
            "",
            "If staged match is not `yes`, run:",
            "",
            "```bash",
            "python3 experiments/scripts/v1870_stage_current_upload.py --from-records",
            "```",
            "",
            "For the first upload with no records, this is also valid:",
            "",
            "```bash",
            "python3 experiments/scripts/v1870_stage_current_upload.py",
            "```",
            "",
            "## Attempt budget",
            "",
            f"Attempts used from records: `{used}`",
            f"Attempts remaining from records: `{remaining}`",
            f"Best recorded score: `{best_text}`",
            f"Latest recorded score: `{latest_text}`",
            f"Stop threshold: `>{TOP3:.5f}`",
            "",
            "## After real score appears",
            "",
            "Dry-run first:",
            "",
            "```bash",
            "python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>",
            "```",
            "",
            "Then record only if the score is real:",
            "",
            "```bash",
            "python3 experiments/scripts/v1872_post_score_command_center.py "
            f"--group {row['group']} --order {row['order']} --score <REAL_SCORE> --confirm-real-score",
            "```",
            "",
            "## Router preview for this selected row",
            "",
            "| Scenario | Example score | Recommended next | Path check |",
            "| --- | ---: | --- | --- |",
            *scenario_rows,
            "",
            "## Completion boundary",
            "",
            f"Only a real private score greater than `{TOP3:.5f}` completes the active score objective.",
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print/write final-attempt cockpit card.")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--records", type=Path, default=RECORDS)
    parser.add_argument("--card", type=Path, default=CARD)
    parser.add_argument("--no-write", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = read_manifest(args.manifest)
    records = read_records(args.records)
    row, row_source = selected_row(manifest, records)
    card = make_card(manifest, records, row, row_source)
    print(card)
    if not args.no_write:
        args.card.parent.mkdir(parents=True, exist_ok=True)
        args.card.write_text(card + "\n", encoding="utf-8")
        print(f"CARD_WRITTEN={args.card}")


if __name__ == "__main__":
    main()
