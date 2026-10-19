#!/usr/bin/env bash
set -euo pipefail

# Simple sandbox runner for validating candidate patches.
# Usage: ./tools/sandbox/run_sandbox.sh [patch_tarball_path] [report_dir]

PATCH_TARBALL=${1:-}
REPORT_DIR=${2:-reports/sandbox}

mkdir -p "$REPORT_DIR"
WORKDIR=$(mktemp -d)

echo "Cloning repo into sandbox: $WORKDIR"
git clone --depth 1 . "$WORKDIR"
cd "$WORKDIR"

if [ -n "$PATCH_TARBALL" ] && [ -f "$PATCH_TARBALL" ]; then
  echo "Applying patch tarball: $PATCH_TARBALL"
  tar -xzf "$PATCH_TARBALL" -C .
fi

RESULT=0
LOGFILE="$REPORT_DIR/run_$(date -u +%Y%m%dT%H%M%SZ).log"

{
  echo "Running linters and tests..."
  # Python linter
  if command -v flake8 >/dev/null 2>&1; then
    flake8 || RESULT=1
  fi
  # Go vet
  if [ -f "go.mod" ]; then
    if command -v go >/dev/null 2>&1; then
      go vet ./... || RESULT=1
    fi
  fi
  # Zig build
  if [ -f "build.zig" ] || [ -d "src/zig" ]; then
    if command -v zig >/dev/null 2>&1; then
      zig build || RESULT=1
    fi
  fi
  # Python tests
  if [ -d "tests" ]; then
    if command -v pytest >/dev/null 2>&1; then
      pytest -q || RESULT=1
    fi
  fi
  echo "RESULT=$RESULT"
} &> "$LOGFILE"

PROV="$REPORT_DIR/provenance_$(date -u +%Y%m%dT%H%M%SZ).json"
python - <<PY
import json, os
prov = {
  "timestamp": os.environ.get("TS", "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)"),
  "worker": os.environ.get("WORKER_ID", "local"),
  "result": {"rc": $RESULT},
  "logfile": "$LOGFILE"
}
json.dump(prov, open("$PROV","w"), indent=2)
PY

echo "Sandbox complete. Result code: $RESULT. Logs: $LOGFILE, provenance: $PROV"
exit $RESULT
