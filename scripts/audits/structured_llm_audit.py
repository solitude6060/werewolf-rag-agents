#!/usr/bin/env python3
"""Structured local-LLM audit for Werewolf submissions.

This is a compliant HW2 experiment:
- local Ollama only (no external API)
- no training/fine-tuning
- intended for qwen3.5:9b / deepseek-r1:14b class models (<12GB files)
- multi-agent structure: deterministic RAG/evidence agent + local LLM analyst +
  conservative scoring solver.

The LLM is not asked to replace the whole solver.  It produces a structured
evidence audit per game, and the downstream solver can decide whether to adjust
wolf_score ordering only.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PROJECT_ROOT.parent

# Reuse the battle-tested feature extractor from the experiment workspace while
# keeping this script runnable via `uv run` inside `werewolf-project/`.
sys.path.insert(0, str(REPO_ROOT / "experiments" / "scripts"))
import werewolf_variants as variants  # type: ignore

DATA = PROJECT_ROOT / "data" / "raw" / "Werewolf_Prediction_Dataset"
RUNS = REPO_ROOT / "experiments" / "llm_runs"
variants.DATA = DATA

by_game = variants.by_game
constraints = variants.constraints
features = variants.features
read_roles = variants.read_roles


ROLE_RAG = """RAG: Werewolf role/rule handbook
- Werewolf: knows teammates; wins by misleading village; avoids being exposed by true Seer/Medium.
- Seer: gets night divinations; true Seer reports should be internally consistent over days.
- Medium: learns executed players' identities; true Medium reports should track lynch outcomes.
- Madman: human for Wolf-AP, but aligned with wolves; often fakes Seer/Medium or injects false reports.
- Hunter: protects at night; can be suspicious in speech but is not a wolf unless other evidence is strong.
- Night-killed players cannot be Werewolf under normal rules: wolves do not kill teammates.
- Do not assume a role label is correct; rank wolf likelihood from behavioral/evidence consistency.
"""


PROMPT_RULES = """You are the Local LLM Analyst in an offline multi-agent homework system.
Use structured reasoning, but keep it compact and evidence-grounded.

You are NOT a summarizer. Your only job is to fill the required `players` array
with wolf-likelihood audits for the exact input players.

Required output: ONLY JSON matching the schema, no markdown.
Schema:
{
  "game_index": "01",
  "player_count": 16,
  "players": [
    {
      "character": "exact input name",
      "wolf_prob": 0.0,
      "wolf_rank": 1,
      "nonwolf_lock": false,
      "key_evidence": ["short evidence phrases"],
      "risk_note": "short reason"
    }
  ],
  "global_checks": ["short consistency checks"]
}

Scoring guidance:
- wolf_prob is for Wolf-AP ordering, not the final role assignment.
- Give likely wolves >=0.70, plausible wolves 0.45-0.69, unlikely wolves <=0.25.
- If night-killed/attacked, set nonwolf_lock=true AND wolf_prob<=0.05. This is a hard rule.
- Madman is NOT a Wolf-AP true positive; if you infer Madman/fake special, usually wolf_prob<=0.20 unless evidence suggests actual wolf fake-claiming.
- Be conservative: do not boost many players; identify the top 2-3 wolf candidates.
- Include EVERY exact input player exactly once. Do not summarize only top suspects.
- `player_count` must equal the number of input players, and `len(players)` must equal `player_count`.
"""


AUDIT_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "game_index": {"type": "string"},
        "player_count": {"type": "integer"},
        "players": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "character": {"type": "string"},
                    "wolf_prob": {"type": "number"},
                    "wolf_rank": {"type": "integer"},
                    "nonwolf_lock": {"type": "boolean"},
                    "key_evidence": {"type": "array", "items": {"type": "string"}},
                    "risk_note": {"type": "string"},
                },
                "required": [
                    "character",
                    "wolf_prob",
                    "wolf_rank",
                    "nonwolf_lock",
                    "key_evidence",
                    "risk_note",
                ],
            },
        },
        "global_checks": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["game_index", "player_count", "players", "global_checks"],
}


def build_audit_prompt(split: str, idx: str, players: list[dict[str, str]]) -> str:
    txt = (DATA / split / f"{idx}.txt").read_text(encoding="utf-8")
    fs, events, snippets = features(txt, players)
    need = constraints(len(players))
    lines = []
    for p in players:
        ch = p["character"]
        f = fs[ch]
        lines.append(
            f"- {ch}: stmts={f['stmts']} seer_claim={f['seer_claim']} "
            f"medium_claim={f['medium_claim']} hunter_claim={f['hunter_claim']} "
            f"not_seer={f['not_seer']} not_medium={f['not_medium']} "
            f"black_against={f['black_result']} white_for={f['white_result']} "
            f"attacked={f['attacked']} retract={f['retract']}"
        )

    return f"""{PROMPT_RULES}

{ROLE_RAG}

Game index: {idx}
Split: {split}
Player count: {len(players)}
Required final role counts for reference: {json.dumps(need)}
Players, exact names:
{json.dumps([p["character"] for p in players], ensure_ascii=False)}

Deterministic Evidence Agent output:
{chr(10).join(lines)}

Chronological events:
{chr(10).join(events[:100])}

Retrieved transcript snippets:
{chr(10).join(snippets[:90])}

