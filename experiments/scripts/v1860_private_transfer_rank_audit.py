#!/usr/bin/env python3
"""Rank final candidates with known private feedback and structural distance diagnostics.

This is not a Kaggle score predictor.  It is a small-sample audit that checks
whether the current portfolio order is contradicted by available private
feedback and candidate-distance evidence.
"""
from __future__ import annotations

import csv
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from local_score import score  # noqa: E402
from v1858_private_feedback_transfer_audit import KNOWN  # noqa: E402

OUT_CSV = Path("experiments/reports/v1860_private_transfer_rank_audit.csv")
OUT_MD = Path("experiments/reports/v1860_private_transfer_rank_audit.md")
MANIFEST = Path("experiments/final_submission_package/manifests/final_submission_pack_manifest.csv")
BASE_PUBLIC = Path("experiments/submissions/submission_v1824a_v1823a_plus_g24_thomas_trueseer_public.csv")
BASE_PRIVATE = Path("experiments/submissions/submission_v1824a_v1823a_plus_g24_thomas_trueseer_private.csv")
BASE_PRIVATE_SCORE = 0.47119
TOP3 = 0.50671

GROUPS = {
    "portfolio_queue",
    "balancedprior_queue",
    "balancedprior_fallback",
    "charprior_queue",
    "charprior_fallback",
    "lowtail_queue",
    "lowtail_fallback",
    "denoise_queue",
    "denoise_fallback",
    "rolecap_queue",
    "rolecap_fallback",
    "known_best_overlay",
    "known_best",
    "scoreonly_safe_queue",
}


@dataclass(frozen=True)
class Candidate:
    kind: str
    group: str
    order: str
    candidate: str
    private_score: float | None
    public_csv: Path
    private_csv: Path
    output_path: str


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def map_rows(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    return {(row["index"], row["character"]): row for row in read_rows(path)}


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def diff_features(candidate_csv: Path, baseline_csv: Path, prefix: str) -> dict[str, float]:
    cand = map_rows(candidate_csv)
    base = map_rows(baseline_csv)
    keys = sorted(set(cand) & set(base))
    if not keys:
        return {
            f"{prefix}_matched": 0.0,
            f"{prefix}_role_change_rate": 1.0,
            f"{prefix}_score_mae": 1.0,
            f"{prefix}_score_max_abs": 1.0,
            f"{prefix}_score_change_gt_0p05_rate": 1.0,
            f"{prefix}_high_wolf_rate": 1.0,
        }
    abs_diffs = [abs(float(cand[k]["wolf_score"]) - float(base[k]["wolf_score"])) for k in keys]
    role_changes = [1.0 if cand[k]["role"] != base[k]["role"] else 0.0 for k in keys]
    high_wolf = [1.0 if float(cand[k]["wolf_score"]) >= 0.5 else 0.0 for k in keys]
    return {
        f"{prefix}_matched": float(len(keys)),
        f"{prefix}_role_change_rate": mean(role_changes),
        f"{prefix}_score_mae": mean(abs_diffs),
        f"{prefix}_score_max_abs": max(abs_diffs),
        f"{prefix}_score_change_gt_0p05_rate": mean(1.0 if d > 0.05 else 0.0 for d in abs_diffs),
        f"{prefix}_high_wolf_rate": mean(high_wolf),
    }


def candidate_public_path(private_path: Path) -> Path:
    text = str(private_path)
    if text.endswith("_private.csv"):
        return Path(text[:-12] + "_public.csv")
    return Path(text.replace("private.csv", "public.csv"))


def load_candidates() -> list[Candidate]:
    candidates: list[Candidate] = []
    for item in KNOWN:
        candidates.append(
            Candidate(
                kind="known",
                group="known_private_feedback",
                order="",
                candidate=item.candidate,
                private_score=item.private_score,
                public_csv=item.public_csv,
                private_csv=item.private_csv,
                output_path=str(item.private_csv),
            )
        )

    manifest = read_rows(MANIFEST)
    seen: set[tuple[str, str]] = set()
    for row in manifest:
        if row["group"] not in GROUPS:
            continue
        source = Path(row["source_path"])
        public = candidate_public_path(source)
        if not public.exists() or not source.exists():
            continue
        key = (row["group"], row["candidate"])
        if key in seen:
            continue
        seen.add(key)
        candidates.append(
            Candidate(
                kind="future",
                group=row["group"],
                order=row["order"],
                candidate=row["candidate"],
                private_score=None,
                public_csv=public,
                private_csv=source,
                output_path=row["output_path"],
            )
        )
    return candidates


def feature_row(c: Candidate) -> dict[str, str | float]:
    public = score(c.public_csv)
    base_public_score = score(BASE_PUBLIC)
    features: dict[str, str | float] = {
        "kind": c.kind,
        "group": c.group,
        "order": c.order,
        "candidate": c.candidate,
        "private_score": "" if c.private_score is None else c.private_score,
        "public_score": public["final_score"],
        "public_f1": public["macro_f1"],
        "public_ap": public["ap"],
        "public_delta_vs_v1824a": public["final_score"] - base_public_score["final_score"],
        "public_ap_delta_vs_v1824a": public["ap"] - base_public_score["ap"],
        "output_path": c.output_path,
    }
    features.update(diff_features(c.public_csv, BASE_PUBLIC, "public"))
    features.update(diff_features(c.private_csv, BASE_PRIVATE, "private"))
    return features


def zscore_vectors(rows: list[dict[str, str | float]], feature_names: list[str]) -> dict[str, list[float]]:
    values = {name: [float(r[name]) for r in rows] for name in feature_names}
    means = {name: mean(vals) for name, vals in values.items()}
    stds = {}
    for name, vals in values.items():
        mu = means[name]
        var = mean((v - mu) ** 2 for v in vals)
        stds[name] = math.sqrt(var) or 1.0
    vectors = {}
    for r in rows:
        vectors[str(r["group"]) + ":" + str(r["candidate"])] = [
            (float(r[name]) - means[name]) / stds[name] for name in feature_names
        ]
    return vectors


def distance(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b, strict=True)))


