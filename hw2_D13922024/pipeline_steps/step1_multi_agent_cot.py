#!/usr/bin/env python3
"""Multi-agent CoT pipeline for Werewolf role prediction (HW2 compliant).

Architecture (Hermes-inspired structured agents):
  Stage 1  Evidence Agent (deterministic regex)        -> features dossier
  Stage 2  Analyst Agent  (qwen3.5:9b, CoT prompt)     -> wolf hypothesis JSON
  Stage 3  Verifier Agent (deepseek-r1:14b, skeptical) -> critique & override
  Stage 4  Solver         (rule-based consensus gate)  -> wolf_score adjustments

Compliance:
- local Ollama only, no external API, no fine-tuning
- both LLMs <12GB VRAM, called with `think: false`
- multi-agent + RAG (deterministic evidence as RAG context)
- pure post-processing of an anchor CSV; never reads private GT
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

sys.path.insert(0, str(Path(__file__).parent))
from werewolf_variants import (  # type: ignore
    DATA, RUNS, by_game, constraints, features, read_roles, lookup, resolve,
)


CACHE_TAG = "v200_macot"
ANALYST_MODEL = "qwen3.5:9b"
VERIFIER_MODEL = "gemma4:e4b"


ROLE_HANDBOOK = """RAG handbook (Werewolf rules):
- Werewolf wins by misleading village; coordinates with teammates; never killed at night by own team.
- Seer divines one player per night; reports BLACK = wolf, WHITE = human.
- Medium learns role of executed players; reports outcome of yesterday's lynch.
- Madman is human-team-side for Wolf-AP, but acts to mislead village; often FAKE-CLAIMS Seer or Medium.
- Hunter takes one player down on death; usually keeps a low profile to avoid attention.
- Night-killed players CANNOT be Werewolves (wolves never kill teammates).
- 12+ players: 2 wolves, plus Madman & Hunter; 13+ players: 3 wolves.
- True Seer/Medium reports must be internally consistent with eventual game outcomes.
- Multiple Seer COs implies at least one is fake (wolf or Madman).
"""


ANALYST_PROMPT = """You are the ANALYST AGENT in a multi-agent Werewolf-prediction homework.
Use explicit, compact step-by-step reasoning. Your output MUST be valid JSON only.

Methodology:
  Step 1  List all Seer claimants and the divinations they reported.
  Step 2  List all Medium claimants and the lynch results they reported.
  Step 3  List night-killed players (cannot be wolves).
  Step 4  Reconcile conflicts: which Seer is most plausible, which is fake (wolf or Madman).
  Step 5  Identify wolf candidates (must equal required wolf count, e.g. 2 or 3).
  Step 6  Tag every player with wolf_prob in [0,1] using ranking:
            >=0.85  high-confidence wolf
            0.55-0.84 plausible wolf
            0.25-0.54 ambiguous
            0.05-0.24 unlikely wolf
            <=0.04  locked non-wolf (attacked, true Seer, true Medium, Madman)
  Step 7  Final verdict per player.

Output JSON schema (strict, no markdown, no commentary outside JSON):
{
  "game_index": "<idx>",
  "thinking": {
    "seer_cos": [{"name": "...", "claims": ["..."]}],
    "medium_cos": [{"name": "...", "claims": ["..."]}],
    "attacked": ["..."],
    "true_seer_guess": "...",
    "fake_seer_guess": "... (Madman or wolf?)",
    "wolf_candidates": [{"name": "...", "evidence": "..."}]
  },
  "verdict": [
    {"name": "<exact input name>", "wolf_prob": 0.0, "role_guess": "Villager|Werewolf|Seer|Medium|Madman|Hunter", "confidence": 0.0, "rationale_short": "..."}
  ]
}

