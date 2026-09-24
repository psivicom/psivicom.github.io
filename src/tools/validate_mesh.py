# src/tools/validate_mesh.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import sys
import json
from pathlib import Path
from typing import List

class MeshValidator:
    def __init__(self):
        self.root = Path(__file__).parent.parent.parent
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def check_file_exists(self, path: str, description: str) -> bool:
        full_path = self.root / path
        if not full_path.exists():
            self.errors.append(f"❌ MISSING {description}: {path}")
            return False
        print(f"✓ Found {description}: {path}")
        return True
    
    def check_osdr_data(self) -> bool:
        osdr_path = self.root / "data" / "osdr_ground_truth.jsonl"
        if not osdr_path.exists():
            self.errors.append("❌ MISSING OSDR data: data/osdr_ground_truth.jsonl")
            return False
        try:
            with open(osdr_path) as f:
                json.loads(f.readline())
            print(f"✓ OSDR data valid: data/osdr_ground_truth.jsonl")
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"❌ INVALID OSDR data: {e}")
            return False
    
    def run_all_checks(self) -> bool:
        print("=" * 60)
        print("PSIVI MESH VALIDATION REPORT")
        print("=" * 60)
        self.check_osdr_data()
        self.check_file_exists("src/agents/pilot_agent.py", "Pilot Agent")
        self.check_file_exists("src/orchestrator/chain_orchestrator.py", "Chain Orchestrator")
        self.check_file_exists("src/base/base_agent.py", "Base Agent")
        self.check_file_exists("psvc_reference.py", "PSVC Reference (Root)")
        self.check_file_exists("src/core/psvc_containers.py", "PSVC Containers")
        
        print("=" * 60)
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for err in self.errors: print(f"  {err}")
            return False
        print("\n✅ ALL CHECKS PASSED - Mesh is ready to run")
        return True

if __name__ == "__main__":
    validator = MeshValidator()
    success = validator.run_all_checks()
    sys.exit(0 if success else 1)
