#!/usr/bin/env python3
"""Candidate-focused local LLM audit.

Full-game structured JSON prompts made qwen3.5 drift into summaries. This script
uses a shorter, safer structure: only audit rows that can affect Wolf-AP ordering
from an existing submission (low-score predicted Werewolves, high-score
non-Werewolves, moderate-score Madmen).  It keeps the HW2 constraints:
local Ollama only, no training/fine-tuning, no external API.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parent
sys.path.insert(0, str(REPO_ROOT / "experiments" / "scripts"))
import werewolf_variants as variants  # type: ignore

DATA = PROJECT_ROOT / "data" / "raw" / "Werewolf_Prediction_Dataset"
RUNS = REPO_ROOT / "experiments" / "llm_runs"
variants.DATA = DATA

FIELDNAMES = ["id", "index", "character", "role", "wolf_score"]


def read_rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.open(newline="", encoding="utf-8")))


def select_candidates(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    by_idx: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        ws = float(row["wolf_score"])
        if (
            (row["role"] == "Werewolf" and ws < 0.5)
            or (row["role"] != "Werewolf" and ws >= 0.45)
            or (row["role"] == "Madman" and ws > 0.05)
        ):
            by_idx[row["index"]].append(row)
    return by_idx


def build_prompt(split: str, idx: str, candidates: list[dict[str, str]]) -> str:
    players = variants.by_game(variants.read_roles(split))[idx]
    txt = (DATA / split / f"{idx}.txt").read_text(encoding="utf-8")
    fs, events, _ = variants.features(txt, players)
    lines = []
    for row in candidates:
        ch = row["character"]
        f = fs[ch]
        lines.append(
            f"- {ch}: current_role={row['role']} current_ws={row['wolf_score']} "
            f"stmts={f['stmts']} seer_claim={f['seer_claim']} medium_claim={f['medium_claim']} "
            f"hunter_claim={f['hunter_claim']} black_against={f['black_result']} "
            f"white_for={f['white_result']} attacked={f['attacked']} retract={f['retract']}"
        )
    names = [row["character"] for row in candidates]
    return f"""Return ONLY valid JSON:
{{"audits":[{{"character":"exact candidate name","wolf_prob":0.0,"nonwolf_lock":false,"decision":"boost|keep|demote","evidence":"short evidence"}}]}}

You are NOT summarizing the game. Audit ONLY the candidate list for Wolf-AP ordering.
Use these rules:
- night-killed/attacked cannot be Werewolf: nonwolf_lock=true, wolf_prob<=0.05, decision=demote.
- predicted Werewolf with no hard non-wolf evidence should usually keep/boost above ordinary non-wolves.
- Madman is human for Wolf-AP; demote only if evidence supports fake special/non-wolf and no wolf evidence.
- Be conservative; if uncertain use decision=keep.

Game {idx} candidates: {json.dumps(names, ensure_ascii=False)}
Candidate features:
{chr(10).join(lines)}

Key events:
{chr(10).join(events[:50])}

