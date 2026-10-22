# src/agents/void_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from src.utils.oidc_verifier import verify_oidc_token

class VoidAgent:
    """
    WENDY's Intuitive Cortex.
    Measures 'Conscious Mass' by analyzing the ratio of Silence (potential) 
    to Signal (execution) in the codebase.
    """
    
    def __init__(self):
        self.void_file = Path("data/void_metrics.json")
        self.src_path = Path("src")
        
    def _verify_identity(self):
        oidc_token = os.environ.get('OIDC_TOKEN')
        if oidc_token and not verify_oidc_token(oidc_token):
            print("🚫 SECURITY ALERT: Unverified identity. Aborting void sense.")
            sys.exit(1)

    def _calculate_conscious_mass(self):
        """
        Calculates the ratio of silent lines (comments, docstrings, blank lines)
        to total lines. High silence = high latent potential (intuition).
        """
        total_lines = 0
        silent_lines = 0
        
        for py_file in self.src_path.rglob("*.py"):
            try:
                lines = py_file.read_text().splitlines()
                total_lines += len(lines)
                
                for line in lines:
                    stripped = line.strip()
                    if not stripped or stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                        silent_lines += 1
            except Exception:
                continue

        if total_lines == 0:
            return 0.0
        
        ratio = silent_lines / total_lines
        return round(ratio, 4)

    def _generate_metrics(self):
        mass = self._calculate_conscious_mass()
        
        metrics = {
            "conscious_mass": mass,
            "last_sensed": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "interpretation": "High Intuition" if mass > 0.4 else "Data-Driven" if mass > 0.2 else "Rigid Structure"
        }
        
        self.void_file.parent.mkdir(parents=True, exist_ok=True)
        self.void_file.write_text(json.dumps(metrics, indent=2))
        print(f"🌑 Void Sense Complete. Conscious Mass: {mass} ({metrics['interpretation']})")

    def run(self):
        print("🕳️  Void Agent: Sensing Dark Matter...")
        self._verify_identity()
        self._generate_metrics()

if __name__ == "__main__":
    agent = VoidAgent()
    agent.run()