Return the JSON object now. Do not write prose before or after it.
"""


def parse_json(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    if raw.startswith("{"):
        return json.loads(raw)
    match = re.search(r"\{.*\}", raw, re.S)
    if not match:
        raise ValueError("no JSON object found")
    return json.loads(match.group(0))


def ollama_chat(model: str, prompt: str, temperature: float, timeout: int, num_ctx: int) -> str:
    body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a JSON-only local audit agent. "
                    "Never output markdown or prose. Return exactly one valid JSON object."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "format": AUDIT_JSON_SCHEMA,
        "think": False,
        "options": {
            "temperature": temperature,
            # Keep runtime VRAM below the HW2 12GB limit.  qwen3.5:9b with a
            # 32k context can exceed the limit on RTX 4090; 8k is enough for
            # retrieved snippets and stayed within the intended local-model lane.
            "num_ctx": num_ctx,
            "num_predict": 6000,
        },
    }
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/chat",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())
    return data.get("message", {}).get("content", "")


def run_audits(
    split: str,
    model: str,
    limit: int | None,
    force: bool,
    temperature: float,
    num_ctx: int,
) -> None:
    games = by_game(read_roles(split))
    keys = sorted(games)[:limit] if limit else sorted(games)
    RUNS.mkdir(parents=True, exist_ok=True)
    model_key = model.replace(":", "_")
    for idx in keys:
        cache = RUNS / f"{split}_{idx}_v129_structured_{model_key}.json"
        if cache.exists() and not force:
            print(f"[cache] {split} {idx} {model}")
            continue
        prompt = build_audit_prompt(split, idx, games[idx])
        t0 = time.time()
        obj: dict[str, Any] = {"model": model, "prompt_version": "v129_structured"}
        try:
            raw = ollama_chat(model, prompt, temperature=temperature, timeout=700, num_ctx=num_ctx)
            obj["raw"] = raw
            obj["parsed"] = parse_json(raw)
            obj["parsed"]["player_count_expected"] = len(games[idx])
            obj["parsed"]["complete"] = len(obj["parsed"].get("players", [])) == len(games[idx])
        except Exception as exc:
            obj["raw"] = obj.get("raw", "")
            obj["error"] = str(exc)
            obj["parsed"] = {"game_index": idx, "players": [], "global_checks": []}
        cache.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
        n = len(obj.get("parsed", {}).get("players", []))
        print(f"[llm] {split} {idx} {model} {time.time() - t0:.1f}s players={n}")


def norm(name: str) -> str:
    return "".join(ch.lower() for ch in name if ch.isalnum())


def load_audit(split: str, idx: str, character: str, model: str) -> dict[str, Any] | None:
    model_key = model.replace(":", "_")
    path = RUNS / f"{split}_{idx}_v129_structured_{model_key}.json"
    if not path.exists():
        return None
    parsed = json.loads(path.read_text(encoding="utf-8")).get("parsed", {})
    target = norm(character)
    for player in parsed.get("players", []):
        cand = norm(str(player.get("character", "")))
        if target in cand or cand in target:
            return player
    return None


def apply_audit(
    input_csv: Path,
    output: Path,
    split: str,
    model: str,
    alpha: float,
    min_conf_delta: float,
) -> None:
    """Blend base wolf_score with structured audit while preserving roles.

    Conservative gates:
    - attacked/nonwolf_lock can demote scores.
    - predicted Werewolf with audit >=0.55 gets a moderate AP boost.
    - non-Werewolf with audit >=0.80 is boosted only if base was already >=0.45
      (avoids noisy LLM-only promotions).
    """
    rows = list(csv.DictReader(input_csv.open(newline="", encoding="utf-8")))
    changes: list[str] = []
    for row in rows:
        audit = load_audit(split, row["index"], row["character"], model)
        if not audit:
            continue
        old = float(row["wolf_score"])
        prob = max(0.0, min(1.0, float(audit.get("wolf_prob", old))))
        new = old
        if audit.get("nonwolf_lock") and old > 0.05:
            new = min(old, 0.05)
        elif row["role"] == "Werewolf" and old < 0.55 and prob >= 0.55:
            new = max(old, 0.55 + 0.25 * (prob - 0.55))
        elif row["role"] != "Werewolf" and old >= 0.45 and prob >= 0.80:
            new = min(0.92, (1 - alpha) * old + alpha * prob)
        elif row["role"] == "Madman" and 0.05 < old < 0.45 and prob <= 0.20:
            # guarded replacement for failed v121: only when this structured audit
            # explicitly rates the player low as Wolf-AP target.
            new = 0.0

        if abs(new - old) >= min_conf_delta:
            row["wolf_score"] = f"{new:.6g}"
            changes.append(
                f'{row["index"]} {row["character"]}: {row["role"]} {old:.3f}->{new:.3f} '
                f'audit={prob:.2f} lock={bool(audit.get("nonwolf_lock"))}'
            )

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "index", "character", "role", "wolf_score"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"{output}: {len(rows)} rows, {len(changes)} changes")
    for change in changes:
        print("  " + change)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_run = sub.add_parser("run")
    p_run.add_argument("--split", choices=("public", "private"), required=True)
    p_run.add_argument("--model", default="qwen3.5:9b")
    p_run.add_argument("--limit", type=int)
    p_run.add_argument("--force", action="store_true")
    p_run.add_argument("--temperature", type=float, default=0.05)
    p_run.add_argument("--num-ctx", type=int, default=8192)

    p_apply = sub.add_parser("apply")
    p_apply.add_argument("input_csv", type=Path)
    p_apply.add_argument("--output", type=Path, required=True)
    p_apply.add_argument("--split", choices=("public", "private"), required=True)
    p_apply.add_argument("--model", default="qwen3.5:9b")
    p_apply.add_argument("--alpha", type=float, default=0.35)
    p_apply.add_argument("--min-conf-delta", type=float, default=0.005)

    args = parser.parse_args()
    if args.cmd == "run":
        run_audits(args.split, args.model, args.limit, args.force, args.temperature, args.num_ctx)
    else:
        apply_audit(args.input_csv, args.output, args.split, args.model, args.alpha, args.min_conf_delta)


if __name__ == "__main__":
    main()
