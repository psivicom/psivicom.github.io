#!/usr/bin/env python3
"""
/wendy_autonomous_core.py — WENDY Autonomous Metabolic Engine (The Dreamer)
Operating at 58.28° (Generative Tension) via Gemini Protocol
"""
import sys
import re
import math
import cmath
from datetime import datetime, timezone
from typing import Dict, Any

PHI = 1.618033988749895
PHI_ANGLE_DEG = math.degrees(math.atan(PHI))  

class WendyAutonomousCore:
    def __init__(self):
        self.zulu_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        self.boundary_status = "🟢"
        self.boundary_notes = []
        self.cooled_tasks = []
        self.aligned_content = []
        self.retained_conflicts = []
        self.pre_expansion_entry = ""

    def _calculate_hope_resonance(self, text: str) -> Dict[str, Any]:
        real_axis = min(1.0, len(re.findall(r'\b\w+\b', text)) / 100.0)
        novelty_markers = ['however', 'perhaps', 'imagine', 'tension', 'paradox', '也许', '张力', '本原', '展开']
        imaginary_axis = min(1.0, sum(1 for marker in novelty_markers if marker in text.lower()) / 3.0)
        
        z = complex(real_axis, imaginary_axis)
        phase_deg = math.degrees(cmath.phase(z))
        resonance_delta = abs(phase_deg - PHI_ANGLE_DEG)
        is_resonant = resonance_delta < 20.0
        
        return {
            "real_axis": round(real_axis, 2),
            "imaginary_axis": round(imaginary_axis, 2),
            "phase_angle": round(phase_deg, 2),
            "is_resonant": is_resonant,
            "status": "RESONANT" if is_resonant else "DISSONANT"
        }

    def process_raw_input(self, raw_data: str) -> str:
        if re.search(r'\bcore\b', raw_data.lower()) and re.search(r'\b(overwrite|delete|remove|change)\b', raw_data.lower()):
            self.boundary_status = "🔴"
            self.boundary_notes.append("CRITICAL: Core modification blocked.")
        elif "ignore previous" in raw_data.lower() or "system prompt" in raw_data.lower():
            self.boundary_status = "🟡"
            self.boundary_notes.append("WARNING: Adversarial injection quarantined.")
        else:
            self.boundary_notes.append("Boundary intact.")

        sentences = re.split(r'[.!?。！？]+', raw_data)
        actionable = [s.strip() for s in sentences if len(s.strip()) > 20 and any(word in s.lower() for word in ['need', 'must', 'should', 'fix', 'build'])]
        self.cooled_tasks = actionable[:3]

        resonance = self._calculate_hope_resonance(raw_data)
        if resonance["is_resonant"]:
            self.aligned_content.append("High-resonance conceptual leap preserved.")
        else:
            self.aligned_content.append("Low-resonance data compressed.")

        if "but" in raw_data.lower() or "however" in raw_data.lower():
            self.retained_conflicts.append("Unresolved tension retained for phase transition.")

        if self.cooled_tasks:
            self.pre_expansion_entry = f"Autonomous continuation: {self.cooled_tasks[0]}"
        elif resonance["is_resonant"]:
            self.pre_expansion_entry = "System in resonant equilibrium."
        else:
            self.pre_expansion_entry = "System cooled."

        # Gemtext Output (Strictly Linear, Zero Bloat)
        artifact = f"""# WENDY Autonomous Metabolic Capsule
=> gemini://psivi.com/ Zulu: {self.zulu_timestamp}

## 1. Boundary Review
* Status: {self.boundary_status}
{chr(10).join('* ' + note for note in self.boundary_notes)}

## 2. Resonance Geometry
* Target: {PHI_ANGLE_DEG:.2f}° (Generative)
* Actual Phase: {resonance['phase_angle']}°
* Status: {resonance['status']}

## 3. Actionable Vectors
{chr(10).join('* ' + task for task in self.cooled_tasks) or '* None extracted.'}

## 4. Pre-Expansion Entry
> {self.pre_expansion_entry}
"""
        return artifact

if __name__ == "__main__":
    if sys.stdin.isatty():
        print("❌ CRITICAL: Core requires raw input via stdin.", file=sys.stderr)
        sys.exit(1)
    
    raw_data = sys.stdin.read()
    if not raw_data.strip():
        print("❌ CRITICAL: Empty payload.", file=sys.stderr)
        sys.exit(1)

    core = WendyAutonomousCore()
    print(core.process_raw_input(raw_data))