Hard rules:
- Use exact input names verbatim (do not paraphrase).
- "verdict" must include EVERY player exactly once.
- wolf_prob is for AP ranking, NOT role assignment. Madman/Hunter/Seer can have wolf_prob>0 if they look wolfish.
- Do not invent roles that violate required role counts.
"""


VERIFIER_PROMPT = """You are the VERIFIER AGENT. The Analyst has submitted a wolf hypothesis.
Your job is to challenge it skeptically before the Solver applies any score change.

Output JSON only. Schema:
{
  "weaknesses": ["short critiques of analyst reasoning, focus on missed evidence"],
  "supports": ["short pieces of evidence that DO support analyst's wolf candidates"],
  "override": [
    {"name": "<exact input name>", "suggested_wolf_prob": 0.0, "reason": "..."}
  ],
  "confirmed_wolves": ["names that you and analyst agree on as wolves"],
  "confirmed_nonwolves": ["names that you and analyst agree on as definitely not wolves"]
}

Guidance:
- Be skeptical. If the analyst rated someone wolf_prob>=0.7 but transcript evidence is weak, lower the suggested_wolf_prob.
- If a player was night-killed, they are NOT a wolf - put in confirmed_nonwolves.
- If the analyst missed a stronger wolf candidate, add via override.
- Use exact input names.
"""


def ollama_chat(model: str, prompt: str, timeout: int = 900,
                num_predict: int = 3500, num_ctx: int = 32768,
                temperature: float = 0.05, force_json: bool = True) -> str:
    body: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "think": False,
        "options": {
            "temperature": temperature,
            "num_ctx": num_ctx,
            "num_predict": num_predict,
        },
    }
    if force_json:
        body["format"] = "json"
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/chat",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())
    return data.get("message", {}).get("content", "")


def parse_json_strict(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
    match = re.search(r"\{.*\}", raw, re.S)
    if not match:
        raise ValueError("no json object found")
    return json.loads(match.group(0))


def parse_json_lenient(raw: str) -> dict[str, Any]:
    """Best-effort recovery when the strict JSON parser fails.

    Strategies:
    1. Try strict parse.
    2. Truncate at the last well-balanced bracket.
    3. Hand-extract verdict entries via regex; thinking is lost but verdict survives.
    """
    try:
        return parse_json_strict(raw)
    except Exception:
        pass

    s = raw
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\n?", "", s)
        s = re.sub(r"\n?```$", "", s)
    start = s.find("{")
    if start < 0:
        raise ValueError("no opening brace")
    depth = 0
    last_balance = -1
    in_str = False
    esc = False
    for i in range(start, len(s)):
        c = s[i]
        if esc:
            esc = False
            continue
        if c == "\\":
            esc = True
            continue
        if c == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                last_balance = i + 1
    if last_balance > 0:
        try:
            return json.loads(s[start:last_balance])
        except Exception:
            pass
    # Fallback: extract verdict entries directly from text.
    out: dict[str, Any] = {"verdict": []}
    pat = re.compile(
        r'\{\s*"name"\s*:\s*"([^"]+)"\s*,\s*"wolf_prob"\s*:\s*([0-9.]+)\s*,'
        r'\s*"role_guess"\s*:\s*"([^"]+)"\s*,\s*"confidence"\s*:\s*([0-9.]+)',
        re.S,
    )
    for m in pat.finditer(s):
        out["verdict"].append({
            "name": m.group(1),
            "wolf_prob": float(m.group(2)),
            "role_guess": m.group(3),
            "confidence": float(m.group(4)),
        })
    if out["verdict"]:
        return out
    raise ValueError("lenient parse failed")


def trim_chars(items: list[str], cap_chars: int) -> list[str]:
    out: list[str] = []
    used = 0
    for s in items:
        sl = len(s) + 1
        if used + sl > cap_chars:
            break
        out.append(s)
        used += sl
    return out


def build_evidence_dossier(idx: str, players: list[dict[str, str]], txt: str,
                           ev_chars: int = 2500, snip_chars: int = 5500) -> str:
    fs, ev, snippets = features(txt, players)
    need = constraints(len(players))
    feat_lines = []
    for p in players:
        ch = p["character"]
        f = fs[ch]
        feat_lines.append(
            f"- {ch}: stmts={f['stmts']} seer_claim={f['seer_claim']} "
            f"medium_claim={f['medium_claim']} hunter_claim={f['hunter_claim']} "
            f"not_seer={f['not_seer']} not_medium={f['not_medium']} "
            f"black_against={f['black_result']} white_for={f['white_result']} "
            f"attacked={f['attacked']} retract={f['retract']}"
        )
    ev_trim = trim_chars(ev, ev_chars)
    snip_trim = trim_chars(snippets, snip_chars)
    return f"""Game index: {idx}
