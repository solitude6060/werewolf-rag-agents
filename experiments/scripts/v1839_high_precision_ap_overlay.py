#!/usr/bin/env python3
"""Generate v1839 high-precision AP-only overlay candidates.

Trusted event families:
- v1821 `baseline_seer_result` public precision: 10/10.
- v1822 `confirmed_reveal` public precision: 4/4.
- v1822 `true_result_reveal` public precision: 2/2.

The overlay only changes wolf_score when the current role already agrees with the
claim direction.  It never changes role labels or role counts.
"""
from __future__ import annotations

import csv
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
    "source",
    "rationale",
    "risk",
    "text",
]
OUT = Path("experiments/submissions")


@dataclass(frozen=True)
class BaseSpec:
    tag: str
    private_base: Path
    public_base: Path
    note: str


BASES = [
    BaseSpec(
        tag="v1839a_v1826a_high_precision_ap_overlay",
        private_base=OUT / "submission_v1826a_g4_g29_apboost_push_private.csv",
        public_base=OUT / "submission_v1826a_g4_g29_apboost_push_public.csv",
        note="strict high-precision AP overlay on v1826a",
    ),
    BaseSpec(
        tag="v1839b_v1826d_high_precision_ap_overlay",
        private_base=OUT / "submission_v1826d_g4_g29_g23_apboost_push_private.csv",
        public_base=OUT / "submission_v1826d_g4_g29_g23_apboost_push_public.csv",
        note="strict high-precision AP overlay on v1826d",
    ),
    BaseSpec(
        tag="v1839c_v1829e_high_precision_ap_overlay",
        private_base=OUT / "submission_v1829e_v1826d_plus_g17_g27_cleaner_hailmary_private.csv",
        public_base=OUT / "submission_v1829e_v1826d_plus_g17_g27_cleaner_hailmary_public.csv",
        note="strict high-precision AP overlay on v1829e",
    ),
]


@dataclass(frozen=True)
class Event:
    source: str
    index: int
    target: str
    claim: str
    text: str


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


def load_events(split: str) -> list[Event]:
    events: list[Event] = []
    seen: set[tuple[str, int, str, str]] = set()

    claimgraph_path = Path(f"experiments/reports/v1821_claimgraph_events_{split}.csv")
    for row in read(claimgraph_path):
        if row["source"] != "baseline_seer_result":
            continue
        key = (row["source"], int(row["index"]), row["target"], row["claim"])
        if key in seen:
            continue
        seen.add(key)
        events.append(Event(row["source"], int(row["index"]), row["target"], row["claim"], row["text"]))

    refined_path = Path(f"experiments/reports/v1822_refined_reveal_events_{split}.csv")
    for row in read(refined_path):
        if row["refined_source"] not in {"confirmed_reveal", "true_result_reveal"}:
            continue
        key = (row["refined_source"], int(row["index"]), row["target"], row["claim"])
        if key in seen:
            continue
        seen.add(key)
        events.append(Event(row["refined_source"], int(row["index"]), row["target"], row["claim"], row["text"]))

    return events


def apply_overlay(rows: list[dict[str, str]], events: list[Event], candidate: str, split: str) -> list[dict[str, str]]:
    by_key = {(int(row["index"]), row["character"]): row for row in rows}
    decisions: dict[tuple[int, str], tuple[str, str, Event] | None] = {}

    for event in events:
        row = by_key.get((event.index, event.target))
        if row is None:
            continue
        old_score = float(row["wolf_score"])
        action: str | None = None
        new_score: str | None = None
        if event.claim == "white" and row["role"] != "Werewolf" and old_score > 0.05:
            action = "white_demote"
            new_score = "0.001"
        elif event.claim == "black" and row["role"] == "Werewolf" and old_score < 1.0:
            action = "black_boost"
            new_score = "1.0"

        if action is None or new_score is None:
            continue

        key = (event.index, event.target)
        previous = decisions.get(key)
        if previous is None and key in decisions:
            continue
        if previous is not None and previous[0] != action:
            decisions[key] = None
            continue
        decisions.setdefault(key, (action, new_score, event))

    evidence: list[dict[str, str]] = []
    for key, decision in sorted(decisions.items()):
        if decision is None:
            continue
        action, new_score, event = decision
        row = by_key[key]
        old_score = row["wolf_score"]
        row["wolf_score"] = new_score
        if old_score == new_score:
            continue
        if action == "white_demote":
            rationale = (
                "High-precision event says this current non-Werewolf is white/human; demote wolf_score only."
            )
            risk = "If the event is fake or perspectival despite high public precision, the demote can hide a true wolf."
        else:
            rationale = "High-precision event says this current Werewolf is black; boost wolf_score only."
            risk = "If the event is fake or perspectival despite high public precision, the boost can create a false AP top rank."
        evidence.append(
            {
                "candidate": candidate,
                "split": split,
                "id": row["id"],
                "index": row["index"],
                "character": row["character"],
                "role": row["role"],
                "old_wolf_score": old_score,
                "new_wolf_score": new_score,
                "action": action,
                "source": event.source,
                "rationale": rationale,
                "risk": risk,
                "text": event.text,
            }
        )
    return evidence


def emit(spec: BaseSpec) -> None:
    private_rows = read(spec.private_base)
    public_rows = read(spec.public_base)
    evidence = []
    evidence.extend(apply_overlay(private_rows, load_events("private"), spec.tag, "private"))
    evidence.extend(apply_overlay(public_rows, load_events("public"), spec.tag, "public"))
    write(OUT / f"submission_{spec.tag}_private.csv", private_rows)
    write(OUT / f"submission_{spec.tag}_public.csv", public_rows)
    write_ev(OUT / f"submission_{spec.tag}_evidence.csv", evidence)
    private_count = sum(1 for row in evidence if row["split"] == "private")
    public_count = sum(1 for row in evidence if row["split"] == "public")
    print(
        f"{spec.tag}\tprivate_base={spec.private_base.name}\tpublic_base={spec.public_base.name}"
        f"\tnote={spec.note}\tprivate_changes={private_count}\tpublic_changes={public_count}"
    )


def main() -> None:
    for spec in BASES:
        emit(spec)


if __name__ == "__main__":
    main()
