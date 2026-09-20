#!/usr/bin/env python3
"""Run every test_*() function in every tests/test_*.py. No dependencies.

The test files are written pytest-style, but pytest is not installed on
this machine, so without this the suite could not actually be run. Usage:

    python3 tests/run.py
"""
import importlib.util
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    passed, failures = 0, []
    for path in sorted(HERE.glob("test_*.py")):
        module = load(path)
        for name in sorted(vars(module)):
            if not name.startswith("test_"):
                continue
            fn = getattr(module, name)
            if not callable(fn):
                continue
            try:
                fn()
                passed += 1
            except Exception:
                failures.append((path.name, name, traceback.format_exc()))

    for fname, name, tb in failures:
        print(f"\nFAIL {fname}::{name}\n{tb}")
    print(f"{passed} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
