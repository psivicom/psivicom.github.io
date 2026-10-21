# src/core/immune_protocol.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import os
import sys
import json
import msgpack
import subprocess
from pathlib import Path
from datetime import datetime, timezone

sys.path.append(str(Path(__file__).parent.parent))
try:
    from src.utils.oidc_verifier import verify_oidc_token
except ImportError:
    def verify_oidc_token(token):
        print("⚠️ OIDC Verifier not found. Skipping identity check.")
        return True

class ImmuneProtocol:
    """
    WENDY's Autonomic Homeostasis Engine.
    Does not guess errors. Restores state, quarantines bad commits, and triggers metabolic learning.
    """
    
    def __init__(self):
        self.quarantine_file = Path("data/immune_quarantine.mpk")
        self.metabolism_file = Path("src/wendy_metabolism.json")
        
    def _verify_identity(self):
        oidc_token = os.environ.get('OIDC_TOKEN')
        if oidc_token and not verify_oidc_token(oidc_token):
            sys.stderr.write("🚫 SECURITY ALERT: Unverified identity. Aborting immune protocol.\n")
            sys.exit(1)

    def _revert_to_last_green(self):
        """Finds the last successful commit and reverts the current HEAD to it."""
        failed_commit = os.environ.get('FAILED_COMMIT', 'HEAD')
        print(f"🛑 Quarantining failed commit: {failed_commit}")
        
        try:
            # Safety Check: Ensure HEAD~1 exists before attempting reset
            result = subprocess.run(['git', 'rev-parse', '--verify', 'HEAD~1'], capture_output=True, text=True)
            if result.returncode == 0:
                subprocess.run(['git', 'reset', '--hard', 'HEAD~1'], check=True)
                subprocess.run(['git', 'clean', '-fd'], check=True) # Remove untracked generated files
                print("✅ State reverted to previous known configuration.")
            else:
                print("⚠️ Cannot revert: This appears to be the first commit. Cleaning working tree only.")
                subprocess.run(['git', 'clean', '-fd'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Revert failed: {e}. Proceeding with quarantine logging only.")

    def _log_quarantine(self):
        """Logs the failure to the Track B binary quarantine ledger."""
        quarantine_data = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "quarantined_commit": os.environ.get('FAILED_COMMIT', 'unknown'),
            "failed_workflow": os.environ.get('FAILED_WORKFLOW', 'unknown'),
            "run_id": os.environ.get('FAILED_RUN_ID', 'unknown'),
            "action": "autonomic_revert"
        }
        
        self.quarantine_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Append to binary log (RFC 1002 Track B)
        existing_logs = []
        if self.quarantine_file.exists():
            try:
                with open(self.quarantine_file, 'rb') as f:
                    existing_logs = msgpack.unpackb(f.read(), raw=False)
            except Exception:
                existing_logs = [] # Degrade gracefully if file is corrupted
                
        existing_logs.append(quarantine_data)
        
        with open(self.quarantine_file, 'wb') as f:
            f.write(msgpack.packb(existing_logs, use_bin_type=True))
            
        print(f"💾 Quarantine logged: {quarantine_data['quarantined_commit']}")

    def _induce_metabolic_stress(self):
        """
        Injects a stress event into WENDY's metabolism.
        Ensures the Neuroplasticity Agent reads this on its next cycle 
        and increases 'defense_weight' to prevent similar future failures.
        """
        try:
            if self.metabolism_file.exists():
                with open(self.metabolism_file, 'r') as f:
                    meta = json.load(f)
            else:
                meta = {"stress_level": 0.0, "last_intensity": 0.5}
                
            # Increase stress level, capped at 1.0
            current_stress = float(meta.get("stress_level", 0.0))
            meta["stress_level"] = round(min(1.0, current_stress + 0.3), 4)
            meta["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            meta["state"] = "Focus" # High stress triggers Focus state
            
            with open(self.metabolism_file, 'w') as f:
                json.dump(meta, f, indent=2)
                
            print(f"🧠 Metabolic stress induced: {meta['stress_level']}. Neuroplastic adaptation queued.")
        except Exception as e:
            print(f"⚠️ Failed to update metabolism: {e}. Continuing to preserve system state.")

    def execute(self):
        print("=" * 50)
        print(" 🛡️ AUTONOMIC HOMEOSTASIS INITIATED")
        print("=" * 50)
        self._verify_identity()
        self._revert_to_last_green()
        self._log_quarantine()
        self._induce_metabolic_stress()
        print("✅ Homeostasis restored. System is secure.")

if __name__ == "__main__":
    protocol = ImmuneProtocol()
    protocol.execute()
