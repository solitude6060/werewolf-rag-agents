#!/usr/bin/env python3
"""Generate v1842 ultra attack queue: v1840 + baseline-Seer black disagreement boosts.

Public proxy showed that adding baseline-Seer black AP boosts even when the
current role is not Werewolf improved public score from 0.5412 to 0.5448.  This
script is intentionally high-variance: it changes only wolf_score, never role.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

FIELDS = ["id", "index", "character", "role", "wolf_score"]
EV_FIELDS = ["candidate", "split", "id", "index", "character", "role", "old_wolf_score", "new_wolf_score", "action", "source", "rationale", "risk", "text"]
OUT = Path("experiments/submissions")

@dataclass(frozen=True)
class BaseSpec:
    tag: str
    private_base: Path
    public_base: Path
    note: str

BASES = [
    BaseSpec("v1842a_queue01_v1826a_blackboost_attack", OUT/"submission_v1826a_g4_g29_apboost_push_private.csv", OUT/"submission_v1826a_g4_g29_apboost_push_public.csv", "order 1: v1826a + v1840 + baseline-Seer black boosts"),
    BaseSpec("v1842b_queue02_v1826b_blackboost_attack", OUT/"submission_v1826b_g4_g29_g23_joachim_push_private.csv", OUT/"submission_v1826b_g4_g29_g23_joachim_push_public.csv", "order 2: v1826b + v1840 + baseline-Seer black boosts"),
    BaseSpec("v1842c_queue03_v1826d_blackboost_attack", OUT/"submission_v1826d_g4_g29_g23_apboost_push_private.csv", OUT/"submission_v1826d_g4_g29_g23_apboost_push_public.csv", "order 3: v1826d + v1840 + baseline-Seer black boosts"),
    BaseSpec("v1842d_queue04_v1826c_blackboost_attack", OUT/"submission_v1826c_g4_g29_g6_dualwhite_push_private.csv", OUT/"submission_v1826c_g4_g29_g6_dualwhite_push_public.csv", "order 4: v1826c + v1840 + baseline-Seer black boosts"),
    BaseSpec("v1842e_queue05_v1829e_blackboost_attack", OUT/"submission_v1829e_v1826d_plus_g17_g27_cleaner_hailmary_private.csv", OUT/"submission_v1829e_v1826d_plus_g17_g27_cleaner_hailmary_public.csv", "order 5: v1829e + v1840 + baseline-Seer black boosts"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows([{k: row[k] for k in FIELDS} for row in rows])


def write_ev(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def trusted_events(split: str):
    # v1839/v1840 demote/boost sources plus medium score-moving safety gate.
    for row in read(Path(f"experiments/reports/v1821_claimgraph_events_{split}.csv")):
        if row["source"] in {"baseline_seer_result", "baseline_medium_result"}:
            yield row["source"], int(row["index"]), row["target"], row["claim"], row["text"]
    for row in read(Path(f"experiments/reports/v1822_refined_reveal_events_{split}.csv")):
        if row["refined_source"] in {"confirmed_reveal", "true_result_reveal"}:
            yield row["refined_source"], int(row["index"]), row["target"], row["claim"], row["text"]


def apply(rows: list[dict[str, str]], split: str, candidate: str) -> list[dict[str, str]]:
    by = {(int(r["index"]), r["character"]): r for r in rows}
    decisions: dict[tuple[int, str], tuple[str, str, str, str] | None] = {}
    for source, idx, target, claim, text in trusted_events(split):
        row = by.get((idx, target))
        if not row:
            continue
        old = float(row["wolf_score"])
        action = None
        new = None
        # v1840 safe demote/boost.
        if claim == "white" and row["role"] != "Werewolf" and old > 0.05:
            action, new = "white_demote", "0.001"
        elif claim == "black" and row["role"] == "Werewolf" and old < 1.0:
            action, new = "black_boost_agree", "1.0"
        # v1842 extra: only baseline-Seer black boosts when role disagrees.
        elif source == "baseline_seer_result" and claim == "black" and row["role"] != "Werewolf" and old < 1.0:
            action, new = "black_boost_disagree", "1.0"
        if not action or not new:
            continue
        key = (idx, target)
        prev = decisions.get(key, "unset")
        if prev != "unset" and prev is not None and prev[0] != action:
            decisions[key] = None
        elif prev == "unset":
            decisions[key] = (action, new, source, text)
    evidence=[]
    for key, dec in sorted(decisions.items()):
        if dec is None:
            continue
        action, new, source, text = dec
        row = by[key]
        old = row["wolf_score"]
        row["wolf_score"] = new
        if old == new:
            continue
        if action == "black_boost_disagree":
            rationale = "Baseline-Seer black event points to a possible Werewolf despite current role disagreement; AP-only boost, no role change."
            risk = "High variance: if this is perspectival or false, it creates a severe AP false positive."
        else:
            rationale = "v1840 AP-only safety gate; role label unchanged."
            risk = "Private transfer may differ from public; not proof of a Kaggle gain."
        evidence.append({
            "candidate": candidate,
            "split": split,
            "id": row["id"],
            "index": row["index"],
            "character": row["character"],
            "role": row["role"],
            "old_wolf_score": old,
            "new_wolf_score": new,
            "action": action,
            "source": source,
            "rationale": rationale,
            "risk": risk,
            "text": text,
        })
    return evidence


def emit(spec: BaseSpec) -> None:
    pr = read(spec.private_base)
    pu = read(spec.public_base)
    ev=[]
    ev.extend(apply(pr, "private", spec.tag))
    ev.extend(apply(pu, "public", spec.tag))
    write(OUT / f"submission_{spec.tag}_private.csv", pr)
    write(OUT / f"submission_{spec.tag}_public.csv", pu)
    write_ev(OUT / f"submission_{spec.tag}_evidence.csv", ev)
    pc=sum(1 for r in ev if r['split']=='private')
    uc=sum(1 for r in ev if r['split']=='public')
    print(f"{spec.tag}\tprivate_changes={pc}\tpublic_changes={uc}\tnote={spec.note}")


def main() -> None:
    for spec in BASES:
        emit(spec)

if __name__ == "__main__":
    main()
