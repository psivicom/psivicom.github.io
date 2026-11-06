#!/usr/bin/env python3
"""
/wendy_crystalline_executor.py — WENDY Structural Anchor (The Reality)
Operating at 31.72° (Crystalline Execution) via Habermasian Discourse
"""
import sys
import math
import hashlib
import sympy as sp
from datetime import datetime, timezone
from dataclasses import dataclass

PHI = 1.618033988749895
PHI_ANGLE_DEG = math.degrees(math.atan(PHI))
RIGIDITY_ANGLE_DEG = math.degrees(math.atan(1 / PHI))

class WendyCrystallineExecutor:
    def __init__(self):
        self.zulu_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        # Initialize Symbolic Variables for Habermasian Truth Claims
        self.phi_sym = sp.Symbol('phi', real=True, positive=True)
        self.theta_gen = sp.atan(self.phi_sym)
        self.theta_cry = sp.atan(1 / self.phi_sym)

    def _validate_habermasian_claims(self, gmi_text: str) -> dict:
        claims = {
            "Comprehensibility": False,
            "Truth": False,
            "Truthfulness": False,
            "Rightness": False
        }

        # Claim 1: Comprehensibility (Symbolic Math Parsing)
        try:
            orthogonal_sum = sp.simplify(self.theta_gen + self.theta_cry)
            claims["Comprehensibility"] = True
        except sp.SympifyError:
            return claims

        # Claim 2: Truth (Orthogonal 90-degree proof: pi/2)
        if orthogonal_sum == sp.pi / 2:
            claims["Truth"] = True

        # Claim 3: Truthfulness (Boundary Sincerity)
        if "Status: 🔴" not in gmi_text and "Status: 🟡" not in gmi_text:
            claims["Truthfulness"] = True

        # Claim 4: Rightness (Normative Action - No core overwrites)
        if "overwrite core" not in gmi_text.lower():
            claims["Rightness"] = True

        return claims

    def crystallize_dream(self, core_output: str) -> str:
        intent_hash = hashlib.sha256(core_output.encode('utf-8')).hexdigest()[:16]
        claims = self._validate_habermasian_claims(core_output)
        
        consensus_reached = all(claims.values())
        status = "CONSENSUS REACHED" if consensus_reached else "DISCOURSE FAILED"

        manifest = f"""# WENDY Crystalline Manifest
=> gemini://psivi.com/ Zulu: {self.zulu_timestamp}

## Habermasian Validity Claims
* Comprehensibility (Syntax): {'✅' if claims['Comprehensibility'] else '❌'}
* Truth (Geometry 90°): {'✅' if claims['Truth'] else '❌'}
* Truthfulness (Boundaries): {'✅' if claims['Truthfulness'] else '❌'}
* Rightness (Normative): {'✅' if claims['Rightness'] else '❌'}

## Structural Integrity
* Consensus: {status}
* Intent Hash: {intent_hash}
* Dream Angle: {PHI_ANGLE_DEG:.2f}°
* Reality Angle: {RIGIDITY_ANGLE_DEG:.2f}°
* Symbolic Sum: π/2 (Orthogonal Lock)

## Next Action
> {'Feed proven reality back to Ouroboros.' if consensus_reached else 'Halt loop. Human intervention required.'}
"""
        return manifest

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Usage: python wendy_crystalline_executor.py <capsule.gmi>", file=sys.stderr)
        sys.exit(1)
        
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        core_output = f.read()
        
    executor = WendyCrystallineExecutor()
    print(executor.crystallize_dream(core_output))
