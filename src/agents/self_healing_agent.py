# src/agents/self_healing_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import json
import logging
import re
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timezone

from src.base.base_agent import BaseAgent, AgentLayer
from src.core.psvc_reference import content_hash, PRECISION_FLOAT16

logger = logging.getLogger(__name__)

class SelfHealingAgent(BaseAgent):
    """
    Autonomous Code Auditor and Repairer.
    Scans src/ for protocol violations and automatically patches them.
    Seals the healing event as a normalized, precision-scaled mathematical vector
    to enforce strict VRAM limits per the PSVC RFC.
    """
    LAYER = AgentLayer.ORCHESTRATION

    def __init__(self, name: str = "self_healer", scan_dir: str = "src"):
        super().__init__(name, capabilities=["audit_code", "patch_imports", "remove_path_hacks"])
        self.scan_dir = Path(scan_dir)
        self.repairs_log: List[Dict[str, Any]] = []

    def _is_python_file(self, path: Path) -> bool:
        return path.suffix == ".py" and "__pycache__" not in str(path)

    def audit_and_patch(self) -> int:
        """Scans all Python files in src/ for violations and repairs them."""
        repairs_count = 0
        
        if not self.scan_dir.exists():
            logger.warning(f"Scan directory {self.scan_dir} does not exist.")
            return 0

        for file_path in self.scan_dir.rglob("*.py"):
            if not self._is_python_file(file_path):
                continue
                
            try:
                original_content = file_path.read_text(encoding='utf-8')
                
                # Remove sys.path hacks using regex
                pattern_sys_path = r'^\s*sys\.path\.(insert|append)\(.*$\n?'
                cleaned_content = re.sub(pattern_sys_path, '', original_content, flags=re.MULTILINE)
                
                if cleaned_content != original_content:
                    # Atomic Write
                    temp_path = file_path.with_suffix('.tmp')
                    temp_path.write_text(cleaned_content, encoding='utf-8')
                    temp_path.replace(file_path)
                    
                    repairs_count += 1
                    self.repairs_log.append({
                        "file": str(file_path),
                        "action": "removed_sys_path_hack",
                        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    })
                    logger.info(f"✅ Repaired protocol violations in: {file_path.name}")

            except Exception as e:
                logger.error(f"❌ Failed to audit/repair {file_path}: {e}")
                continue

        return repairs_count

    def execute(self, instruction: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main entry point for the daemon."""
        logger.info("[SelfHealingAgent] Starting autonomous code audit...")
        
        count = self.audit_and_patch()
        
        result = {
            "status": "success",
            "files_repaired": count,
            "repairs_detail": self.repairs_log[-10:] if self.repairs_log else [],
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        
        # CRUCIAL MATH: Seal the healing event as a precision-scaled mathematical vector
        if count > 0:
            # 1. Initialize the 4096-dimensional state vector in float32 for calculation stability
            vector = np.zeros(4096, dtype=np.float32)
            
            # 2. Encode the healing magnitude
            vector[0] = float(count) / 100.0
            
            # 3. Normalize the vector to maintain mesh mathematical integrity
            norm = np.linalg.norm(vector)
            if norm > 1e-9:
                vector /= norm
            
            # 4. RFC PRECISION SCALING: Cast down to float16 (or float8/int8 depending on data type)
            # This enforces strict VRAM Dim enforcement and minimizes mesh bandwidth.
            # PRECISION_FLOAT16 maps to np.float16 in the PSVC reference.
            vector = vector.astype(np.float16)
            
            output_dir = Path("reports/scientific_reports")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = int(datetime.now(timezone.utc).timestamp())
            
            # 5. Generate cryptographic content hash of the exact precision-scaled binary
            chash = content_hash(vector.tobytes())
            
            # 6. Save the pure mathematical vector (preserving exact float16 binary precision)
            vector_path = output_dir / f"healing_vector_{chash[:12]}.npy"
            np.save(vector_path, vector)
            
            # 7. Save the metadata sidecar
            meta_path = output_dir / f"healing_report_{chash[:12]}.json"
            with open(meta_path, 'w') as f:
                json.dump(result, f, indent=2)
                
            logger.info(f"[SelfHealingAgent] Sealed precision-scaled vector ({vector.dtype}): {vector_path.name}")

        return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = SelfHealingAgent()
    res = agent.execute()
    print(res)
