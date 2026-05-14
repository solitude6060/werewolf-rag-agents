#!/usr/bin/env python3
"""Generate v1840 AP-only overlay: v1839 + score-moving baseline Medium results.

This is a slightly more aggressive variant of v1839.  It keeps the same safety
rule: only change wolf_score when the current role already agrees with the event
direction, and never change role labels.
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


@dataclass(frozen=True)
class Event:
    source: str
    index: int
    target: str
    claim: str
    text: str


BASES = [
    BaseSpec(
        "v1840a_v1826a_high_precision_medium_ap_overlay",
        OUT / "submission_v1826a_g4_g29_apboost_push_private.csv",
        OUT / "submission_v1826a_g4_g29_apboost_push_public.csv",
        "v1839 strict overlay plus score-moving baseline Medium AP demote on v1826a",
    ),
    BaseSpec(
        "v1840b_v1826d_high_precision_medium_ap_overlay",
        OUT / "submission_v1826d_g4_g29_g23_apboost_push_private.csv",
        OUT / "submission_v1826d_g4_g29_g23_apboost_push_public.csv",
        "v1839 strict overlay plus score-moving baseline Medium AP demote on v1826d",
    ),
    BaseSpec(
        "v1840c_v1829e_high_precision_medium_ap_overlay",
        OUT / "submission_v1829e_v1826d_plus_g17_g27_cleaner_hailmary_private.csv",
        OUT / "submission_v1829e_v1826d_plus_g17_g27_cleaner_hailmary_public.csv",
        "v1839 strict overlay plus score-moving baseline Medium AP demote on v1829e",
    ),
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


def load_events(split: str) -> list[Event]:
    events: list[Event] = []
    seen: set[tuple[str, int, str, str]] = set()

    for row in read(Path(f"experiments/reports/v1821_claimgraph_events_{split}.csv")):
        if row["source"] not in {"baseline_seer_result", "baseline_medium_result"}:
            continue
        key = (row["source"], int(row["index"]), row["target"], row["claim"])
        if key in seen:
            continue
        seen.add(key)
        events.append(Event(row["source"], int(row["index"]), row["target"], row["claim"], row["text"]))

    for row in read(Path(f"experiments/reports/v1822_refined_reveal_events_{split}.csv")):
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
        action = None
        new_score = None
        if event.claim == "white" and row["role"] != "Werewolf" and old_score > 0.05:
            action = "white_demote"
            new_score = "0.001"
        elif event.claim == "black" and row["role"] == "Werewolf" and old_score < 1.0:
            action = "black_boost"
            new_score = "1.0"
        if action is None or new_score is None:
            continue
        key = (event.index, event.target)
        previous = decisions.get(key, "unset")
        if previous != "unset" and previous is not None and previous[0] != action:
            decisions[key] = None
        elif previous == "unset":
            decisions[key] = (action, new_score, event)

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
        if event.source == "baseline_medium_result":
            source_note = "Medium-result event; lower public precision overall, but score-moving public application was correct."
        else:
            source_note = "Perfect-public-precision event family from v1821/v1822 audits."
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
                "rationale": f"{source_note} Score-only AP overlay; role label is unchanged.",
                "risk": "Private transfer may differ from public; this is not proof of a Kaggle gain.",
                "text": event.text,
            }
        )
    return evidence


def emit(spec: BaseSpec) -> None:
    private_rows = read(spec.private_base)
    public_rows = read(spec.public_base)
    evidence: list[dict[str, str]] = []
    evidence.extend(apply_overlay(private_rows, load_events("private"), spec.tag, "private"))
    evidence.extend(apply_overlay(public_rows, load_events("public"), spec.tag, "public"))
    write(OUT / f"submission_{spec.tag}_private.csv", private_rows)
    write(OUT / f"submission_{spec.tag}_public.csv", public_rows)
    write_ev(OUT / f"submission_{spec.tag}_evidence.csv", evidence)
    private_count = sum(1 for row in evidence if row["split"] == "private")
    public_count = sum(1 for row in evidence if row["split"] == "public")
    print(f"{spec.tag}\tprivate_changes={private_count}\tpublic_changes={public_count}\tnote={spec.note}")


def main() -> None:
    for spec in BASES:
        emit(spec)


if __name__ == "__main__":
    main()
