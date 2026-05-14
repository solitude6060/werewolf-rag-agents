#!/usr/bin/env python3
"""Generate v1838 confirmed-white AP overlay candidates.

Rationale: v1822 refined reveal audit found `confirmed_reveal` precision 4/4 on
public.  The corresponding private confirmed-white hit with non-trivial score is
g26 Wounded Soldier Simon, currently Villager/0.214 in v1824a-derived files.
This script only lowers that non-wolf score; it does not change any role count.
"""
from __future__ import annotations

import csv
from pathlib import Path

FIELDS = ["id", "index", "character", "role", "wolf_score"]
EV_FIELDS = [
    "candidate",
    "split",
    "id",
    "index",
    "character",
    "old_role",
    "new_role",
    "old_wolf_score",
    "new_wolf_score",
    "source",
    "rationale",
    "risk",
]
OUT = Path("experiments/submissions")

BASES = [
    (
        "v1838a_v1826a_confirmed_white_overlay",
        OUT / "submission_v1826a_g4_g29_apboost_push_private.csv",
        OUT / "submission_v1826a_g4_g29_apboost_push_public.csv",
        "primary-overlay on v1826a",
    ),
    (
        "v1838b_v1826d_confirmed_white_overlay",
        OUT / "submission_v1826d_g4_g29_g23_apboost_push_private.csv",
        OUT / "submission_v1826d_g4_g29_g23_apboost_push_public.csv",
        "conditional-overlay on v1826d",
    ),
    (
        "v1838c_v1829e_confirmed_white_overlay",
        OUT / "submission_v1829e_v1826d_plus_g17_g27_cleaner_hailmary_private.csv",
        OUT / "submission_v1829e_v1826d_plus_g17_g27_cleaner_hailmary_public.csv",
        "final-slot overlay on v1829e",
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


def patch_score(
    rows: list[dict[str, str]],
    ev: list[dict[str, str]],
    *,
    candidate: str,
    split: str,
    index: int,
    character: str,
    score: str,
    source: str,
    rationale: str,
    risk: str,
) -> None:
    row = next(r for r in rows if int(r["index"]) == index and r["character"] == character)
    old_role = row["role"]
    old_score = row["wolf_score"]
    row["wolf_score"] = score
    if old_score != score:
        ev.append(
            {
                "candidate": candidate,
                "split": split,
                "id": row["id"],
                "index": row["index"],
                "character": character,
                "old_role": old_role,
                "new_role": row["role"],
                "old_wolf_score": old_score,
                "new_wolf_score": score,
                "source": source,
                "rationale": rationale,
                "risk": risk,
            }
        )


def apply_private_overlay(rows: list[dict[str, str]], ev: list[dict[str, str]], candidate: str) -> None:
    patch_score(
        rows,
        ev,
        candidate=candidate,
        split="private",
        index=26,
        character="Wounded Soldier Simon",
        score="0.001",
        source="v1822_private_confirmed_reveal_g26_simon_white",
        rationale=(
            "v1822 refined reveal has private g26 `[Confirmed: Simon is white.]`; public confirmed-reveal "
            "precision is 4/4, and current row is already Villager but still has wolf_score 0.214."
        ),
        risk="If the confirmed line is from an unreliable perspective despite the label, this AP demote could hide a true wolf.",
    )


def apply_public_overlay(rows: list[dict[str, str]], ev: list[dict[str, str]], candidate: str) -> None:
    patch_score(
        rows,
        ev,
        candidate=candidate,
        split="public",
        index=18,
        character="Young Girl Liza",
        score="0.001",
        source="v1822_public_confirmed_reveal_g18_liza_white",
        rationale=(
            "Public counterpart for confirmed-white overlay: `[Confirmed: Liza is white.]` is correct in GT "
            "and lowers Villager wolf_score from 0.278 to 0.001."
        ),
        risk="Public proxy is only one score-moving row, so it validates direction but not private magnitude.",
    )


def emit(tag: str, private_base: Path, public_base: Path, note: str) -> None:
    private_rows = read(private_base)
    public_rows = read(public_base)
    ev: list[dict[str, str]] = []
    apply_private_overlay(private_rows, ev, tag)
    apply_public_overlay(public_rows, ev, tag)
    write(OUT / f"submission_{tag}_private.csv", private_rows)
    write(OUT / f"submission_{tag}_public.csv", public_rows)
    write_ev(OUT / f"submission_{tag}_evidence.csv", ev)
    print(f"{tag}\tprivate_base={private_base.name}\tpublic_base={public_base.name}\tnote={note}\tchanges={len(ev)}")


def main() -> None:
    for tag, private_base, public_base, note in BASES:
        emit(tag, private_base, public_base, note)


if __name__ == "__main__":
    main()