def annotate_neighbors(rows: list[dict[str, str | float]]) -> None:
    feature_names = [
        "public_delta_vs_v1824a",
        "public_ap_delta_vs_v1824a",
        "public_role_change_rate",
        "public_score_mae",
        "private_role_change_rate",
        "private_score_mae",
        "private_score_change_gt_0p05_rate",
        "private_high_wolf_rate",
    ]
    vectors = zscore_vectors(rows, feature_names)
    known = [r for r in rows if r["kind"] == "known"]
    for row in rows:
        key = str(row["group"]) + ":" + str(row["candidate"])
        neighbors = []
        for k in known:
            if k is row:
                continue
            kkey = str(k["group"]) + ":" + str(k["candidate"])
            d = distance(vectors[key], vectors[kkey])
            neighbors.append((d, str(k["candidate"]), float(k["private_score"])))
        neighbors.sort(key=lambda x: x[0])
        nearest = neighbors[:3]
        if nearest:
            weighted_num = sum(score_ / (dist + 1e-6) for dist, _, score_ in nearest)
            weighted_den = sum(1.0 / (dist + 1e-6) for dist, _, _ in nearest)
            weighted_private = weighted_num / weighted_den
            nearest_text = "; ".join(f"{name}@{priv:.5f}/d={dist:.2f}" for dist, name, priv in nearest)
        else:
            weighted_private = float("nan")
            nearest_text = ""
        row["nearest_known_private_weighted"] = weighted_private
        row["nearest_known"] = nearest_text
        # Risk-adjusted local index: keep public upside, but penalize structural
        # distance from the current verified-best private submission.  This is a
        # ranking diagnostic only, not an expected private score.
        row["risk_adjusted_index"] = (
            float(row["public_delta_vs_v1824a"]) * 100.0
            - float(row["private_role_change_rate"]) * 1.5
            - float(row["private_score_mae"]) * 1.0
            - float(row["private_score_change_gt_0p05_rate"]) * 0.5
        )


