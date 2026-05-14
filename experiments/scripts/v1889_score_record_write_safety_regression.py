#!/usr/bin/env python3
"""Regression-check score-record append safety without writing real score records."""
from __future__ import annotations

import csv
import importlib.util
from pathlib import Path
from types import ModuleType

ROUTER_PATH = Path("experiments/scripts/v1836_score_feedback_router.py")
OUT_CSV = Path("experiments/reports/v1889_score_record_write_safety_regression.csv")
OUT_MD = Path("experiments/reports/v1889_score_record_write_safety_regression.md")


def load_router() -> ModuleType:
    spec = importlib.util.spec_from_file_location("v1836_score_feedback_router", ROUTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {ROUTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def row(order: int, candidate: str, score: str, *, top3_hit: str = "no") -> dict[str, str]:
    return {
        "recorded_at_utc": f"2026-05-15T00:00:0{order}+00:00",
        "group": "scoreonly_safe_queue",
        "order": str(order),
        "candidate": candidate,
        "uploaded_path": f"experiments/final_submission_package/scoreonly_safe_queue/0{order}_{candidate}.csv",
        "score": score,
        "delta_vs_current_best": "+0.00000",
        "top3_hit": top3_hit,
        "recommended_next": "placeholder",
    }


def assert_allowed(router: ModuleType, rows: list[dict[str, str]], result: dict[str, str]) -> tuple[bool, str]:
    try:
        router.validate_append_allowed(rows, result)
    except SystemExit as exc:
        return False, str(exc)
    return True, "allowed"


def main() -> None:
    router = load_router()
    candidate = row(1, "v1856g", "0.47120")
    four_rows = [row(i, f"v18{i:02d}", f"0.47{i:03d}") for i in range(1, 5)]
    five_rows = [row(i, f"v18{i:02d}", f"0.47{i:03d}") for i in range(1, 6)]
    top3_rows = [row(1, "v1856g", "0.50672", top3_hit="yes")]

    cases = [
        {
            "label": "empty_ledger_allows_first_record",
            "rows": [],
            "result": candidate,
            "expect_allowed": True,
            "expect_fragment": "allowed",
        },
        {
            "label": "four_records_allows_fifth_record",
            "rows": four_rows,
            "result": row(5, "v1846g", "0.46400"),
            "expect_allowed": True,
            "expect_fragment": "allowed",
        },
        {
            "label": "five_records_rejects_sixth_record",
            "rows": five_rows,
            "result": row(6, "v9999", "0.46300"),
            "expect_allowed": False,
            "expect_fragment": "budget",
        },
        {
            "label": "existing_top3_hit_rejects_followup_record",
            "rows": top3_rows,
            "result": row(2, "v1853g", "0.51000"),
            "expect_allowed": False,
            "expect_fragment": "top-3 hit",
        },
        {
            "label": "exact_duplicate_rejected",
            "rows": [candidate],
            "result": candidate.copy(),
            "expect_allowed": False,
            "expect_fragment": "duplicate score record",
        },
        {
            "label": "same_candidate_different_score_allowed",
            "rows": [candidate],
            "result": {**candidate, "score": "0.47121"},
            "expect_allowed": True,
            "expect_fragment": "allowed",
        },
    ]

    rows_out: list[dict[str, str]] = []
    for case in cases:
        allowed, message = assert_allowed(router, case["rows"], case["result"])
        allowed_ok = allowed == case["expect_allowed"]
        message_ok = case["expect_fragment"] in message
        passed = allowed_ok and message_ok
        rows_out.append(
            {
                "label": case["label"],
                "expected_allowed": "yes" if case["expect_allowed"] else "no",
                "actual_allowed": "yes" if allowed else "no",
                "message": message,
                "pass": "yes" if passed else "no",
            }
        )

    failures = [item for item in rows_out if item["pass"] != "yes"]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = ["label", "expected_allowed", "actual_allowed", "message", "pass"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows_out)

    lines = [
        "# v1889 Score Record Write Safety Regression",
        "",
        "Date: 2026-05-15",
        "",
        "## Summary",
        "",
        f"- Scenarios checked: `{len(rows_out)}`",
        f"- Failures: `{len(failures)}`",
        "- Real score-record files touched: `no`",
        "",
        "## Matrix",
        "",
        "| Label | Expected allowed | Actual allowed | Pass |",
        "| --- | --- | --- | --- |",
    ]
    for item in rows_out:
        lines.append(
            f"| {item['label']} | {item['expected_allowed']} | {item['actual_allowed']} | {item['pass']} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "The score-record append guard rejects duplicate exact records, a sixth final-attempt record, and any follow-up write after a recorded top-3 hit while preserving valid first/fifth-record writes.",
            "",
            "## Completion boundary",
            "",
            "This regression protects the attempt ledger, but it does not complete the active score objective. Completion still requires a real Kaggle private score greater than `0.50671`.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"SCENARIOS={len(rows_out)}")
    print(f"FAILURES={len(failures)}")
    if failures:
        raise SystemExit("score record write safety regression failed")


if __name__ == "__main__":
    main()
