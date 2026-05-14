#!/usr/bin/env python3
"""Generate v1848 non-Werewolf denoise calibration candidates.

Starting from v1846 role-cap candidates:
- keep explicit black-evidence rows at wolf_score = 1.0;
- keep Werewolf-role rows at their v1846 calibrated scores;
- for non-Werewolf-role rows with 0.30 <= wolf_score < 1.0, set score to 0.20.

This is still score-only; it does not change role labels or role counts.
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
REPORT = Path("experiments/reports/v1848_nonwolf_denoise_calibration.md")
THRESHOLD = 0.30
CAP = 0.20


@dataclass(frozen=True)
class BaseSpec:
    tag: str
    private_base: Path
    public_base: Path
    note: str


BASES = [
    BaseSpec(
        "v1848a_queue01_v1846a_denoise",
        Path("experiments/submissions/submission_v1846a_queue01_v1842a_rolecap099_private.csv"),
        Path("experiments/submissions/submission_v1846a_queue01_v1842a_rolecap099_public.csv"),
        "Maximum public-proxy first shot: v1846a plus non-Werewolf mid/high score denoise.",
    ),
    BaseSpec(
        "v1848b_queue02_v1846b_denoise",
        Path("experiments/submissions/submission_v1846b_queue02_v1842b_rolecap099_private.csv"),
        Path("experiments/submissions/submission_v1846b_queue02_v1842b_rolecap099_public.csv"),
        "Denoise version of v1846 queue order 2.",
    ),
    BaseSpec(
        "v1848c_queue03_v1846c_denoise",
        Path("experiments/submissions/submission_v1846c_queue03_v1842c_rolecap099_private.csv"),
        Path("experiments/submissions/submission_v1846c_queue03_v1842c_rolecap099_public.csv"),
        "Denoise version of v1846 queue order 3.",
    ),
    BaseSpec(
        "v1848d_queue04_v1846d_denoise",
        Path("experiments/submissions/submission_v1846d_queue04_v1842d_rolecap099_private.csv"),
        Path("experiments/submissions/submission_v1846d_queue04_v1842d_rolecap099_public.csv"),
        "Denoise version of v1846 queue order 4.",
    ),
    BaseSpec(
        "v1848e_queue05_v1846e_denoise",
        Path("experiments/submissions/submission_v1846e_queue05_v1842e_rolecap099_private.csv"),
        Path("experiments/submissions/submission_v1846e_queue05_v1842e_rolecap099_public.csv"),
        "Denoise version of v1846 queue order 5.",
    ),
    BaseSpec(
        "v1848f_v1824a_rolecap_denoise",
        Path("experiments/submissions/submission_v1846f_v1824a_rolecap099_private.csv"),
        Path("experiments/submissions/submission_v1846f_v1824a_rolecap099_public.csv"),
        "Lower-structural-risk fallback: v1824a role-cap plus denoise.",
    ),
    BaseSpec(
        "v1848g_v1845c_rolecap_denoise",
        Path("experiments/submissions/submission_v1846g_v1845c_rolecap099_private.csv"),
        Path("experiments/submissions/submission_v1846g_v1845c_rolecap099_public.csv"),
        "Score-only fallback: v1845c role-cap plus denoise.",
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
        if row["role"] == "Werewolf":
            continue
        if score >= 0.999999:
            continue
        if score < THRESHOLD:
            continue
        old = row["wolf_score"]
        row["wolf_score"] = f"{CAP:.1f}"
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
                "action": "denoise_nonwerewolf_mid_high_score",
                "rationale": "Preserve explicit 1.0 black-evidence rows, but demote non-Werewolf-role mid/high scores that lack that explicit signal.",
                "risk": "Some demoted non-Werewolf-role rows can still be true wolves; private transfer may differ.",
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
        "# v1848 Non-Werewolf Denoise Calibration",
        "",
        "Date: 2026-05-14",
        "",
        "## Rule",
        "",
        "Starting from v1846 outputs:",
        "",
        "```text",
        "if role != Werewolf and 0.30 <= wolf_score < 1.0:",
        "    wolf_score = 0.20",
        "```",
        "",
        "The rule preserves explicit `1.0` black-evidence rows and all role labels.  It only demotes non-Werewolf-role mid/high scores without the explicit top-rank signal.",
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
            "Use v1848a as the most aggressive public-proxy first shot if accepting the added denoise risk:",
            "",
            "```text",
            "experiments/final_submission_package/denoise_queue/01_v1848a_queue01_v1846a_denoise_private.csv",
            "```",
            "",
            "If preferring the already-robust v1846 role-cap without this extra denoise layer, use v1846a instead.",
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
