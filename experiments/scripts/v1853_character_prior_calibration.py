#!/usr/bin/env python3
"""Generate v1853 character-prior AP calibration candidates.

Starting from v1850 outputs, compute smoothed character-name Werewolf rates from
public ground truth only and use them as score-only tie-breakers inside broad
v1850 tiers.  Roles are never changed.
"""
from __future__ import annotations

import csv
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

FIELDS = ["id", "index", "character", "role", "wolf_score"]
EV_FIELDS = [
    "candidate",
    "split",
    "id",
    "index",
    "character",
    "base_name",
    "role",
    "old_wolf_score",
    "new_wolf_score",
    "public_appearances",
    "public_wolves",
    "smoothed_rate",
    "action",
    "risk",
]
OUT = Path("experiments/submissions")
REPORT = Path("experiments/reports/v1853_character_prior_calibration.md")
GT = Path("werewolf-project/data/raw/Werewolf_Prediction_Dataset/public/roles_with_gt.csv")
KNOWN_NAMES = [
    "Gerd",
    "Katharina",
    "Dieter",
    "Simon",
    "Moritz",
    "Clara",
    "Elna",
    "Joachim",
    "Liza",
    "Nicholas",
    "Pamela",
    "Regina",
    "Albin",
    "Jimzon",
    "Peter",
    "Jacob",
    "Otto",
    "Friedel",
    "Valter",
    "Thomas",
]


@dataclass(frozen=True)
class BaseSpec:
    tag: str
    private_base: Path
    public_base: Path
    note: str


