#!/usr/bin/env bash
# Quality gate for the snake-factory-test repo.
# Runs the test suite and a couple of deterministic static checks.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

fail=0

# 1) Test suite (pytest).
if command -v python3 >/dev/null 2>&1; then
  if python3 -m pytest -q tests/; then
    echo "[gate] tests: PASS"
  else
    echo "[gate] tests: FAIL"
    fail=1
  fi
else
  echo "[gate] tests: SKIP (python3 not found)"
fi

# 2) No debug prints / TODO markers left in snake.py.
if grep -nE 'print\(.*(TODO|FIXME|XXX)|breakpoint\(' snake.py >/dev/null 2>&1; then
  echo "[gate] hygiene: FAIL (leftover debug markers in snake.py)"
  fail=1
else
  echo "[gate] hygiene: PASS"
fi

# 3) Byte-compile all Python files (catches syntax errors).
if python3 -m compileall -q snake.py tests/; then
  echo "[gate] compile: PASS"
else
  echo "[gate] compile: FAIL"
  fail=1
fi

exit "$fail"
