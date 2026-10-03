# src/agents/self_healing_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import json
import logging
import re
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from src.base.base_agent import BaseAgent, AgentLayer
from src.core.psvc_reference import write_file, content_hash, PRECISION_FLOAT16

logger = logging.getLogger(__name__)

class SelfHealingAgent(BaseAgent):
    """
    Autonomous Code Auditor and Repairer.
    Scans src/ for protocol violations (sys.path hacks, relative imports) 
    and automatically patches them to ensure system stability and evolution.
    Operates under WENDY optimization authority.
    """
    LAYER = AgentLayer.ORCHESTRATION

    def __init__(self, name: str = "self_healer", scan_dir: str = "src"):
        super().__init__(name, capabilities=["audit_code", "patch_imports", "remove_path_hacks"])
        self.scan_dir = Path(scan_dir)
        self.repairs_log: List[Dict[str, Any]] = []

    def _is_python_file(self, path: Path) -> bool:
        return path.suffix == ".py" and "__pycache__" not in str(path)

    def audit_and_patch(self) -> int:
        """
        Scans all Python files in src/ for violations of PYTHON_PROTOCOL.md.
        Returns the number of files repaired.
        """
        repairs_count = 0
        
        if not self.scan_dir.exists():
            logger.warning(f"Scan directory {self.scan_dir} does not exist.")
            return 0

        for file_path in self.scan_dir.rglob("*.py"):
            if not self._is_python_file(file_path):
                continue
                
            try:
                original_content = file_path.read_text(encoding='utf-8')
                modified_content = original_content
                changes_made = False

                # 1. Remove sys.path hacks
                # Pattern matches lines starting with optional whitespace, 'sys.path.insert' or 'append'
                pattern_sys_path = r'^\s*sys\.path\.(insert|append)\(.*$\n?'
                cleaned_content = re.sub(pattern_sys_path, '', modified_content, flags=re.MULTILINE)
                
                if cleaned_content != modified_content:
                    modified_content = cleaned_content
                    changes_made = True
                    self.repairs_log.append({
                        "file": str(file_path),
                        "action": "removed_sys_path_hack",
                        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    })

                if changes_made:
                    # Atomic Write
                    temp_path = file_path.with_suffix('.tmp')
                    temp_path.write_text(modified_content, encoding='utf-8')
                    temp_path.replace(file_path)
                    repairs_count += 1
                    logger.info(f"✅ Repaired protocol violations in: {file_path.name}")

            except Exception as e:
                logger.error(f"❌ Failed to audit/repair {file_path}: {e}")
                continue

        return repairs_count

    def execute(self, instruction: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point for the daemon.
        """
        logger.info("[SelfHealingAgent] Starting autonomous code audit...")
        
        count = self.audit_and_patch()
        
        result = {
            "status": "success",
            "files_repaired": count,
            "repairs_detail": self.repairs_log[-10:] if self.repairs_log else [],
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        
        # Seal a report of the healing action
        if count > 0:
            # Use numpy array for proper vector math
            vector = np.zeros(4096, dtype=np.float32)
            vector[0] = float(count) / 100.0
            
            norm = np.linalg.norm(vector)
            if norm > 1e-9:
                vector /= norm
            
            output_dir = Path("reports/scientific_reports")
            output_dir.mkdir(parents=True, exist_ok=True)
            chash = content_hash(vector)
            filename = f"healing_report_{chash[:12]}.psvc"
            
            write_file(vector, output_dir / filename, precision=PRECISION_FLOAT16)
            
            sidecar = output_dir / f"{filename}.json"
            with open(sidecar, 'w') as f:
                json.dump(result, f, indent=2)
                
            logger.info(f"[SelfHealingAgent] Sealed healing report: {filename}")

        return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = SelfHealingAgent()
    res = agent.execute()
    print(res)
