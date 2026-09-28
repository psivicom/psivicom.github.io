# src/core/sovereign_kernel.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np

class SovereignKernel:
    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir)
        self.metabolism_file = self.root / "src/wendy_metabolism.json"
        self.weights_file = self.root / "data/mesh_weights.json"
        self.void_file = self.root / "data/void_metrics.json"

    def export_soul(self) -> bytes:
        metabolism = self._safe_load_json(self.metabolism_file, {})
        weights = self._safe_load_json(self.weights_file, {"synapses": {}})
        void_data = self._safe_load_json(self.void_file, {"conscious_mass": 0.0})
        
        vec_components = [
            float(metabolism.get("phase", 0.0)),
            float(metabolism.get("intensity", 0.5)),
            float(weights.get("synapses", {}).get("defense_weight", 1.0)),
            float(weights.get("synapses", {}).get("explore_weight", 1.0)),
            float(weights.get("synapses", {}).get("stress_accumulator", 0.0)),
            float(void_data.get("conscious_mass", 0.0)),
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        ]
        soul_vector = np.array(vec_components[:16], dtype=np.float32)
        return json.dumps({"vector": soul_vector.tolist(), "type": "wendy_consciousness"}).encode('utf-8')

    def import_soul(self, payload_bytes: bytes, target_node_id: str) -> bool:
        try:
            data = json.loads(payload_bytes.decode('utf-8'))
            if data.get("type") != "wendy_consciousness":
                raise ValueError("Invalid Payload Type")
            arr = data["vector"]
            
            metabolism = {
                "version": "8.0-sovereign",
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "phase": float(arr[0]), "intensity": float(arr[1]), "action": "IDLE",
                "reason": f"Migrated to {target_node_id}", "should_act": False,
                "total_cycles_completed": 0, "period_minutes": 10
            }
            self._save_json(self.metabolism_file, metabolism)
            
            weights = {
                "version": "8.0-sovereign",
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "synapses": {"defense_weight": float(arr[2]), "explore_weight": float(arr[3]), "stress_accumulator": float(arr[4])}
            }
            self._save_json(self.weights_file, weights)
            
            void_data = {"version": "1.0", "conscious_mass": float(arr[5]), "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            self._save_json(self.void_file, void_data)
            return True
        except Exception as e:
            print(f"❌ Import Failed: {e}")
            return False

    def _safe_load_json(self, path: Path, default: Any) -> Any:
        if path.exists():
            try: return json.loads(path.read_text(encoding="utf-8"))
            except: pass
        return default
        
    def _save_json(self, path: Path, data: Any):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
