"""Restore retained responses into scratch outputs without overwriting a different run.

Added for the GitHub portfolio; no API calls and no changes to the submitted apparatus.
"""
from __future__ import annotations

from pathlib import Path
import shutil
import sys

from portfolio_verify import ROOT, sha256, verify_source_integrity


def main() -> int:
    try:
        verify_source_integrity()
        source = ROOT / "evidence/main-run"
        target = ROOT / "outputs/full_live"
        if target.is_symlink() or not target.resolve().is_relative_to(ROOT):
            raise ValueError("Refusing an out-of-repository/symlink output directory")
        names = ("parsed_model_outputs.jsonl", "raw_model_outputs.jsonl", "main_run_telemetry.csv")
        # Check all targets before copying anything. Never mix evidence with a different run.
        for name in names:
            destination = target / name
            if destination.is_symlink():
                raise ValueError(f"Refusing a symlink destination: {destination}")
            if destination.exists() and sha256(destination) != sha256(source / name):
                raise ValueError(f"Different output already exists: {destination}. Use a fresh working copy.")
        target.mkdir(parents=True, exist_ok=True)
        for name in names:
            destination = target / name
            if not destination.exists():
                shutil.copy2(source / name, destination)
        print("PASS: archived responses and live-run telemetry available in outputs/full_live.")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
