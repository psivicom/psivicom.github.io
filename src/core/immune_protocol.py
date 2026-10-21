# src/core/immune_protocol.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import os
import sys
import msgpack
from pathlib import Path
from datetime import datetime, timezone

sys.path.append(str(Path(__file__).parent.parent))
try:
    from src.utils.oidc_verifier import verify_oidc_token
except ImportError:
    def verify_oidc_token(token):
        return True

class ImmuneProtocol:
    def __init__(self):
        self.quarantine_file = Path("data/immune_quarantine.mpk")
        # UPGRADE: Track B Binary Metabolism File
        self.metabolism_file = Path("src/wendy_metabolism.mpk")
        
    def _verify_identity(self):
        oidc_token = os.environ.get('OIDC_TOKEN')
        if oidc_token and not verify_oidc_token(oidc_token):
            sys.stderr.write("🚫 SECURITY ALERT: Unverified identity.\n")
            sys.exit(1)

    def _log_quarantine(self):
        quarantine_data = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "quarantined_commit": os.environ.get('FAILED_COMMIT', 'unknown'),
            "failed_workflow": os.environ.get('FAILED_WORKFLOW', 'unknown'),
            "run_id": os.environ.get('FAILED_RUN_ID', 'unknown'),
            "action": "autonomic_observation"
        }
        
        self.quarantine_file.parent.mkdir(parents=True, exist_ok=True)
        existing_logs = []
        if self.quarantine_file.exists():
            try:
                with open(self.quarantine_file, 'rb') as f:
                    existing_logs = msgpack.unpackb(f.read(), raw=False)
            except Exception:
                existing_logs = []
                
        existing_logs.append(quarantine_data)
        with open(self.quarantine_file, 'wb') as f:
            f.write(msgpack.packb(existing_logs, use_bin_type=True))
        print(f"💾 Trauma logged: {quarantine_data['quarantined_commit']}")

    def _induce_metabolic_stress(self):
        try:
            # UPGRADE: Pure binary deserialization (Track B)
            if self.metabolism_file.exists():
                with open(self.metabolism_file, 'rb') as f:
                    meta = msgpack.unpackb(f.read(), raw=False)
            else:
                meta = {"stress_level": 0.0, "last_intensity": 0.5}
                
            current_stress = float(meta.get("stress_level", 0.0))
            meta["stress_level"] = round(min(1.0, current_stress + 0.2), 4)
            meta["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            meta["state"] = "Focus"
            
            # UPGRADE: Pure binary serialization (Track B)
            with open(self.metabolism_file, 'wb') as f:
                f.write(msgpack.packb(meta, use_bin_type=True))
                
            print(f"🧠 Metabolic stress induced: {meta['stress_level']}. Adaptation queued.")
        except Exception as e:
            print(f"⚠️ Failed to update metabolism: {e}")

    def execute(self):
        print("=" * 50)
        print(" 🛡️ AUTONOMIC OBSERVATION INITIATED")
        print("=" * 50)
        self._verify_identity()
        self._log_quarantine()
        self._induce_metabolic_stress()
        print("✅ Trauma recorded. System is learning.")

if __name__ == "__main__":
    protocol = ImmuneProtocol()
    protocol.execute()