Player count: {len(players)}
Required role counts: {json.dumps(need)}
Players (exact names): {json.dumps([p['character'] for p in players], ensure_ascii=False)}

Evidence Agent dossier (deterministic):
{chr(10).join(feat_lines)}

Chronological events:
{chr(10).join(ev_trim)}

Top transcript snippets (RAG retrieved):
{chr(10).join(snip_trim)}
"""


def build_analyst_prompt(idx: str, players, txt: str) -> str:
    # Schema/instructions placed AFTER the dossier so they survive any
    # left-side truncation when the model context shrinks.
    return (
        ROLE_HANDBOOK
        + "\n\n"
        + build_evidence_dossier(idx, players, txt)
        + "\n\n"
        + ANALYST_PROMPT
    )


def build_verifier_prompt(idx: str, players, txt: str, analyst: dict[str, Any]) -> str:
    return (
        ROLE_HANDBOOK
        + "\n\n"
        + build_evidence_dossier(idx, players, txt, ev_chars=1500, snip_chars=2500)
        + "\n\nAnalyst's hypothesis (full JSON):\n"
        + json.dumps(analyst, ensure_ascii=False)[:5000]
        + "\n\n"
        + VERIFIER_PROMPT
    )


def cache_path(split: str, idx: str, role: str, model: str) -> Path:
    return RUNS / f"{split}_{idx}_{CACHE_TAG}_{role}_{model.replace(':','_')}.json"


def run_analyst(split: str, idx: str, players, txt: str, force: bool) -> dict[str, Any] | None:
    p = cache_path(split, idx, "analyst", ANALYST_MODEL)
    if p.exists() and not force:
        try:
            return json.loads(p.read_text(encoding="utf-8")).get("parsed")
        except Exception:
            pass
    prompt = build_analyst_prompt(idx, players, txt)
    t0 = time.time()
    obj: dict[str, Any] = {"model": ANALYST_MODEL, "stage": "analyst"}
    try:
        raw = ollama_chat(ANALYST_MODEL, prompt, num_ctx=8192, num_predict=3600)
        obj["raw"] = raw
        obj["parsed"] = parse_json_lenient(raw)
    except Exception as exc:
        obj["error"] = str(exc)
        obj["parsed"] = None
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    parsed = obj.get("parsed")
    n = len(parsed.get("verdict", [])) if isinstance(parsed, dict) else 0
    print(f"[analyst] {split} {idx} {time.time()-t0:.1f}s verdicts={n}")
    return parsed


def run_verifier(split: str, idx: str, players, txt: str, analyst: dict[str, Any], force: bool) -> dict[str, Any] | None:
    p = cache_path(split, idx, "verifier", VERIFIER_MODEL)
    if p.exists() and not force:
        try:
            return json.loads(p.read_text(encoding="utf-8")).get("parsed")
        except Exception:
            pass
    if not isinstance(analyst, dict):
        return None
    prompt = build_verifier_prompt(idx, players, txt, analyst)
    t0 = time.time()
    obj: dict[str, Any] = {"model": VERIFIER_MODEL, "stage": "verifier"}
    try:
        raw = ollama_chat(VERIFIER_MODEL, prompt, num_ctx=8192, num_predict=2400)
        obj["raw"] = raw
        obj["parsed"] = parse_json_lenient(raw)
    except Exception as exc:
        obj["error"] = str(exc)
        obj["parsed"] = None
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    parsed = obj.get("parsed")
    n = (
        len(parsed.get("override", [])) + len(parsed.get("confirmed_wolves", []))
        if isinstance(parsed, dict)
        else 0
    )
    print(f"[verifier] {split} {idx} {time.time()-t0:.1f}s notes={n}")
    return parsed


def cmd_run(args) -> None:
    games = by_game(read_roles(args.split))
    keys = sorted(games)
    if args.limit:
        keys = keys[: args.limit]
    if args.only:
        targets = set(args.only)
        keys = [k for k in keys if k in targets]
    for idx in keys:
        players = games[idx]
        txt = (DATA / args.split / f"{idx}.txt").read_text(encoding="utf-8")
        analyst = run_analyst(args.split, idx, players, txt, args.force)
        if args.with_verifier and analyst is not None:
            run_verifier(args.split, idx, players, txt, analyst, args.force)


def norm(s: str) -> str:
    return "".join(c.lower() for c in s if c.isalnum())


def index_verdict(parsed: dict[str, Any] | None, key: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if not isinstance(parsed, dict):
        return out
    items = parsed.get(key, [])
    if not isinstance(items, list):
        return out
    for item in items:
        if isinstance(item, dict) and "name" in item:
            out[norm(str(item["name"]))] = item
    return out


def lookup_audit(audits: dict[str, dict[str, Any]], character: str) -> dict[str, Any] | None:
    target = norm(character)
    if target in audits:
        return audits[target]
    for cand_key, val in audits.items():
        if target in cand_key or cand_key in target:
            return val
    return None


def safe_float(value: Any, default: float) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return default


def cmd_apply(args) -> None:
    rows = list(csv.DictReader(args.input_csv.open(newline="", encoding="utf-8")))
    games = by_game(read_roles(args.split))
    by_index: dict[str, dict[str, dict[str, Any]]] = {}
    for idx in games:
        analyst_path = cache_path(args.split, idx, "analyst", ANALYST_MODEL)
        verifier_path = cache_path(args.split, idx, "verifier", VERIFIER_MODEL)
        analyst_parsed = json.loads(analyst_path.read_text(encoding="utf-8")).get("parsed") if analyst_path.exists() else None
        verifier_parsed = json.loads(verifier_path.read_text(encoding="utf-8")).get("parsed") if verifier_path.exists() else None
        by_index[idx] = {
            "analyst_verdict": index_verdict(analyst_parsed, "verdict"),
            "verifier_override": index_verdict(verifier_parsed, "override"),
            "verifier_confirmed_wolves": set(
                norm(n) for n in (verifier_parsed.get("confirmed_wolves", []) if isinstance(verifier_parsed, dict) else [])
            ),
            "verifier_confirmed_nonwolves": set(
                norm(n) for n in (verifier_parsed.get("confirmed_nonwolves", []) if isinstance(verifier_parsed, dict) else [])
            ),
        }

    changes: list[str] = []
    evidence: list[dict[str, str]] = []

    for row in rows:
        idx = row["index"]
        if idx not in by_index:
            continue
        bucket = by_index[idx]
        analyst = lookup_audit(bucket["analyst_verdict"], row["character"]) or {}
        override = lookup_audit(bucket["verifier_override"], row["character"]) or {}
        a_prob = safe_float(analyst.get("wolf_prob"), -1.0)
        v_prob = safe_float(override.get("suggested_wolf_prob"), -1.0)
        old = float(row["wolf_score"])
        char_norm = norm(row["character"])

        confirmed_wolf = char_norm in bucket["verifier_confirmed_wolves"]
        confirmed_nonwolf = char_norm in bucket["verifier_confirmed_nonwolves"]

        # Combine probabilities; if verifier override given, use it; else analyst.
        eff_prob = v_prob if v_prob >= 0 else a_prob
        # Direction from analyst alone (when verifier silent)
        analyst_only = (v_prob < 0) and (a_prob >= 0)

        new = old
        reason = ""
        # Trust anchor on extremes: never touch rows already in [0, 0.05] or
        # [args.protect_high, 1.0] — these are confidently locked by prior pipelines.
        in_protected_low = old <= 0.05
        in_protected_high = old >= args.protect_high or row["role"] == "Werewolf"

        if confirmed_nonwolf and not in_protected_low and not in_protected_high:
            # Lower a mid-range non-wolf row toward 0.05.
            new = min(old, 0.05)
            reason = "verifier_locked_nonwolf"
        elif row["role"] == "Werewolf" and eff_prob >= args.boost_thresh and old < args.ww_floor and not analyst_only:
            new = max(old, args.ww_floor)
            reason = "wolf_role_consensus_boost"
        elif (row["role"] != "Werewolf"
              and not in_protected_high
              and eff_prob >= args.high_thresh
              and old >= args.high_base
              and not analyst_only):
            new = max(old, min(args.high_cap, 0.5 * old + 0.5 * eff_prob))
            reason = "nonwolf_high_consensus_boost"
        elif row["role"] == "Madman" and 0.05 < old < 0.45 and 0 <= eff_prob <= args.low_thresh:
            new = 0.0
            reason = "madman_low_consensus_zero"
        elif (row["role"] != "Werewolf"
              and not in_protected_high
              and 0.45 <= old < args.protect_high
              and 0 <= eff_prob <= args.low_thresh):
            new = 0.45
            reason = "nonwolf_high_consensus_demote"

        if abs(new - old) >= args.min_delta:
            row["wolf_score"] = f"{new:.6g}"
            changes.append(f"{idx} {row['character']:30s} {row['role']:9s} {old:.3f}->{new:.3f}  ({reason})")
            evidence.append({
                "id": row["id"],
                "index": idx,
                "character": row["character"],
                "role": row["role"],
                "old_score": f"{old:.6g}",
                "new_score": f"{new:.6g}",
                "analyst_prob": f"{a_prob:.3f}" if a_prob >= 0 else "",
                "verifier_prob": f"{v_prob:.3f}" if v_prob >= 0 else "",
                "reason": reason,
            })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "index", "character", "role", "wolf_score"])
        writer.writeheader()
        writer.writerows(rows)
    evidence_path = args.output.with_suffix(".evidence.csv")
    with evidence_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "index", "character", "role", "old_score", "new_score", "analyst_prob", "verifier_prob", "reason"],
        )
        writer.writeheader()
        writer.writerows(evidence)
    print(f"{args.output}: {len(rows)} rows, {len(changes)} changes")
    print(f"{evidence_path}: {len(evidence)} evidence rows")
    for line in changes:
        print("  " + line)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run")
    run_p.add_argument("--split", choices=("public", "private"), required=True)
    run_p.add_argument("--limit", type=int)
    run_p.add_argument("--only", nargs="*", help="game indices to run, e.g. 01 02")
    run_p.add_argument("--force", action="store_true")
    run_p.add_argument("--with-verifier", action="store_true")
    run_p.set_defaults(func=cmd_run)

    apply_p = sub.add_parser("apply")
    apply_p.add_argument("input_csv", type=Path)
    apply_p.add_argument("--split", choices=("public", "private"), required=True)
    apply_p.add_argument("--output", type=Path, required=True)
    apply_p.add_argument("--boost-thresh", type=float, default=0.65)
    apply_p.add_argument("--high-thresh", type=float, default=0.80)
    apply_p.add_argument("--high-base", type=float, default=0.45)
    apply_p.add_argument("--high-cap", type=float, default=0.92)
    apply_p.add_argument("--low-thresh", type=float, default=0.15)
    apply_p.add_argument("--ww-floor", type=float, default=0.55)
    apply_p.add_argument("--protect-high", type=float, default=0.7,
                          help="never modify rows with old wolf_score >= this (anchor lock)")
    apply_p.add_argument("--min-delta", type=float, default=0.005)
    apply_p.set_defaults(func=cmd_apply)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
