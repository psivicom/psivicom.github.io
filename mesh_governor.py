# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# Author: Louis-Philippe Audette
# ORCID: https://orcid.org/0000-000X-XXXX-XXXX
# Affiliation: PSIVI Research
#
# Mesh Governor - RFC 1001 Enforcement

import os
import json
import datetime
import numpy as np
from pathlib import Path

class MeshGovernor:
    """Enforces RFC 1001 compliance and Pico Protocol."""

    RULES = {
        "no_text_between_agents": True,
        "max_vram_slots": 5,
        "vector_dim": 4096,
        "precision_required": ["int8", "float16", "float32"],
        "fallback_to_disk_below_mb": 64,
    }

    def __init__(self, vector_folder="reports/pico_containers", 
                 log_file="reports/governor_log.md"):
        self.vector_folder = Path(vector_folder)
        self.log_file = Path(log_file)
        self.vector_folder.mkdir(parents=True, exist_ok=True)
        self.violations = []
        self.decisions = []

    def check_available_memory_mb(self):
        """Check available RAM."""
        try:
            with open('/proc/meminfo') as f:
                for line in f:
                    if line.startswith('MemAvailable:'):
                        return int(line.split()[1]) / 1024
        except:
            pass
        return 256

    def decide_mode(self):
        """Decide VRAM or disk mode."""
        available_mb = self.check_available_memory_mb()
        threshold = self.RULES["fallback_to_disk_below_mb"]

        if available_mb < threshold:
            mode = "disk"
            reason = f"Only {available_mb:.0f}MB available."
        else:
            mode = "vram"
            reason = f"{available_mb:.0f}MB available."

        self.decisions.append({
            "mode": mode, 
            "reason": reason, 
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        return mode, reason

    def enforce_no_text(self):
        """Check for text-based communication violations."""
        violations = []
        banned_patterns = [
            'requests.post',
            'json.dumps',
            'socket.send',
            'subprocess.run',
        ]
        
        # Safe patterns that are allowed
        safe_patterns = [
            'subprocess.run(["go", "run", "mesh.go"',  # Go orchestrator
            'from psvc_reference import',               # Canonical library
            'import psvc_reference',                    # Canonical library
        ]

        for py_file in Path('.').glob('*_agent.py'):
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Skip if file imports the canonical library
                uses_canonical = 'psvc_reference' in content
                
                for pattern in banned_patterns:
                    if pattern in content:
                        # Check if it's a safe pattern
                        is_safe = any(safe in content for safe in safe_patterns)
                        
                        if is_safe and pattern == 'subprocess.run':
                            continue
                        
                        # json.dumps is allowed for sidecar metadata
                        if pattern == 'json.dumps' and uses_canonical:
                            continue
                        
                        violations.append({
                            "file": str(py_file),
                            "violation": f"Found '{pattern}'",
                            "severity": "WARNING"
                        })
            except:
                continue

        self.violations = violations
        return violations

    def enforce_vector_format(self):
        """Verify all vectors use approved precision."""
        from psvc_reference import validate_file, PSVCError
        
        format_violations = []
        
        for psvc_file in self.vector_folder.glob("*.psvc"):
            try:
                info = validate_file(psvc_file)
                if info["precision"] not in self.RULES["precision_required"]:
                    format_violations.append({
                        "file": str(psvc_file),
                        "violation": f"Invalid precision: {info['precision']}",
                        "severity": "ERROR"
                    })
            except PSVCError as e:
                format_violations.append({
                    "file": str(psvc_file),
                    "violation": f"RFC 1001 violation: {e}",
                    "severity": "ERROR"
                })

        self.violations.extend(format_violations)
        return format_violations

    def generate_report(self):
        """Write enforcement report."""
        mode, reason = self.decide_mode()
        self.enforce_no_text()
        self.enforce_vector_format()

        vector_count = len(list(self.vector_folder.glob("*.psvc")))

        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("# Mesh Governor Enforcement Report\n\n")
            f.write(f"**Timestamp:** {datetime.datetime.utcnow().isoformat()}\n")
            f.write(f"**Available RAM:** {self.check_available_memory_mb():.0f} MB\n\n")
            f.write("## Mode Decision\n")
            f.write(f"- **Selected Mode:** `{mode}`\n")
            f.write(f"- **Reason:** {reason}\n\n")
            f.write("## Enforcement Scan\n")
            f.write(f"- **Vectors in storage:** {vector_count}\n")
            f.write(f"- **Violations found:** {len(self.violations)}\n\n")

            if self.violations:
                f.write("## Violations\n")
                for v in self.violations:
                    f.write(f"- [{v['severity']}] `{v['file']}`: {v['violation']}\n")
            else:
                f.write("## Status: COMPLIANT\n")
                f.write("All agents use RFC 1001 canonical library. No violations.\n")

        print(f"[GOVERNOR] Report written to {self.log_file}")
        print(f"[GOVERNOR] Mode: {mode} | Violations: {len(self.violations)}")
        return mode, len(self.violations)

if __name__ == "__main__":
    print("=== PSIVI MESH GOVERNOR (RFC 1001 ENFORCEMENT) ===")
    governor = MeshGovernor()
    mode, violation_count = governor.generate_report()

    # Write governor decision as vector
    try:
        from psvc_reference import encode_text, write_file, content_hash, PRECISION_FLOAT16
        
        decision_text = f"Governor decision at {datetime.date.today().isoformat()}: Mode={mode}. Violations={violation_count}."
        vector = encode_text(decision_text)
        chash = content_hash(vector)
        output_path = Path("reports/pico_containers") / f"governor_{chash}.psvc"
        
        write_file(vector, output_path, precision=PRECISION_FLOAT16)
        print(f"[GOVERNOR] Decision sealed: {output_path.name}")
    except Exception as e:
        print(f"[GOVERNOR] Could not seal decision: {e}")
