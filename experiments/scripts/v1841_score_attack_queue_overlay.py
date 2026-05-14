#!/usr/bin/env python3
"""Generate a five-file score-attack queue with the v1840 AP-only overlay.

This is a queue-shaped wrapper around the v1840 high-precision + Medium overlay
logic.  It applies the same score-only rule to each of the current final queue
families so tomorrow's remaining attempts can be uploaded from one ordered set.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path("experiments/scripts/v1840_high_precision_plus_medium_ap_overlay.py")
OUT = Path("experiments/submissions")


def load_v1840_module():
    spec = importlib.util.spec_from_file_location("v1840_overlay", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    module = load_v1840_module()
    bases = [
        module.BaseSpec(
            "v1841a_queue01_v1826a_attack_overlay",
            OUT / "submission_v1826a_g4_g29_apboost_push_private.csv",
            OUT / "submission_v1826a_g4_g29_apboost_push_public.csv",
            "attack queue order 1: v1826a plus v1840 AP-only overlay",
        ),
        module.BaseSpec(
            "v1841b_queue02_v1826b_attack_overlay",
            OUT / "submission_v1826b_g4_g29_g23_joachim_push_private.csv",
            OUT / "submission_v1826b_g4_g29_g23_joachim_push_public.csv",
            "attack queue order 2: v1826b plus v1840 AP-only overlay",
        ),
        module.BaseSpec(
            "v1841c_queue03_v1826d_attack_overlay",
            OUT / "submission_v1826d_g4_g29_g23_apboost_push_private.csv",
            OUT / "submission_v1826d_g4_g29_g23_apboost_push_public.csv",
            "attack queue order 3: v1826d plus v1840 AP-only overlay",
        ),
        module.BaseSpec(
            "v1841d_queue04_v1826c_attack_overlay",
            OUT / "submission_v1826c_g4_g29_g6_dualwhite_push_private.csv",
            OUT / "submission_v1826c_g4_g29_g6_dualwhite_push_public.csv",
            "attack queue order 4: v1826c plus v1840 AP-only overlay",
        ),
        module.BaseSpec(
            "v1841e_queue05_v1829e_attack_overlay",
            OUT / "submission_v1829e_v1826d_plus_g17_g27_cleaner_hailmary_private.csv",
            OUT / "submission_v1829e_v1826d_plus_g17_g27_cleaner_hailmary_public.csv",
            "attack queue order 5: v1829e plus v1840 AP-only overlay",
        ),
    ]
    for base in bases:
        module.emit(base)


if __name__ == "__main__":
    main()
