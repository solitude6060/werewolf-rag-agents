#!/usr/bin/env python3
"""Generate v1850 low-tail denoise calibration candidates.

Starting from v1848 outputs, demote non-Werewolf-role low tail scores:

    if role != Werewolf and 0.05 <= wolf_score < 0.20:
        wolf_score = 0.001

This is a tiny global-AP calibration.  It should be treated as marginal and
higher public-calibration risk than v1848, but it does not change roles.
"""
from __future__ import annotations

import csv
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

FIELDS = ["id", "index", "character", "role", "wolf_score"]
EV_FIELDS = ["candidate", "split", "id", "index", "character", "role", "old_wolf_score", "new_wolf_score", "action", "risk"]
OUT = Path("experiments/submissions")
REPORT = Path("experiments/reports/v1850_lowtail_denoise_calibration.md")


@dataclass(frozen=True)
class BaseSpec:
    tag: str
    private_base: Path
    public_base: Path
    note: str


BASES = [
    BaseSpec("v1850a_queue01_v1848a_lowtail", OUT / "submission_v1848a_queue01_v1846a_denoise_private.csv", OUT / "submission_v1848a_queue01_v1846a_denoise_public.csv", "v1848a plus low-tail denoise."),
    BaseSpec("v1850b_queue02_v1848b_lowtail", OUT / "submission_v1848b_queue02_v1846b_denoise_private.csv", OUT / "submission_v1848b_queue02_v1846b_denoise_public.csv", "v1848b plus low-tail denoise."),
    BaseSpec("v1850c_queue03_v1848c_lowtail", OUT / "submission_v1848c_queue03_v1846c_denoise_private.csv", OUT / "submission_v1848c_queue03_v1846c_denoise_public.csv", "v1848c plus low-tail denoise."),
    BaseSpec("v1850d_queue04_v1848d_lowtail", OUT / "submission_v1848d_queue04_v1846d_denoise_private.csv", OUT / "submission_v1848d_queue04_v1846d_denoise_public.csv", "v1848d plus low-tail denoise."),
    BaseSpec("v1850e_queue05_v1848e_lowtail", OUT / "submission_v1848e_queue05_v1846e_denoise_private.csv", OUT / "submission_v1848e_queue05_v1846e_denoise_public.csv", "v1848e plus low-tail denoise."),
    BaseSpec("v1850f_v1848f_lowtail", OUT / "submission_v1848f_v1824a_rolecap_denoise_private.csv", OUT / "submission_v1848f_v1824a_rolecap_denoise_public.csv", "fallback v1848f plus low-tail denoise."),
    BaseSpec("v1850g_v1848g_lowtail", OUT / "submission_v1848g_v1845c_rolecap_denoise_private.csv", OUT / "submission_v1848g_v1845c_rolecap_denoise_public.csv", "fallback v1848g plus low-tail denoise."),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows([{key: row[key] for key in FIELDS} for row in rows])


def write_evidence(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def apply(rows: list[dict[str, str]], candidate: str, split: str) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    for row in rows:
        score = float(row["wolf_score"])
        if row["role"] == "Werewolf":
            continue
        if 0.05 <= score < 0.20:
            old = row["wolf_score"]
            row["wolf_score"] = "0.001"
            evidence.append(
                {
                    "candidate": candidate,
                    "split": split,
                    "id": row["id"],
                    "index": row["index"],
                    "character": row["character"],
                    "role": row["role"],
                    "old_wolf_score": old,
                    "new_wolf_score": row["wolf_score"],
                    "action": "lowtail_nonwerewolf_denoise",
                    "risk": "Tiny public-calibrated AP effect; if low-tail private rows include true wolves, it can hurt.",
                }
            )
    return evidence


def run_quiet(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    return proc.stdout.strip()


def emit(spec: BaseSpec) -> dict[str, str]:
    private_rows = read(spec.private_base)
    public_rows = read(spec.public_base)
    evidence = []
    evidence.extend(apply(private_rows, spec.tag, "private"))
    evidence.extend(apply(public_rows, spec.tag, "public"))
    private_out = OUT / f"submission_{spec.tag}_private.csv"
    public_out = OUT / f"submission_{spec.tag}_public.csv"
    evidence_out = OUT / f"submission_{spec.tag}_evidence.csv"
    write(private_out, private_rows)
    write(public_out, public_rows)
    write_evidence(evidence_out, evidence)
    private_changes = sum(1 for row in evidence if row["split"] == "private")
    public_changes = sum(1 for row in evidence if row["split"] == "public")
    private_validation = run_quiet([sys.executable, "werewolf-project/assert/validate_submission.py", str(private_out)])
    public_validation = run_quiet([sys.executable, "werewolf-project/assert/validate_submission.py", str(public_out)])
    public_score = run_quiet([sys.executable, "experiments/scripts/local_score.py", str(public_out), "--quiet"])
    print(f"{spec.tag}\tprivate_changes={private_changes}\tpublic_changes={public_changes}\tprivate_validation={private_validation}\tpublic_validation={public_validation}\tpublic={public_score}")
    return {
        "tag": spec.tag,
        "private_csv": str(private_out),
        "public_proxy": public_score.rsplit("Score=", 1)[-1],
        "private_changes": str(private_changes),
        "public_changes": str(public_changes),
        "note": spec.note,
    }


def write_report(rows: list[dict[str, str]]) -> None:
    lines = [
        "# v1850 Low-Tail Denoise Calibration",
        "",
        "Date: 2026-05-14",
        "",
        "## Rule",
        "",
        "```text",
        "if role != Werewolf and 0.05 <= wolf_score < 0.20:",
        "    wolf_score = 0.001",
        "```",
        "",
        "## Candidates",
        "",
        "| Candidate | Private CSV | Public proxy | Private changes | Public changes | Note |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['tag'].split('_', 1)[0]} | `{row['private_csv']}` | {row['public_proxy']} | "
            f"{row['private_changes']} | {row['public_changes']} | {row['note']} |"
        )
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            "v1850a is the absolute highest public-proxy first shot, but the lift over v1848a is tiny. Prefer v1850a only if chasing every AP basis point:",
            "",
            "```text",
            "experiments/final_submission_package/lowtail_queue/01_v1850a_queue01_v1848a_lowtail_private.csv",
            "```",
            "",
            "If avoiding marginal over-calibration, use v1848a.",
            "",
            "No Kaggle upload was performed.",
        ]
    )
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    rows = [emit(spec) for spec in BASES]
    write_report(rows)
    print(f"report={REPORT}")


if __name__ == "__main__":
    main()