def loo_mae(rows: list[dict[str, str | float]]) -> float:
    known = [r for r in rows if r["kind"] == "known"]
    if len(known) < 4:
        return float("nan")
    feature_names = [
        "public_delta_vs_v1824a",
        "public_ap_delta_vs_v1824a",
        "public_role_change_rate",
        "public_score_mae",
        "private_role_change_rate",
        "private_score_mae",
        "private_score_change_gt_0p05_rate",
        "private_high_wolf_rate",
    ]
    errors = []
    for holdout in known:
        train = [r for r in known if r is not holdout]
        pool = train + [holdout]
        vectors = zscore_vectors(pool, feature_names)
        hkey = str(holdout["group"]) + ":" + str(holdout["candidate"])
        neighbors = []
        for row in train:
            rkey = str(row["group"]) + ":" + str(row["candidate"])
            d = distance(vectors[hkey], vectors[rkey])
            neighbors.append((d, float(row["private_score"])))
        neighbors.sort(key=lambda x: x[0])
        top = neighbors[:3]
        pred = sum(score_ / (dist + 1e-6) for dist, score_ in top) / sum(1.0 / (dist + 1e-6) for dist, _ in top)
        errors.append(abs(pred - float(holdout["private_score"])))
    return mean(errors)


def fmt(value: str | float, digits: int = 4) -> str:
    if isinstance(value, str):
        return value
    if math.isnan(value):
        return "nan"
    return f"{value:.{digits}f}"


