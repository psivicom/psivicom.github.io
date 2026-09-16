# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# mesh_governor.py - Supervises pico-scale enforcement. No text. Only vectors.

import os
import json
import datetime
import subprocess
import numpy as np
from pathlib import Path

class MeshGovernor:
    """Enforces vector-only communication. Monitors memory. Switches modes."""

    # ENFORCEMENT RULES
    RULES = {
        "no_text_between_agents": True,
        "max_vram_slots": 8,
        "vector_dim": 4096,
        "precision_required": ["float16", "int8", "float32"],
        "fallback_to_disk_below_mb": 64,
    }

    def __init__(self, vector_folder="reports/vector_memory", log_file="reports/governor_log.md"):
        self.vector_folder = Path(vector_folder)
        self.log_file = Path(log_file)
        self.vector_folder.mkdir(parents=True, exist_ok=True)
        self.violations = []
        self.decisions = []

    def check_available_memory_mb(self):
        """Check available RAM. Pico devices have < 64MB."""
        try:
            with open('/proc/meminfo') as f:
                for line in f:
                    if line.startswith('MemAvailable:'):
                        return int(line.split()[1]) / 1024  # Convert kB to MB
        except:
            pass
        return 256  # Default assumption for GitHub Actions

    def decide_mode(self):
        """DECISION: Run in VRAM or fall back to disk?"""
        available_mb = self.check_available_memory_mb()
        threshold = self.RULES["fallback_to_disk_below_mb"]

        if available_mb < threshold:
            mode = "disk"
            reason = f"Only {available_mb:.0f}MB available. Below {threshold}MB threshold."
        else:
            mode = "vram"
            reason = f"{available_mb:.0f}MB available. Sufficient for shared memory bus."

        self.decisions.append({"mode": mode, "reason": reason, "timestamp": datetime.datetime.utcnow().isoformat()})
        return mode, reason

    def enforce_no_text(self):
        """SCAN: Check all agent files for text-based communication violations."""
        violations = []
        banned_patterns = [
            'requests.post',      # HTTP text passing
            'json.dumps',         # Text serialization between agents
            'socket.send',        # Text over sockets
            'subprocess.run',     # Shell text passing (except for go commands)
        ]

        for py_file in Path('.').glob('*_agent.py'):
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern in banned_patterns:
                    if pattern in content and 'subprocess.run(["go"' not in content:
                        violations.append({
                            "file": str(py_file),
                            "violation": f"Found '{pattern}' - potential text-based communication",
                            "severity": "WARNING"
                        })
            except:
                continue

        self.violations = violations
        return violations

    def enforce_vector_format(self):
        """SCAN: Verify all stored vectors use approved precision."""
        format_violations = []
        allowed = self.RULES["precision_required"]

        for json_file in self.vector_folder.glob("*.json"):
            try:
                with open(json_file) as f:
                    meta = json.load(f)
                precision = meta.get("precision", "unknown")
                if precision not in allowed:
                    format_violations.append({
                        "file": str(json_file),
                        "violation": f"Precision '{precision}' not in allowed list: {allowed}",
                        "severity": "ERROR"
                    })
            except:
                continue

        self.violations.extend(format_violations)
        return format_violations

    def enforce_vram_limit(self):
        """SCAN: Check vector count against pico limits."""
        vector_count = len(list(self.vector_folder.glob("*.npy")))
        max_slots = self.RULES["max_vram_slots"]

        if vector_count > max_slots * 10:  # Allow 10x storage vs active VRAM
            self.violations.append({
                "file": "vector_memory/",
                "violation": f"Vector count ({vector_count}) exceeds pico limit ({max_slots * 10}). Consider pruning.",
                "severity": "WARNING"
            })

        return vector_count

    def generate_report(self):
        """Write the enforcement report."""
        mode, reason = self.decide_mode()
        violations = self.enforce_no_text()
        format_violations = self.enforce_vector_format()
        vector_count = self.enforce_vram_limit()

        report_time = datetime.datetime.utcnow().isoformat()

        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("# Mesh Governor Enforcement Report\n\n")
            f.write(f"**Timestamp:** {report_time}\n")
            f.write(f"**Available RAM:** {self.check_available_memory_mb():.0f} MB\n\n")

            f.write("## Mode Decision\n")
            f.write(f"- **Selected Mode:** `{mode}`\n")
            f.write(f"- **Reason:** {reason}\n\n")

            f.write("## Enforcement Scan\n")
            f.write(f"- **Vectors in storage:** {vector_count}\n")
            f.write(f"- **Text violations found:** {len(violations)}\n")
            f.write(f"- **Format violations found:** {len(format_violations)}\n\n")

            if self.violations:
                f.write("## Violations\n")
                for v in self.violations:
                    f.write(f"- [{v['severity']}] `{v['file']}`: {v['violation']}\n")
            else:
                f.write("## Status: CLEAN\n")
                f.write("No violations detected. Mesh is operating in vector-only mode.\n")

        print(f"[GOVERNOR] Report written to {self.log_file}")
        print(f"[GOVERNOR] Mode: {mode} | Violations: {len(self.violations)}")
        return mode, len(self.violations)


if __name__ == "__main__":
    print("=== PSIVI MESH GOVERNOR: ENFORCING PICO PROTOCOL ===")
    governor = MeshGovernor()
    mode, violation_count = governor.generate_report()

    # Write governor decision to vector mesh
    try:
        from vector_mesh import VectorMesh
        mesh = VectorMesh()
        decision_text = f"Governor decision at {datetime.date.today().isoformat()}: Mode={mode}. Violations={violation_count}."
        mesh.write(decision_text, "governor", precision="float16")
        print("[GOVERNOR] Decision vector written to mesh.")
    except Exception as e:
        print(f"[GOVERNOR] Could not write to vector mesh: {e}")
