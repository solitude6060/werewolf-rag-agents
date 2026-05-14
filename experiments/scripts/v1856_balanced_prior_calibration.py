#!/usr/bin/env python3
"""Generate v1856 balanced character-prior calibration candidates.

Selected from v1855 spec s0205:
- Only non-Werewolf 0.20 <= wolf_score < 0.30 rows are adjusted.
- Smoothed public name prior uses pseudo-count 16 and requires at least 2 public wolves.
- New score blends 75% prior-tier score with 25% existing score.
- Roles are never changed.
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
    "prior_tier_score",
    "new_wolf_score",
    "public_appearances",
    "public_wolves",
    "smoothed_rate",
    "action",
    "risk",
]
OUT = Path("experiments/submissions")
REPORT = Path("experiments/reports/v1856_balanced_prior_calibration.md")
GT = Path("werewolf-project/data/raw/Werewolf_Prediction_Dataset/public/roles_with_gt.csv")
PSEUDO = 16.0
MIN_WOLVES = 2
MID_ALPHA = 0.75
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
    BaseSpec("v1856a_queue01_v1850a_balancedprior", OUT / "submission_v1850a_queue01_v1848a_lowtail_private.csv", OUT / "submission_v1850a_queue01_v1848a_lowtail_public.csv", "v1850a plus balanced non-Werewolf mid-tier prior."),
    BaseSpec("v1856b_queue02_v1850b_balancedprior", OUT / "submission_v1850b_queue02_v1848b_lowtail_private.csv", OUT / "submission_v1850b_queue02_v1848b_lowtail_public.csv", "v1850b plus balanced non-Werewolf mid-tier prior."),
    BaseSpec("v1856c_queue03_v1850c_balancedprior", OUT / "submission_v1850c_queue03_v1848c_lowtail_private.csv", OUT / "submission_v1850c_queue03_v1848c_lowtail_public.csv", "v1850c plus balanced non-Werewolf mid-tier prior."),
    BaseSpec("v1856d_queue04_v1850d_balancedprior", OUT / "submission_v1850d_queue04_v1848d_lowtail_private.csv", OUT / "submission_v1850d_queue04_v1848d_lowtail_public.csv", "v1850d plus balanced non-Werewolf mid-tier prior."),
    BaseSpec("v1856e_queue05_v1850e_balancedprior", OUT / "submission_v1850e_queue05_v1848e_lowtail_private.csv", OUT / "submission_v1850e_queue05_v1848e_lowtail_public.csv", "v1850e plus balanced non-Werewolf mid-tier prior."),
    BaseSpec("v1856f_v1850f_balancedprior", OUT / "submission_v1850f_v1848f_lowtail_private.csv", OUT / "submission_v1850f_v1848f_lowtail_public.csv", "fallback v1850f plus balanced non-Werewolf mid-tier prior."),
    BaseSpec("v1856g_v1850g_balancedprior", OUT / "submission_v1850g_v1848g_lowtail_private.csv", OUT / "submission_v1850g_v1848g_lowtail_public.csv", "fallback v1850g plus balanced non-Werewolf mid-tier prior."),
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
        name: (wolves[name] + baseline * PSEUDO) / (appearances[name] + PSEUDO)
        for name in appearances
    }
    return PriorTable(baseline=baseline, appearances=dict(appearances), wolves=dict(wolves), rates=rates)


def apply(rows: list[dict[str, str]], candidate: str, split: str, priors: PriorTable) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    for row in rows:
        score = float(row["wolf_score"])
        if row["role"] == "Werewolf" or not (0.20 <= score < 0.30):
            continue
        name = base_name(row["character"])
        rate = priors.rates.get(name, priors.baseline)
        app = priors.appearances.get(name, 0)
        wolves = priors.wolves.get(name, 0)
        if wolves < MIN_WOLVES:
            rate = priors.baseline
        prior_tier_score = 0.20 + 0.09 * rate
        new_score = (1.0 - MID_ALPHA) * score + MID_ALPHA * prior_tier_score
        old = row["wolf_score"]
        row["wolf_score"] = f"{new_score:.6f}"
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
                "prior_tier_score": f"{prior_tier_score:.6f}",
                "new_wolf_score": row["wolf_score"],
                "public_appearances": str(app),
                "public_wolves": str(wolves),
                "smoothed_rate": f"{rate:.6f}",
                "action": "balanced_nonwerewolf_mid_prior_rerank",
                "risk": "Public-label name prior restricted to non-Werewolf mid-tier scores; lower overfit risk than v1853 but still calibration-based.",
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
    lines = [
        "# v1856 Balanced Character-Prior Calibration",
        "",
        "Date: 2026-05-14",
        "",
        "## Rule",
        "",
        "Selected from `experiments/reports/v1855_balanced_prior_search.md` as spec `s0205`.",
        "",
        "```text",
        "rate = (public_wolf_count(name) + baseline_rate * 16) / (public_appearance_count(name) + 16)",
        "if role != Werewolf and 0.20 <= wolf_score < 0.30:",
        "    prior_tier_score = 0.20 + 0.09 * rate  # baseline rate if public_wolf_count < 2",
        "    wolf_score = 0.25 * old_score + 0.75 * prior_tier_score",
        "```",
        "",
        f"Public baseline Werewolf rate: `{priors.baseline:.6f}`.",
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
            "v1856a is a balanced fallback between v1850a and v1853a: it has lower local proxy than v1853a, but the v1855 search found no no-leak heldout negatives for the selected rule.",
            "",
            "```text",
            "experiments/final_submission_package/balancedprior_queue/01_v1856a_queue01_v1850a_balancedprior_private.csv",
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
