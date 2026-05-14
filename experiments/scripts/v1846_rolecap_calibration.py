#!/usr/bin/env python3
"""Generate v1846 role-cap score calibration candidates.

Rule: if a row is currently labeled Werewolf and has wolf_score > 0.99, cap it
to 0.99.  This preserves role labels and role counts while ranking explicit
non-role black-evidence boosts at 1.0 above generic Werewolf-role assignments.

This is a high-upside AP calibration: public proxy improves sharply, but private
transfer depends on whether the 1.0 non-role black-evidence rows are true wolves.
"""
from __future__ import annotations

import csv
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

FIELDS = ["id", "index", "character", "role", "wolf_score"]
EV_FIELDS = [
    "candidate",
    "split",
    "id",
    "index",
    "character",
    "role",
    "old_wolf_score",
    "new_wolf_score",
    "action",
    "rationale",
    "risk",
]
OUT = Path("experiments/submissions")
REPORT = Path("experiments/reports/v1846_rolecap_calibration.md")
CAP = 0.99


@dataclass(frozen=True)
class BaseSpec:
    tag: str
    private_base: Path
    public_base: Path
    note: str


BASES = [
    BaseSpec(
        "v1846a_queue01_v1842a_rolecap099",
        Path("experiments/submissions/submission_v1842a_queue01_v1826a_blackboost_attack_private.csv"),
        Path("experiments/submissions/submission_v1842a_queue01_v1826a_blackboost_attack_public.csv"),
        "Maximum public-proxy first shot: v1842a plus role-Werewolf score cap.",
    ),
    BaseSpec(
        "v1846b_queue02_v1842b_rolecap099",
        Path("experiments/submissions/submission_v1842b_queue02_v1826b_blackboost_attack_private.csv"),
        Path("experiments/submissions/submission_v1842b_queue02_v1826b_blackboost_attack_public.csv"),
        "Role-cap version of v1842 queue order 2.",
    ),
    BaseSpec(
        "v1846c_queue03_v1842c_rolecap099",
        Path("experiments/submissions/submission_v1842c_queue03_v1826d_blackboost_attack_private.csv"),
        Path("experiments/submissions/submission_v1842c_queue03_v1826d_blackboost_attack_public.csv"),
        "Role-cap version of v1842 queue order 3.",
    ),
    BaseSpec(
        "v1846d_queue04_v1842d_rolecap099",
        Path("experiments/submissions/submission_v1842d_queue04_v1826c_blackboost_attack_private.csv"),
        Path("experiments/submissions/submission_v1842d_queue04_v1826c_blackboost_attack_public.csv"),
        "Role-cap version of v1842 queue order 4.",
    ),
    BaseSpec(
        "v1846e_queue05_v1842e_rolecap099",
        Path("experiments/submissions/submission_v1842e_queue05_v1829e_blackboost_attack_private.csv"),
        Path("experiments/submissions/submission_v1842e_queue05_v1829e_blackboost_attack_public.csv"),
        "Role-cap version of v1842 queue order 5.",
    ),
    BaseSpec(
        "v1846f_v1824a_rolecap099",
        Path("experiments/submissions/submission_v1824a_v1823a_plus_g24_thomas_trueseer_private.csv"),
        Path("experiments/submissions/submission_v1824a_v1823a_plus_g24_thomas_trueseer_public.csv"),
        "Low-structural-risk fallback: verified-best v1824a plus role-Werewolf score cap.",
    ),
    BaseSpec(
        "v1846g_v1845c_rolecap099",
        Path("experiments/submissions/submission_v1845c_v1824a_blackboost_score_overlay_private.csv"),
        Path("experiments/submissions/submission_v1845c_v1824a_blackboost_score_overlay_public.csv"),
        "Score-only fallback: v1845c plus role-Werewolf score cap.",
    ),
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
        if row["role"] != "Werewolf" or score <= CAP:
            continue
        old = row["wolf_score"]
        row["wolf_score"] = f"{CAP:.2f}"
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
                "action": "cap_role_werewolf_score",
                "rationale": "Rank explicit 1.0 black-evidence non-role rows above generic Werewolf-role assignments without changing roles.",
                "risk": "If the 1.0 non-role black-evidence rows are false positives on private, AP can regress.",
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
    print(
        f"{spec.tag}\tprivate_changes={private_changes}\tpublic_changes={public_changes}"
        f"\tprivate_validation={private_validation}\tpublic_validation={public_validation}\tpublic={public_score}"
    )
    return {
        "tag": spec.tag,
        "private_csv": str(private_out),
        "public_csv": str(public_out),
        "evidence_csv": str(evidence_out),
        "private_changes": str(private_changes),
        "public_changes": str(public_changes),
        "public_proxy": public_score.rsplit("Score=", 1)[-1],
        "note": spec.note,
    }


def write_report(rows: list[dict[str, str]]) -> None:
    lines = [
        "# v1846 Role-Cap Score Calibration",
        "",
        "Date: 2026-05-14",
        "",
        "## Rule",
        "",
        "If `role == Werewolf` and `wolf_score > 0.99`, set `wolf_score = 0.99`.",
        "",
        "The rule changes only scores.  It leaves role labels and role counts unchanged.",
        "",
        "## Why this is considered",
        "",
        "The v1842/v1845 black-evidence overlays create a small set of non-Werewolf-role rows with `wolf_score = 1.0`.  On public validation, those rows are high precision.  Capping generic Werewolf-role 1.0 scores to 0.99 ranks the explicit black-evidence rows ahead of generic role assignments and improves Wolf-AP.",
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
            "Use v1846a as the new maximum-public-proxy first shot if accepting AP-rank calibration risk:",
            "",
            "```text",
            "experiments/final_submission_package/rolecap_queue/01_v1846a_queue01_v1842a_rolecap099_private.csv",
            "```",
            "",
            "If avoiding structural role changes while still using the same role-cap calibration, use the score-only fallback:",
            "",
            "```text",
            "experiments/final_submission_package/rolecap_fallback/02_v1846g_v1845c_rolecap099_private.csv",
            "```",
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
