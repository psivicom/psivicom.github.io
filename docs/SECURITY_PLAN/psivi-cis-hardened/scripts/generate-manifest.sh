#!/bin/bash
# generate-manifest.sh — FAIR + CIS data integrity
# Usage: ./scripts/generate-manifest.sh
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"
mkdir -p data
find data -type f -not -name "manifest.sha256" -exec sha256sum {} \; | sort > data/manifest.sha256
echo "Wrote data/manifest.sha256 with $(wc -l < data/manifest.sha256) files"
cat data/manifest.sha256
