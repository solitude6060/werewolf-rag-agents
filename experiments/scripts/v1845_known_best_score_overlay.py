#!/usr/bin/env python3
"""Generate score-only overlays on the verified private-best v1824a baseline.

This lane is distinct from v1842: it keeps the user-reported best private
submission's role labels intact, then applies only AP-oriented score moves from
previously audited event families.  It is intended as a safer fallback if the
v1826/v1842 structural stack is considered too risky.
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
    "source",
    "rationale",
    "risk",
    "text",
]
OUT = Path("experiments/submissions")
REPORT = Path("experiments/reports/v1845_known_best_score_overlay.md")


@dataclass(frozen=True)
class Variant:
    tag: str
    name: str
    include_medium: bool
    include_black_disagree: bool
    note: str


@dataclass(frozen=True)
class Event:
    source: str
    index: int
    target: str
    claim: str
    text: str


VARIANTS = [
    Variant(
        tag="v1845a_v1824a_strict_ap_overlay",
        name="strict",
        include_medium=False,
        include_black_disagree=False,
        note="v1824a plus v1839-style perfect-public-precision agree-direction AP moves.",
    ),
    Variant(
        tag="v1845b_v1824a_medium_ap_overlay",
        name="medium",
        include_medium=True,
        include_black_disagree=False,
        note="v1824a plus v1840-style Medium-result agree-direction AP moves.",
    ),
    Variant(
        tag="v1845c_v1824a_blackboost_score_overlay",
        name="blackboost",
        include_medium=True,
        include_black_disagree=True,
        note="v1824a plus v1842-style baseline-Seer black disagreement AP boosts.",
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


def write_ev(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def load_events(split: str, include_medium: bool) -> list[Event]:
    events: list[Event] = []
    seen: set[tuple[str, int, str, str]] = set()

    allowed_claimgraph = {"baseline_seer_result"}
    if include_medium:
        allowed_claimgraph.add("baseline_medium_result")

    for row in read(Path(f"experiments/reports/v1821_claimgraph_events_{split}.csv")):
        if row["source"] not in allowed_claimgraph:
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


def apply_overlay(
    rows: list[dict[str, str]], events: list[Event], variant: Variant, split: str
) -> list[dict[str, str]]:
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
            action = "black_boost_agree"
            new_score = "1.0"
        elif (
            variant.include_black_disagree
            and event.source == "baseline_seer_result"
            and event.claim == "black"
            and row["role"] != "Werewolf"
            and old_score < 1.0
        ):
            action = "black_boost_disagree"
            new_score = "1.0"

        if action is None or new_score is None:
            continue
        key = (event.index, event.target)
        previous = decisions.get(key, "unset")
        if previous != "unset" and previous is not None and previous[1] != new_score:
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
        if old_score == new_score:
            continue
        row["wolf_score"] = new_score
        if action == "black_boost_disagree":
            rationale = "Baseline-Seer black event conflicts with current non-Werewolf role; score-only AP boost, no role change."
            risk = "High variance: if the event is deceptive or perspectival, this becomes a severe false positive."
        elif event.source == "baseline_medium_result":
            rationale = "Medium-result event under the same score-moving agree-direction gate as v1840; role label unchanged."
            risk = "Medium-result public precision is lower than baseline-Seer; transfer may differ on private."
        else:
            rationale = "Perfect-public-precision event family under agree-direction score gate; role label unchanged."
            risk = "Private transfer is not guaranteed; this is a score-only AP overlay."
        evidence.append(
            {
                "candidate": variant.tag,
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


def run_quiet(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    return proc.stdout.strip()


def emit(variant: Variant) -> tuple[Path, Path, Path, list[dict[str, str]]]:
    private_rows = read(Path("experiments/submissions/submission_v1824a_v1823a_plus_g24_thomas_trueseer_private.csv"))
    public_rows = read(Path("experiments/submissions/submission_v1824a_v1823a_plus_g24_thomas_trueseer_public.csv"))
    evidence: list[dict[str, str]] = []
    evidence.extend(apply_overlay(private_rows, load_events("private", variant.include_medium), variant, "private"))
    evidence.extend(apply_overlay(public_rows, load_events("public", variant.include_medium), variant, "public"))

    private_out = OUT / f"submission_{variant.tag}_private.csv"
    public_out = OUT / f"submission_{variant.tag}_public.csv"
    evidence_out = OUT / f"submission_{variant.tag}_evidence.csv"
    write(private_out, private_rows)
    write(public_out, public_rows)
    write_ev(evidence_out, evidence)
    return private_out, public_out, evidence_out, evidence


def write_report(rows: list[dict[str, str]]) -> None:
    lines = [
        "# v1845 Known-Best Score-Only Overlay",
        "",
        "Date: 2026-05-14",
        "",
        "## Purpose",
        "",
        "Generate fallback candidates that preserve the verified-best v1824a role labels and change only `wolf_score`.",
        "",
        "This is safer than the v1826/v1842 structural queue when the user wants to protect the known `0.47119` private baseline, but it is less likely to create the large Macro-F1 lift needed to pass `0.50671`.",
        "",
        "## Candidates",
        "",
        "| Candidate | Private CSV | Public proxy | Private score changes | Public score changes |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['candidate']} | `{row['private_csv']}` | {row['public_proxy']} | "
            f"{row['private_changes']} | {row['public_changes']} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "Keep v1845 as a fallback/diagnostic group rather than replacing the maximum-upside v1842 recommendation.",
            "",
            "Recommended use:",
            "",
            "1. If the user wants maximum top-3 upside, still upload v1842a first.",
            "2. If v1842-style structural changes feel too risky, use v1845c as a score-only alternative on the verified-best baseline.",
            "3. If avoiding black-disagreement boosts, use v1845b or v1845a.",
            "",
            "No Kaggle upload was performed.",
        ]
    )
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    report_rows: list[dict[str, str]] = []
    for variant in VARIANTS:
        private_out, public_out, evidence_out, evidence = emit(variant)
        private_changes = sum(1 for row in evidence if row["split"] == "private")
        public_changes = sum(1 for row in evidence if row["split"] == "public")
        validation = run_quiet([sys.executable, "werewolf-project/assert/validate_submission.py", str(private_out)])
        public_score = run_quiet([sys.executable, "experiments/scripts/local_score.py", str(public_out), "--quiet"])
        print(
            f"{variant.tag}\tprivate_changes={private_changes}\tpublic_changes={public_changes}"
            f"\tvalidation={validation}\tpublic={public_score}"
        )
        report_rows.append(
            {
                "candidate": variant.tag.split("_", 1)[0],
                "private_csv": str(private_out),
                "public_proxy": public_score.rsplit("Score=", 1)[-1],
                "private_changes": str(private_changes),
                "public_changes": str(public_changes),
                "evidence_csv": str(evidence_out),
                "note": variant.note,
            }
        )
    write_report(report_rows)
    print(f"report={REPORT}")


if __name__ == "__main__":
    main()
