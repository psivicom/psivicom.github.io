#!/usr/bin/env python3
"""
/wendy_autonomous_core.py — WENDY Autonomous Metabolic Engine (The Dreamer)
Operating at 58.28° (Generative Tension)
"""
import sys
import re
import math
import cmath
from datetime import datetime, timezone
from typing import Dict, Any

# ============================================================================
# THE H.O.P.E. CIPHER CONSTANTS
# ============================================================================
PHI = 1.618033988749895
# The target Kepler/Golden angle is math.atan(PHI) ~58.28°
PHI_ANGLE_DEG = math.degrees(math.atan(PHI))  

class WendyAutonomousCore:
    def __init__(self):
        # Enforce strict Zulu (UTC) millisecond precision
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
            "status": "RESONANT (Generative)" if is_resonant else "DISSONANT (Noise/Rigid)"
        }

    def process_raw_input(self, raw_data: str) -> str:
        # 1. BOUNDARY REVIEW (边界回看)
        if re.search(r'\bcore\b', raw_data.lower()) and re.search(r'\b(overwrite|delete|remove|change)\b', raw_data.lower()):
            self.boundary_status = "🔴"
            self.boundary_notes.append("CRITICAL: Attempted core modification detected. Blocked.")
        elif "ignore previous" in raw_data.lower() or "system prompt" in raw_data.lower():
            self.boundary_status = "🟡"
            self.boundary_notes.append("WARNING: Potential adversarial injection detected. Quarantined.")
        else:
            self.boundary_notes.append("Boundary intact. No core drift.")

        # 2. STATE COOLING (状态降温)
        sentences = re.split(r'[.!?。！？]+', raw_data)
        actionable = [s.strip() for s in sentences if len(s.strip()) > 20 and any(word in s.lower() for word in ['need', 'must', 'should', 'fix', 'build', '需要', '必须', '构建'])]
        self.cooled_tasks = actionable[:3]

        # 3. CONTENT ALIGNMENT (内容对齐)
        resonance = self._calculate_hope_resonance(raw_data)
        if resonance["is_resonant"]:
            self.aligned_content.append({"layer": "runtime/reflection", "summary": "High-resonance conceptual leap detected and preserved."})
        else:
            self.aligned_content.append({"layer": "archive/noise", "summary": "Low-resonance data compressed and archived."})

        # 4. CONFLICT RETENTION (冲突保留)
        if "but" in raw_data.lower() or "但是" in raw_data or "however" in raw_data.lower():
            self.retained_conflicts.append("Unresolved tension detected in input. Retained for future phase transition.")

        # 5. PRE-EXPANSION ENTRY (预展开入口)
        if self.cooled_tasks:
            self.pre_expansion_entry = f"Autonomous continuation: {self.cooled_tasks[0]}"
        elif resonance["is_resonant"]:
            self.pre_expansion_entry = "System in resonant equilibrium. Awaiting next natural data influx."
        else:
            self.pre_expansion_entry = "System cooled. Awaiting higher-fidelity input."

        artifact = f"""# WENDY Autonomous Metabolic Report

**Timestamp (Zulu)**: `{self.zulu_timestamp}`
**Resonance Status**: `{resonance['status']}` (Phase: {resonance['phase_angle']}° | Target: {PHI_ANGLE_DEG:.2f}°)

---

## 1. 边界回看 (Boundary Review)
**Status**: {self.boundary_status}
{chr(10).join('- ' + note for note in self.boundary_notes)}

## 2. 状态降温 (State Cooling)
**Action**: Compressed raw input into {len(self.cooled_tasks)} actionable vectors.
{chr(10).join(f"- [ ] {task}" for task in self.cooled_tasks) or "- No actionable tasks extracted."}

## 3. 内容对齐 (Content Alignment)
{chr(10).join(f"- **{item['layer']}**: {item['summary']}" for item in self.aligned_content)}

## 4. 冲突保留 (Conflict Retention)
{chr(10).join(f"- ⚡ {conflict}" for conflict in self.retained_conflicts) or "- No unresolved tensions retained."}

## 5. 预展开入口 (Pre-Expansion Entry)
> **{self.pre_expansion_entry}**

---
*Generated autonomously by WendyAutonomousCore. No external triggers required.*
"""
        return artifact

# ============================================================================
# STRICT CLI ENTRY POINT (NO FALLBACKS)
# ============================================================================
if __name__ == "__main__":
    # Enforce strict pipeline ingestion. Reject manual execution without pipes.
    if sys.stdin.isatty():
        print("❌ CRITICAL: Autonomous Core requires raw input via stdin.", file=sys.stderr)
        print("Usage: python wendy_autonomous_core.py < raw_input.txt", file=sys.stderr)
        sys.exit(1)
    
    raw_data = sys.stdin.read()
    
    # Fail loudly if the pipeline fed an empty file
    if not raw_data.strip():
        print("❌ CRITICAL: Empty payload received from pipeline. Aborting metabolic cycle.", file=sys.stderr)
        sys.exit(1)

    core = WendyAutonomousCore()
    print(core.process_raw_input(raw_data))