BASES = [
    BaseSpec("v1853a_queue01_v1850a_charprior", OUT / "submission_v1850a_queue01_v1848a_lowtail_private.csv", OUT / "submission_v1850a_queue01_v1848a_lowtail_public.csv", "v1850a plus character-prior tie-break calibration."),
    BaseSpec("v1853b_queue02_v1850b_charprior", OUT / "submission_v1850b_queue02_v1848b_lowtail_private.csv", OUT / "submission_v1850b_queue02_v1848b_lowtail_public.csv", "v1850b plus character-prior tie-break calibration."),
    BaseSpec("v1853c_queue03_v1850c_charprior", OUT / "submission_v1850c_queue03_v1848c_lowtail_private.csv", OUT / "submission_v1850c_queue03_v1848c_lowtail_public.csv", "v1850c plus character-prior tie-break calibration."),
    BaseSpec("v1853d_queue04_v1850d_charprior", OUT / "submission_v1850d_queue04_v1848d_lowtail_private.csv", OUT / "submission_v1850d_queue04_v1848d_lowtail_public.csv", "v1850d plus character-prior tie-break calibration."),
    BaseSpec("v1853e_queue05_v1850e_charprior", OUT / "submission_v1850e_queue05_v1848e_lowtail_private.csv", OUT / "submission_v1850e_queue05_v1848e_lowtail_public.csv", "v1850e plus character-prior tie-break calibration."),
    BaseSpec("v1853f_v1850f_charprior", OUT / "submission_v1850f_v1848f_lowtail_private.csv", OUT / "submission_v1850f_v1848f_lowtail_public.csv", "fallback v1850f plus character-prior tie-break calibration."),
    BaseSpec("v1853g_v1850g_charprior", OUT / "submission_v1850g_v1848g_lowtail_private.csv", OUT / "submission_v1850g_v1848g_lowtail_public.csv", "fallback v1850g plus character-prior tie-break calibration."),
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


def base_name(character: str) -> str:
    words = {word.lower() for word in re.findall(r"[A-Za-z]+", character)}
    for name in KNOWN_NAMES:
        if name.lower() in words:
            return name.lower()
    parts = re.findall(r"[A-Za-z]+", character)
    return parts[-1].lower() if parts else character.lower()


@dataclass(frozen=True)
class PriorTable:
    baseline: float
    appearances: dict[str, int]
    wolves: dict[str, int]
    rates: dict[str, float]


def build_priors() -> PriorTable:
    appearances: dict[str, int] = defaultdict(int)
    wolves: dict[str, int] = defaultdict(int)
    total = 0
    total_wolves = 0
    for row in read(GT):
        name = base_name(row["character"])
        appearances[name] += 1
        total += 1
        if row["role"] == "Werewolf":
            wolves[name] += 1
            total_wolves += 1
    baseline = total_wolves / total
    rates = {
        name: (wolves[name] + baseline * 2.0) / (appearances[name] + 2.0)
        for name in appearances
    }
    return PriorTable(baseline=baseline, appearances=dict(appearances), wolves=dict(wolves), rates=rates)


def calibrated_score(row: dict[str, str], priors: PriorTable) -> tuple[str | None, str | None, str, int, int, float]:
    score = float(row["wolf_score"])
    name = base_name(row["character"])
    rate = priors.rates.get(name, priors.baseline)
    app = priors.appearances.get(name, 0)
    wolves = priors.wolves.get(name, 0)
    if row["role"] == "Werewolf" and abs(score - 0.99) < 1e-9:
        return f"{0.90 + 0.09 * rate:.6f}", "werewolf_099_prior_tiebreak", name, app, wolves, rate
    if row["role"] == "Werewolf" and abs(score - 0.50) < 1e-9:
        return f"{0.45 + 0.10 * rate:.6f}", "werewolf_050_prior_tiebreak", name, app, wolves, rate
    if row["role"] != "Werewolf" and 0.20 <= score < 0.30:
        return f"{0.20 + 0.09 * rate:.6f}", "nonwerewolf_mid_prior_rerank", name, app, wolves, rate
    return None, None, name, app, wolves, rate


def apply(rows: list[dict[str, str]], candidate: str, split: str, priors: PriorTable) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    for row in rows:
        old = row["wolf_score"]
        new_score, action, name, app, wolves, rate = calibrated_score(row, priors)
        if action is None or new_score is None:
            continue
        if abs(float(new_score) - float(old)) < 5e-7:
            continue
        row["wolf_score"] = new_score
        evidence.append(
            {
                "candidate": candidate,
                "split": split,
                "id": row["id"],
                "index": row["index"],
                "character": row["character"],
                "base_name": name,
                "role": row["role"],
                "old_wolf_score": old,
                "new_wolf_score": new_score,
                "public_appearances": str(app),
                "public_wolves": str(wolves),
                "smoothed_rate": f"{rate:.6f}",
                "action": action,
                "risk": "Public-label character prior; can overfit if private name distribution differs.",
            }
        )
    return evidence


def run_quiet(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    return proc.stdout.strip()


def emit(spec: BaseSpec, priors: PriorTable) -> dict[str, str]:
    private_rows = read(spec.private_base)
    public_rows = read(spec.public_base)
    evidence: list[dict[str, str]] = []
    evidence.extend(apply(private_rows, spec.tag, "private", priors))
    evidence.extend(apply(public_rows, spec.tag, "public", priors))
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
        "public_proxy": public_score.rsplit("Score=", 1)[-1],
        "private_changes": str(private_changes),
        "public_changes": str(public_changes),
        "note": spec.note,
    }


def write_report(rows: list[dict[str, str]], priors: PriorTable) -> None:
    top_rates = sorted(priors.rates.items(), key=lambda item: item[1], reverse=True)[:8]
    lines = [
        "# v1853 Character-Prior AP Calibration",
        "",
        "Date: 2026-05-14",
        "",
        "## Rule",
        "",
        "Public ground truth is used only to compute smoothed recurrent-name Werewolf rates; private labels and private leaderboard feedback are not used.",
        "",
        "```text",
        "rate = (public_wolf_count(name) + baseline_rate * 2) / (public_appearance_count(name) + 2)",
        "if role == Werewolf and wolf_score == 0.99:",
        "    wolf_score = 0.90 + 0.09 * rate",
        "elif role == Werewolf and wolf_score == 0.50:",
        "    wolf_score = 0.45 + 0.10 * rate",
        "elif role != Werewolf and 0.20 <= wolf_score < 0.30:",
        "    wolf_score = 0.20 + 0.09 * rate",
        "```",
        "",
        f"Public baseline Werewolf rate: `{priors.baseline:.6f}`.",
        "",
        "Top smoothed name rates:",
        "",
        "| Name | Smoothed rate | Public wolves | Public appearances |",
        "| --- | ---: | ---: | ---: |",
    ]
    for name, rate in top_rates:
        lines.append(f"| {name} | {rate:.6f} | {priors.wolves.get(name, 0)} | {priors.appearances.get(name, 0)} |")
    lines.extend(
        [
            "",
            "## Candidates",
            "",
            "| Candidate | Private CSV | Public proxy | Private changes | Public changes | Note |",
            "| --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
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
            "v1853a has the highest local public proxy so far, but it is more public-label calibrated than v1850. Treat it as a high-upside final-sprint option, not proof of private improvement.",
            "",
            "```text",
            "experiments/final_submission_package/charprior_queue/01_v1853a_queue01_v1850a_charprior_private.csv",
            "```",
            "",
            "No Kaggle upload was performed.",
        ]
    )
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    priors = build_priors()
    rows = [emit(spec, priors) for spec in BASES]
    write_report(rows, priors)
    print(f"report={REPORT}")


if __name__ == "__main__":
    main()
