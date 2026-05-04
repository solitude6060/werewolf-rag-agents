#!/usr/bin/env python3
"""Compatibility wrapper for scripts/audits/structured_llm_audit.py."""
from __future__ import annotations

from pathlib import Path
from runpy import run_path

TARGET = Path(__file__).resolve().parent / "audits" / "structured_llm_audit.py"
run_path(str(TARGET), run_name="__main__")
