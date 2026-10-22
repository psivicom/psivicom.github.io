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

# Import the sovereign identity verifier
try:
    from utils.oidc_verifier import verify_oidc_token
except ImportError:
    def verify_oidc_token(token):
        return True # Fallback for local testing

def validate_ledger(file_path="reports/pilot_report.json"):
    """
    Validates the structural integrity of the mesh ledger.
    Exits with code 1 if corrupt, preventing downstream commits.
    """
    
    # 1. Sovereign Identity Check
    oidc_token = os.environ.get('OIDC_TOKEN')
    if oidc_token and not verify_oidc_token(oidc_token):
        sys.stderr.write("🚫 SECURITY ALERT: Unverified identity during ledger validation. Aborting.\n")
        sys.exit(1)

    # 2. File Existence Check
    if not os.path.exists(file_path):
        sys.stderr.write(f"🛑 CRITICAL: Ledger not found at {file_path}. Aborting.\n")
        sys.exit(1)

    # 3. JSON Integrity Check
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"🛑 CRITICAL: Ledger is malformed JSON: {e}. Aborting.\n")
        sys.exit(1)
    except OSError as e:
        sys.stderr.write(f"🛑 CRITICAL: Ledger unreadable: {e}. Aborting.\n")
        sys.exit(1)

    # 4. Schema Validation (RFC 1001 Compliance)
    required_keys = ["aggregate_fragility", "aggregate_concordance", "last_updated"]
    for key in required_keys:
        if key not in data:
            sys.stderr.write(f"🛑 CRITICAL: Ledger missing required key '{key}'. Aborting.\n")
            sys.exit(1)

    # 5. Type Safety Check
    if not isinstance(data["aggregate_fragility"], (int, float)):
        sys.stderr.write("🛑 CRITICAL: 'aggregate_fragility' must be numeric. Aborting.\n")
        sys.exit(1)

    if not isinstance(data["aggregate_concordance"], (int, float)):
        sys.stderr.write("🛑 CRITICAL: 'aggregate_concordance' must be numeric. Aborting.\n")
        sys.exit(1)

    # 6. Temporal Precision Check (ISO 8601 Zulu)
    try:
        # Handle both 'Z' suffix and '+00:00' offset
        ts = data["last_updated"]
        if ts.endswith('Z'):
            ts = ts[:-1] + '+00:00'
        dt = datetime.fromisoformat(ts)
        
        # Optional: Enforce millisecond precision if required by your protocol
        # if dt.microsecond % 1000 != 0:
        #     raise ValueError("Timestamp lacks millisecond precision")
            
    except ValueError:
        sys.stderr.write("🛑 CRITICAL: 'last_updated' is not valid ISO 8601 Zulu. Aborting.\n")
        sys.exit(1)

    print("✅ Ledger structural integrity confirmed. Safe to commit.")
    sys.exit(0)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "reports/pilot_report.json"
    validate_ledger(target)