JSON now:"""


def ollama_json(model: str, prompt: str, num_ctx: int, timeout: int = 180) -> dict[str, Any]:
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "format": "json",
        "think": False,
        "options": {"temperature": 0.0, "num_ctx": num_ctx, "num_predict": 1600},
    }
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/chat",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = json.loads(resp.read()).get("message", {}).get("content", "")
    return {"raw": raw, "parsed": json.loads(raw)}


def run(input_csv: Path, split: str, model: str, force: bool, num_ctx: int) -> None:
    rows = read_rows(input_csv)
    batches = select_candidates(rows)
    RUNS.mkdir(parents=True, exist_ok=True)
    model_key = model.replace(":", "_")
    for idx, candidates in sorted(batches.items()):
        cache = RUNS / f"{split}_{idx}_v130_candidate_{model_key}.json"
        if cache.exists() and not force:
            print(f"[cache] {split} {idx} candidates={len(candidates)}")
            continue
        prompt = build_prompt(split, idx, candidates)
        t0 = time.time()
        obj: dict[str, Any] = {"model": model, "prompt_version": "v130_candidate", "candidates": [c["character"] for c in candidates]}
        try:
            obj.update(ollama_json(model, prompt, num_ctx=num_ctx))
        except Exception as exc:
            obj["error"] = str(exc)
            obj["raw"] = obj.get("raw", "")
            obj["parsed"] = {"audits": []}
        cache.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[llm] {split} {idx} {model} {time.time()-t0:.1f}s audits={len(obj.get('parsed', {}).get('audits', []))}")


def norm(name: str) -> str:
    return "".join(ch.lower() for ch in name if ch.isalnum())


def load_audits(split: str, model: str) -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], dict[str, Any]] = {}
    model_key = model.replace(":", "_")
    for path in RUNS.glob(f"{split}_*_v130_candidate_{model_key}.json"):
        idx = path.name.split("_")[1]
        data = json.loads(path.read_text(encoding="utf-8"))
        for audit in data.get("parsed", {}).get("audits", []):
            out[(idx, norm(str(audit.get("character", ""))))] = audit
    return out


def apply(
    input_csv: Path,
    output: Path,
    split: str,
    model: str,
    ww_floor: float,
    allow_ww_demote: bool,
) -> None:
    rows = read_rows(input_csv)
    audits = load_audits(split, model)
    changes: list[str] = []
    for row in rows:
        audit = audits.get((row["index"], norm(row["character"])))
        old = float(row["wolf_score"])
        new = old
        if audit:
            prob = float(audit.get("wolf_prob", old))
            decision = str(audit.get("decision", "keep"))
            if row["role"] == "Werewolf" and old < ww_floor and not (
                allow_ww_demote and (audit.get("nonwolf_lock") or decision == "demote")
            ):
                # Safe default: do not let a noisy LLM overturn a role assignment;
                # use it mainly to confirm score monotonicity for predicted wolves.
                new = ww_floor
            elif audit.get("nonwolf_lock") or decision == "demote":
                new = min(old, 0.05)
            elif row["role"] == "Werewolf" and old < ww_floor and decision in {"boost", "keep"}:
                new = ww_floor
            elif row["role"] != "Werewolf" and old >= 0.45 and decision == "boost" and prob >= 0.75:
                new = max(old, min(0.9, prob))
        elif row["role"] == "Werewolf" and old < ww_floor:
            # Deterministic fallback: role and score should be monotonic for AP.
            new = ww_floor
        if new != old:
            row["wolf_score"] = f"{new:.6g}"
            changes.append(f"{row['index']} {row['character']}: {row['role']} {old:.3f}->{new:.3f}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)
    print(f"{output}: {len(rows)} rows, {len(changes)} changes")
    for change in changes:
        print("  " + change)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_run = sub.add_parser("run")
    p_run.add_argument("input_csv", type=Path)
    p_run.add_argument("--split", choices=("public", "private"), required=True)
    p_run.add_argument("--model", default="qwen3.5:9b")
    p_run.add_argument("--num-ctx", type=int, default=4096)
    p_run.add_argument("--force", action="store_true")
    p_apply = sub.add_parser("apply")
    p_apply.add_argument("input_csv", type=Path)
    p_apply.add_argument("--output", type=Path, required=True)
    p_apply.add_argument("--split", choices=("public", "private"), required=True)
    p_apply.add_argument("--model", default="qwen3.5:9b")
    p_apply.add_argument("--ww-floor", type=float, default=0.5)
    p_apply.add_argument(
        "--allow-ww-demote",
        action="store_true",
        help="allow LLM audit to demote predicted Werewolf rows; off by default because v120 showed role-side aggressiveness is risky",
    )
    args = parser.parse_args()
    if args.cmd == "run":
        run(args.input_csv, args.split, args.model, args.force, args.num_ctx)
    else:
        apply(args.input_csv, args.output, args.split, args.model, args.ww_floor, args.allow_ww_demote)


if __name__ == "__main__":
    main()
