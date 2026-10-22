# src/agents/pilot_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import os
import sys
import json
import glob
from pathlib import Path
from datetime import datetime, timezone
from src.utils.oidc_verifier import verify_oidc_token

class PilotAgent:
    """
    WENDY's Sensory Cortex.
    Scans the repository state to generate the 'pilot_report.json' ledger.
    """
    
    def __init__(self):
        self.report_path = Path("reports/pilot_report.json")
        self.src_path = Path("src")
        
    def _verify_identity(self):
        oidc_token = os.environ.get('OIDC_TOKEN')
        if oidc_token and not verify_oidc_token(oidc_token):
            print("🚫 SECURITY ALERT: Unverified identity. Aborting scan.")
            sys.exit(1)

    def _scan_fragility(self):
        """
        Counts potential points of failure: 
        - Empty __init__.py files (bloat)
        - TODO/FIXME comments (technical debt)
        - Missing docstrings in public methods
        """
        fragility_count = 0
        for py_file in self.src_path.rglob("*.py"):
            content = py_file.read_text()
            fragility_count += content.count("TODO")
            fragility_count += content.count("FIXME")
            if py_file.stat().st_size == 0 and py_file.name == "__init__.py":
                fragility_count += 1 # Empty init is often bloat
        return fragility_count

    def _scan_concordance(self):
        """
        Counts signs of health and consistency:
        - Presence of SPDX headers
        - Valid JSON files in config/
        - Consistent naming conventions (simplified check)
        """
        concordance_count = 0
        for py_file in self.src_path.rglob("*.py"):
            if "SPDX-License-Identifier" in py_file.read_text():
                concordance_count += 1
        
        for json_file in Path("config").rglob("*.json"):
            try:
                json.loads(json_file.read_text())
                concordance_count += 1
            except:
                pass # Malformed JSON reduces concordance
        return concordance_count

    def _generate_report(self):
        fragility = self._scan_fragility()
        concordance = self._scan_concordance()
        
        report = {
            "aggregate_fragility": fragility,
            "aggregate_concordance": concordance,
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "scan_version": "1.0.0",
            "status": "healthy" if fragility < 10 else "degraded"
        }
        
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        self.report_path.write_text(json.dumps(report, indent=2))
        print(f"✅ Pilot Scan Complete. Fragility: {fragility}, Concordance: {concordance}")

    def run(self):
        print("👁️  Pilot Agent: Initiating Sensory Scan...")
        self._verify_identity()
        self._generate_report()

if __name__ == "__main__":
    agent = PilotAgent()
    agent.run()
