#!/usr/bin/env python3
"""Compatibility wrapper for scripts/postprocess/leaderboard_informed_fixes.py."""
from __future__ import annotations

from pathlib import Path
from runpy import run_path

TARGET = Path(__file__).resolve().parent / "postprocess" / "leaderboard_informed_fixes.py"
run_path(str(TARGET), run_name="__main__")
