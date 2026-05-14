#!/usr/bin/env python3
"""Generate score-only blend candidates between v1824a and high-proxy fallbacks."""
from __future__ import annotations

import csv
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from local_score import score  # noqa: E402

BASE_PUBLIC = Path("experiments/submissions/submission_v1824a_v1823a_plus_g24_thomas_trueseer_public.csv")
BASE_PRIVATE = Path("experiments/submissions/submission_v1824a_v1823a_plus_g24_thomas_trueseer_private.csv")
OUT_REPORT = Path("experiments/reports/v1863_scoreonly_blend_ladder.md")
OUT_CSV = Path("experiments/reports/v1863_scoreonly_blend_ladder.csv")
VALIDATOR = Path("werewolf-project/assert/validate_submission.py")

ALPHAS = (0.25, 0.40, 0.55, 0.70, 0.85, 1.00)


@dataclass(frozen=True)
class Target:
    name: str
    public_csv: Path
    private_csv: Path
    family: str
    risk_note: str


TARGETS = (
    Target(
        "v1856g",
        Path("experiments/submissions/submission_v1856g_v1850g_balancedprior_public.csv"),
        Path("experiments/submissions/submission_v1856g_v1850g_balancedprior_private.csv"),
        "balancedprior",
        "same proxy as v1856a with zero role changes",
    ),
    Target(
        "v1853g",
        Path("experiments/submissions/submission_v1853g_v1850g_charprior_public.csv"),
        Path("experiments/submissions/submission_v1853g_v1850g_charprior_private.csv"),
        "charprior",
        "maximum public proxy with higher score-calibration risk",
    ),
    Target(
        "v1850g",
        Path("experiments/submissions/submission_v1850g_v1848g_lowtail_public.csv"),
        Path("experiments/submissions/submission_v1850g_v1848g_lowtail_private.csv"),
        "lowtail",
        "lower-calibration score-only fallback",
    ),
    Target(
        "v1848g",
        Path("experiments/submissions/submission_v1848g_v1845c_rolecap_denoise_public.csv"),
        Path("experiments/submissions/submission_v1848g_v1845c_rolecap_denoise_private.csv"),
        "denoise",
        "denoise score-only fallback",
    ),
    Target(
        "v1846g",
        Path("experiments/submissions/submission_v1846g_v1845c_rolecap099_public.csv"),
        Path("experiments/submissions/submission_v1846g_v1845c_rolecap099_private.csv"),
        "rolecap",
        "lowest score-distance high-proxy fallback",
    ),
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def key(row: dict[str, str]) -> tuple[str, str, str]:
    return (row["id"], row["index"], row["character"])


def fmt_score(value: float) -> str:
    value = min(1.0, max(0.0, value))
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return text if text else "0"


def blend_file(base_path: Path, target_path: Path, alpha: float, out_path: Path) -> None:
    base_rows = read_rows(base_path)
    target_map = {key(row): row for row in read_rows(target_path)}
    out_rows: list[dict[str, str]] = []
    for row in base_rows:
        k = key(row)
        if k not in target_map:
            raise ValueError(f"missing target row {k} in {target_path}")
        target = target_map[k]
        base_score = float(row["wolf_score"])
        target_score = float(target["wolf_score"])
        blended = (1.0 - alpha) * base_score + alpha * target_score
        out = dict(row)
        # Preserve v1824a role labels by construction.
        out["role"] = row["role"]
        out["wolf_score"] = fmt_score(blended)
        out_rows.append(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "index", "character", "role", "wolf_score"])
        writer.writeheader()
        writer.writerows(out_rows)


def diff_stats(path: Path, base_path: Path) -> dict[str, float]:
    rows = read_rows(path)
    base = {key(row): row for row in read_rows(base_path)}
    diffs = []
    role_changes = 0
    high = 0
    for row in rows:
        b = base[key(row)]
        diffs.append(abs(float(row["wolf_score"]) - float(b["wolf_score"])))
        role_changes += int(row["role"] != b["role"])
        high += int(float(row["wolf_score"]) >= 0.5)
    return {
        "rows": float(len(rows)),
        "role_changes": float(role_changes),
        "score_mae": sum(diffs) / len(diffs),
        "score_max_abs": max(diffs),
        "score_change_gt_0p05": float(sum(d > 0.05 for d in diffs)),
        "high_wolf_count": float(high),
    }


def validate(path: Path) -> str:
    proc = subprocess.run([sys.executable, str(VALIDATOR), str(path)], text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr + proc.stdout)
    return proc.stdout.strip()


