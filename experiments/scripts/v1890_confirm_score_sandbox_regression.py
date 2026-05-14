#!/usr/bin/env python3
"""Sandbox-regress the confirmed score-record write path without touching real records."""
from __future__ import annotations

import contextlib
import csv
import importlib.util
import io
import sys
import tempfile
from pathlib import Path
from types import ModuleType

ROUTER_PATH = Path("experiments/scripts/v1836_score_feedback_router.py")
REAL_RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
REAL_RECORDS_MD = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.md")
OUT_CSV = Path("experiments/reports/v1890_confirm_score_sandbox_regression.csv")
OUT_MD = Path("experiments/reports/v1890_confirm_score_sandbox_regression.md")


def load_router() -> ModuleType:
    spec = importlib.util.spec_from_file_location("v1836_score_feedback_router", ROUTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {ROUTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def run_router(router: ModuleType, args: list[str]) -> tuple[int, str]:
    old_argv = sys.argv[:]
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = 0
    try:
        sys.argv = [str(ROUTER_PATH), *args]
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                router.main()
            except SystemExit as exc:
                code = int(exc.code) if isinstance(exc.code, int) else 1
                if exc.code and not isinstance(exc.code, int):
                    print(exc.code, file=stderr)
    finally:
        sys.argv = old_argv
    return code, (stdout.getvalue() + stderr.getvalue()).strip()


def write_fake_records(router: ModuleType, count: int) -> None:
    rows = []
    for order in range(1, count + 1):
        rows.append(
            {
                "recorded_at_utc": f"2026-05-15T00:00:0{order}+00:00",
                "group": "scoreonly_safe_queue",
                "order": str(order),
                "candidate": f"v18{order:02d}",
                "uploaded_path": f"experiments/final_submission_package/scoreonly_safe_queue/0{order}_fake.csv",
                "score": f"0.47{order:03d}",
                "delta_vs_current_best": "+0.00000",
                "top3_hit": "no",
                "recommended_next": "placeholder",
            }
        )
    router.write_results(rows)


def main() -> None:
    real_records_before = REAL_RECORDS.exists() or REAL_RECORDS_MD.exists()
    rows_out: list[dict[str, str]] = []

    with tempfile.TemporaryDirectory(prefix="v1890_score_sandbox_") as tmp:
        tmpdir = Path(tmp)

        # Scenario 1: first confirmed write succeeds into the sandbox records.
        router = load_router()
        router.RESULTS_CSV = tmpdir / "records_first.csv"
        router.RESULTS_MD = tmpdir / "records_first.md"
        code, output = run_router(
            router,
            ["--group", "scoreonly_safe_queue", "--order", "1", "--score", "0.47120", "--confirm-real-score"],
        )
        first_rows = read_rows(router.RESULTS_CSV)
        pass_first = code == 0 and len(first_rows) == 1 and first_rows[0].get("score") == "0.47120" and "wrote=" in output
        rows_out.append(
            {
                "label": "first_confirm_write_succeeds_in_sandbox",
                "exit_code": str(code),
                "records": str(len(first_rows)),
                "message": output.splitlines()[-1] if output else "",
                "pass": "yes" if pass_first else "no",
            }
        )

        # Scenario 2: exact duplicate confirm is rejected and row count stays one.
        code, output = run_router(
            router,
            ["--group", "scoreonly_safe_queue", "--order", "1", "--score", "0.47120", "--confirm-real-score"],
        )
        dup_rows = read_rows(router.RESULTS_CSV)
        pass_dup = code != 0 and len(dup_rows) == 1 and "duplicate score record" in output
        rows_out.append(
            {
                "label": "duplicate_confirm_rejected_in_sandbox",
                "exit_code": str(code),
                "records": str(len(dup_rows)),
                "message": output.splitlines()[-1] if output else "",
                "pass": "yes" if pass_dup else "no",
            }
        )

        # Scenario 3: top-3 score writes a stop record, then follow-up writes are rejected.
        router_top3 = load_router()
        router_top3.RESULTS_CSV = tmpdir / "records_top3.csv"
        router_top3.RESULTS_MD = tmpdir / "records_top3.md"
        code, output = run_router(
            router_top3,
            ["--group", "scoreonly_safe_queue", "--order", "1", "--score", "0.50672", "--confirm-real-score"],
        )
        top3_rows = read_rows(router_top3.RESULTS_CSV)
        pass_top3 = code == 0 and len(top3_rows) == 1 and top3_rows[0].get("top3_hit") == "yes" and "STOP" in top3_rows[0].get("recommended_next", "")
        rows_out.append(
            {
                "label": "top3_confirm_writes_stop_record_in_sandbox",
                "exit_code": str(code),
                "records": str(len(top3_rows)),
                "message": top3_rows[0].get("recommended_next", "") if top3_rows else output,
                "pass": "yes" if pass_top3 else "no",
            }
        )
        code, output = run_router(
            router_top3,
            ["--group", "scoreonly_safe_queue", "--order", "2", "--score", "0.51000", "--confirm-real-score"],
        )
        top3_after_rows = read_rows(router_top3.RESULTS_CSV)
        pass_top3_reject = code != 0 and len(top3_after_rows) == 1 and "top-3 hit is already recorded" in output
        rows_out.append(
            {
                "label": "post_top3_followup_confirm_rejected_in_sandbox",
                "exit_code": str(code),
                "records": str(len(top3_after_rows)),
                "message": output.splitlines()[-1] if output else "",
                "pass": "yes" if pass_top3_reject else "no",
            }
        )

        # Scenario 4: exhausted five-record ledger rejects a sixth write.
        router_budget = load_router()
        router_budget.RESULTS_CSV = tmpdir / "records_budget.csv"
        router_budget.RESULTS_MD = tmpdir / "records_budget.md"
        write_fake_records(router_budget, 5)
        code, output = run_router(
            router_budget,
            ["--group", "scoreonly_safe_queue", "--order", "5", "--score", "0.46400", "--confirm-real-score"],
        )
        budget_rows = read_rows(router_budget.RESULTS_CSV)
        pass_budget = code != 0 and len(budget_rows) == 5 and "budget" in output
        rows_out.append(
            {
                "label": "sixth_confirm_rejected_in_sandbox",
                "exit_code": str(code),
                "records": str(len(budget_rows)),
                "message": output.splitlines()[-1] if output else "",
                "pass": "yes" if pass_budget else "no",
            }
        )

    real_records_after = REAL_RECORDS.exists() or REAL_RECORDS_MD.exists()
    official_untouched = real_records_before == real_records_after
    failures = [row for row in rows_out if row["pass"] != "yes"]
    if not official_untouched:
        failures.append({"label": "official_records_untouched", "pass": "no"})

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = ["label", "exit_code", "records", "message", "pass"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows_out)

    lines = [
        "# v1890 Confirm Score Sandbox Regression",
        "",
        "Date: 2026-05-15",
        "",
        "## Summary",
        "",
        f"- Scenarios checked: `{len(rows_out)}`",
        f"- Failures: `{len(failures)}`",
        f"- Official score records existed before: `{real_records_before}`",
        f"- Official score records existed after: `{real_records_after}`",
        f"- Official score records untouched: `{official_untouched}`",
        "",
        "## Matrix",
        "",
        "| Label | Exit code | Sandbox records | Pass |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in rows_out:
        lines.append(f"| {row['label']} | `{row['exit_code']}` | `{row['records']}` | {row['pass']} |")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "The real confirmed-write path can write a first sandbox score, rejects exact duplicates, records top-3 stop state, rejects post-top-3 follow-up writes, and rejects a sixth final-attempt write without touching official records.",
            "",
            "## Completion boundary",
            "",
            "This sandbox verifies local score-record behavior only. The active score objective still requires a real Kaggle private score greater than `0.50671`.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"SCENARIOS={len(rows_out)}")
    print(f"FAILURES={len(failures)}")
    print(f"OFFICIAL_RECORDS_UNTOUCHED={'yes' if official_untouched else 'no'}")
    if failures:
        raise SystemExit("confirm score sandbox regression failed")


if __name__ == "__main__":
    main()