def main() -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    candidates = load_candidates()
    rows = [feature_row(c) for c in candidates]
    annotate_neighbors(rows)
    mae = loo_mae(rows)

    fields = [
        "kind",
        "group",
        "order",
        "candidate",
        "private_score",
        "public_score",
        "public_f1",
        "public_ap",
        "public_delta_vs_v1824a",
        "public_ap_delta_vs_v1824a",
        "public_role_change_rate",
        "public_score_mae",
        "private_role_change_rate",
        "private_score_mae",
        "private_score_max_abs",
        "private_score_change_gt_0p05_rate",
        "private_high_wolf_rate",
        "nearest_known_private_weighted",
        "risk_adjusted_index",
        "nearest_known",
        "output_path",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})

    future = [r for r in rows if r["kind"] == "future"]
    portfolio = [r for r in future if r["group"] == "portfolio_queue"]
    scoreonly = [r for r in future if r["group"] == "scoreonly_safe_queue"]
    future_by_index = sorted(future, key=lambda r: float(r["risk_adjusted_index"]), reverse=True)
    portfolio_by_order = sorted(portfolio, key=lambda r: int(str(r["order"])))
    scoreonly_by_order = sorted(scoreonly, key=lambda r: int(str(r["order"])))

    first = scoreonly_by_order[0] if scoreonly_by_order else (portfolio_by_order[0] if portfolio_by_order else None)
    lines = [
        "# v1860 Private-Transfer Rank Audit",
        "",
        "Date: 2026-05-14",
        "",
        "## Purpose",
        "",
        "Audit whether the current final portfolio order is contradicted by known private-feedback history and structural distance from the verified-best v1824a submission.  This is a decision audit, not a private leaderboard predictor.",
        "",
        "## Completion boundary",
        "",
        f"The active goal is complete only after a real Kaggle private score greater than `{TOP3:.5f}` is reported.  This audit does not provide that proof.",
        "",
        "## Method summary",
        "",
        "- Known private-feedback rows: 11.",
        "- Future/package candidates scored: " + str(len(future)) + ".",
        "- Features: public proxy deltas, public/private role-change rate, score-difference magnitude, high-wolf-score rate, and nearest known private-feedback neighbors.",
        f"- Leave-one-known-out nearest-neighbor MAE: `{mae:.5f}`.  This is too large for completion proof, but useful for risk ranking.",
        "",
        "## Current portfolio order",
        "",
        "| Order | Candidate | Public proxy | Public delta | Private role-change rate vs v1824a | Score MAE vs v1824a | Nearest known private feedback | Upload path |",
        "| ---: | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for r in portfolio_by_order:
        lines.append(
            "| {order} | {candidate} | {public_score} | {delta} | {rolechg} | {mae_score} | {nearest} | `{path}` |".format(
                order=r["order"],
                candidate=r["candidate"],
                public_score=fmt(float(r["public_score"]), 4),
                delta=fmt(float(r["public_delta_vs_v1824a"]), 4),
                rolechg=fmt(float(r["private_role_change_rate"]), 4),
                mae_score=fmt(float(r["private_score_mae"]), 4),
                nearest=str(r["nearest_known"]),
                path=r["output_path"],
            )
        )
    lines.extend(
        [
            "",
            "## Score-only safe order",
            "",
            "| Order | Candidate | Public proxy | Public delta | Private role-change rate vs v1824a | Score MAE vs v1824a | Nearest known private feedback | Upload path |",
            "| ---: | --- | ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for r in scoreonly_by_order:
        lines.append(
            "| {order} | {candidate} | {public_score} | {delta} | {rolechg} | {mae_score} | {nearest} | `{path}` |".format(
                order=r["order"],
                candidate=r["candidate"],
                public_score=fmt(float(r["public_score"]), 4),
                delta=fmt(float(r["public_delta_vs_v1824a"]), 4),
                rolechg=fmt(float(r["private_role_change_rate"]), 4),
                mae_score=fmt(float(r["private_score_mae"]), 4),
                nearest=str(r["nearest_known"]),
                path=r["output_path"],
            )
        )
    lines.extend(
        [
            "",
            "## Top risk-adjusted package candidates",
            "",
            "The index below is only a ranking diagnostic: public delta is rewarded while distance from v1824a is penalized.  It is not an expected Kaggle score.",
            "",
            "| Rank | Group | Candidate | Public proxy | Risk-adjusted index | Private role-change rate | Upload path |",
            "| ---: | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for i, r in enumerate(future_by_index[:12], 1):
        lines.append(
            f"| {i} | {r['group']} | {r['candidate']} | {fmt(float(r['public_score']), 4)} | {fmt(float(r['risk_adjusted_index']), 4)} | {fmt(float(r['private_role_change_rate']), 4)} | `{r['output_path']}` |"
        )

    decision = "Prefer the score-only safe first upload when minimizing role-label transfer risk."
    rationale = "It keeps the v1856 balanced-prior public proxy while preserving the verified-best private role labels."
    if first is not None:
        first_path = str(first["output_path"])
    else:
        first_path = "MISSING_FIRST_UPLOAD"
        decision = "Package needs manual review."
        rationale = "Neither score-only safe nor portfolio first row was found in the manifest."

    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"{decision} {rationale}",
            "",
            "Recommended first upload:",
            "",
            "```text",
            first_path,
            "```",
            "",
            "If the user reports a real private score, use:",
            "",
            "```bash",
            "python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score <REAL_SCORE> --dry-run",
            "```",
            "",
            "## Artifacts",
            "",
            f"- `{OUT_CSV}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"known_rows={sum(1 for r in rows if r['kind'] == 'known')}")
    print(f"future_rows={len(future)}")
    print(f"loo_mae={mae:.5f}")
    print(f"recommended_first={first_path}")
    print(f"csv={OUT_CSV}")
    print(f"report={OUT_MD}")


if __name__ == "__main__":
    main()