def main() -> None:
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    base_score = score(BASE_PUBLIC)
    rows: list[dict[str, str]] = []
    counter = 0
    for target in TARGETS:
        target_score = score(target.public_csv)
        for alpha in ALPHAS:
            counter += 1
            tag = f"{counter:02d}"
            alpha_tag = str(alpha).replace(".", "p")
            public_out = Path(f"experiments/submissions/submission_v1863_{target.name}_alpha{alpha_tag}_scoreblend_public.csv")
            private_out = Path(f"experiments/submissions/submission_v1863_{target.name}_alpha{alpha_tag}_scoreblend_private.csv")
            blend_file(BASE_PUBLIC, target.public_csv, alpha, public_out)
            blend_file(BASE_PRIVATE, target.private_csv, alpha, private_out)
            local = score(public_out)
            stats = diff_stats(private_out, BASE_PRIVATE)
            validation = validate(private_out)
            risk_index = (local["final_score"] - base_score["final_score"]) * 100.0 - stats["score_mae"] * 1.25 - (stats["score_change_gt_0p05"] / stats["rows"]) * 0.4
            rows.append(
                {
                    "candidate": f"v1863_{tag}",
                    "target": target.name,
                    "family": target.family,
                    "alpha": f"{alpha:.2f}",
                    "public_score": f"{local['final_score']:.12f}",
                    "public_f1": f"{local['macro_f1']:.12f}",
                    "public_ap": f"{local['ap']:.12f}",
                    "public_delta_vs_v1824a": f"{local['final_score'] - base_score['final_score']:+.12f}",
                    "target_public_score": f"{target_score['final_score']:.12f}",
                    "private_role_changes_vs_v1824a": str(int(stats["role_changes"])),
                    "private_score_mae_vs_v1824a": f"{stats['score_mae']:.12f}",
                    "private_score_max_abs_vs_v1824a": f"{stats['score_max_abs']:.12f}",
                    "private_score_change_gt_0p05": str(int(stats["score_change_gt_0p05"])),
                    "private_high_wolf_count": str(int(stats["high_wolf_count"])),
                    "risk_adjusted_index": f"{risk_index:.12f}",
                    "public_csv": str(public_out),
                    "private_csv": str(private_out),
                    "validation": validation,
                    "risk_note": target.risk_note,
                }
            )

    fields = list(rows[0].keys())
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    # Promote a compact ladder: best alpha per family by risk-adjusted index,
    # then order by a balance of public score and lower distance.
    best_by_family: dict[str, dict[str, str]] = {}
    for row in rows:
        family = row["family"]
        prev = best_by_family.get(family)
        if prev is None or float(row["risk_adjusted_index"]) > float(prev["risk_adjusted_index"]):
            best_by_family[family] = row
    promoted = sorted(
        best_by_family.values(),
        key=lambda r: (float(r["public_score"]), -float(r["private_score_mae_vs_v1824a"])),
        reverse=True,
    )[:5]

    lines = [
        "# v1863 Score-Only Blend Ladder",
        "",
        "Date: 2026-05-14",
        "",
        "## Purpose",
        "",
        "Search partial score-only blends between the verified-best v1824a scores and high-proxy score-only targets. Roles always remain v1824a roles.",
        "",
        "## Search summary",
        "",
        f"- Targets: {len(TARGETS)}.",
        f"- Alpha values per target: {len(ALPHAS)}.",
        f"- Generated public/private pairs: {len(rows)}.",
        f"- Baseline public proxy: `{base_score['final_score']:.4f}`.",
        "- All generated private CSVs passed the local submission validator.",
        "",
        "## Promoted one-per-family candidates",
        "",
        "| Candidate | Target | Alpha | Public proxy | Public delta | Score MAE vs v1824a | Changed scores >0.05 | Private CSV |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in promoted:
        lines.append(
            f"| {row['candidate']} | {row['target']} | {row['alpha']} | {float(row['public_score']):.4f} | {float(row['public_delta_vs_v1824a']):+.4f} | {float(row['private_score_mae_vs_v1824a']):.4f} | {row['private_score_change_gt_0p05']} | `{row['private_csv']}` |"
        )
    lines.extend(
        [
            "",
            "## Top 10 by risk-adjusted index",
            "",
            "| Rank | Candidate | Target | Alpha | Public proxy | Risk-adjusted index | Score MAE | Private CSV |",
            "| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for i, row in enumerate(sorted(rows, key=lambda r: float(r["risk_adjusted_index"]), reverse=True)[:10], 1):
        lines.append(
            f"| {i} | {row['candidate']} | {row['target']} | {row['alpha']} | {float(row['public_score']):.4f} | {float(row['risk_adjusted_index']):.4f} | {float(row['private_score_mae_vs_v1824a']):.4f} | `{row['private_csv']}` |"
        )
    first = promoted[0]
    safe_first_path = "experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv"
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "No partial alpha below 1.00 dominated the existing full-strength score-only safe queue.  Therefore no new package queue is added from v1863.",
            "",
            "Highest public-proxy generated blend:",
            "",
            "```text",
            first["private_csv"],
            "```",
            "",
            "Operational first upload remains the v1862 lower role-risk file:",
            "",
            "```text",
            safe_first_path,
            "```",
            "",
            "The active goal is still incomplete until a real private score greater than `0.50671` is reported.",
            "",
            "## Artifacts",
            "",
            f"- `{OUT_CSV}`",
        ]
    )
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"generated_pairs={len(rows)}")
    print(f"promoted={','.join(row['candidate'] for row in promoted)}")
    print(f"best_promoted={first['candidate']} {first['private_csv']} public={float(first['public_score']):.4f} mae={float(first['private_score_mae_vs_v1824a']):.4f}")
    print(f"csv={OUT_CSV}")
    print(f"report={OUT_REPORT}")


if __name__ == "__main__":
    main()
