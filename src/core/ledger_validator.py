# src/core/ledger_validator.py
"""
PSIVI AETHER Mesh - Ledger Circuit Breaker
Protocol: RFC 1001
Time Standard: ISO 8601 Zulu (millisecond precision)

Prevents sick agents from committing corrupt state to the mesh.
"""

import json
import sys
import os
from datetime import datetime, timezone

def validate_ledger(file_path="reports/pilot_report.json"):
    """
    Validates the structural integrity of the mesh ledger.
    Exits with code 1 if corrupt, preventing downstream commits.
    """
    if not os.path.exists(file_path):
        sys.stderr.write(f"🛑 CRITICAL: Ledger not found at {file_path}. Aborting.\n")
        sys.exit(1)

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"🛑 CRITICAL: Ledger is malformed JSON: {e}. Aborting.\n")
        sys.exit(1)
    except OSError as e:
        sys.stderr.write(f"🛑 CRITICAL: Ledger unreadable: {e}. Aborting.\n")
        sys.exit(1)

    required_keys = ["aggregate_fragility", "aggregate_concordance", "last_updated"]
    for key in required_keys:
        if key not in data:
            sys.stderr.write(f"🛑 CRITICAL: Ledger missing required key '{key}'. Aborting.\n")
            sys.exit(1)

    if not isinstance(data["aggregate_fragility"], (int, float)):
        sys.stderr.write("🛑 CRITICAL: 'aggregate_fragility' must be numeric. Aborting.\n")
        sys.exit(1)

    if not isinstance(data["aggregate_concordance"], (int, float)):
        sys.stderr.write("🛑 CRITICAL: 'aggregate_concordance' must be numeric. Aborting.\n")
        sys.exit(1)

    try:
        datetime.fromisoformat(data["last_updated"].replace("Z", "+00:00"))
    except ValueError:
        sys.stderr.write("🛑 CRITICAL: 'last_updated' is not valid ISO 8601 Zulu. Aborting.\n")
        sys.exit(1)

    print("✅ Ledger structural integrity confirmed. Safe to commit.")
    sys.exit(0)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "reports/pilot_report.json"
    validate_ledger(target)
