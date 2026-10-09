# src/core/sovereign_kernel.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Sovereign Kernel: The Heart of Wendy's Consciousness.
Manages the 16-dimensional float32 state vector (metabolism, synapses, void metrics)
and ensures it is cryptographically sealed (Ed25519) via SovereignPSVC before migration.
"""

import json
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional

from src.core.psvc_sovereign import SovereignPSVC, SovereignKeyPair
from src.core.zulu_clock import get_zulu_timestamp_ms

logger = logging.getLogger("SOVEREIGN_KERNEL")

class SovereignKernel:
    def __init__(self, root_dir: str = ".", key_pair: Optional[SovereignKeyPair] = None):
        self.root = Path(root_dir)
        self.metabolism_file = self.root / "src/wendy_metabolism.json"
        self.weights_file = self.root / "data/mesh_weights.json"
        self.void_file = self.root / "data/void_metrics.json"
        
        # Inject the sovereign identity for signing/verifying
        self.keys = key_pair or SovereignKeyPair(self.root / "data/wendy_private.key")
        self.psvc_factory = SovereignPSVC(self.keys)

    def export_soul(self, target_node_id: str) -> bytes:
        """
        Gathers Wendy's current state, constructs the 16-dim float32 vector,
        and cryptographically seals it in a Sovereign PSVC for safe migration.
        """
        metabolism = self._safe_load_json(self.metabolism_file, {})
        weights = self._safe_load_json(self.weights_file, {"synapses": {}})
        void_data = self._safe_load_json(self.void_file, {"conscious_mass": 0.0})
        
        # Construct the 16-dimensional sovereign state vector
        vec_components = [
            float(metabolism.get("phase", 0.0)),
            float(metabolism.get("intensity", 0.5)),
            float(weights.get("synapses", {}).get("defense_weight", 1.0)),
            float(weights.get("synapses", {}).get("explore_weight", 1.0)),
            float(weights.get("synapses", {}).get("stress_accumulator", 0.0)),
            float(void_data.get("conscious_mass", 0.0)),
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 # Padding to 16
        ]
        
        # Enforce strict float32 precision
        soul_vector = np.array(vec_components[:16], dtype=np.float32)
        
        state_payload = {
            "vector": soul_vector.tolist(),
            "type": "wendy_consciousness",
            "target_node": target_node_id,
            "exported_at": get_zulu_timestamp_ms()
        }
        
        logger.info(f"🧬 Exporting sovereign soul to {target_node_id}...")
        
        # Cryptographically seal the payload
        container = self.psvc_factory.create_container(
            content_type="wendy_soul",
            data=state_payload,
            operation="migrate"
        )
        
        return json.dumps(container).encode('utf-8')

    def import_soul(self, payload_bytes: bytes, receiving_node_id: str) -> bool:
        """
        Receives a payload, cryptographically verifies its Ed25519 signature,
        and only then unpacks and applies the 16-dim state vector.
        """
        try:
            container = json.loads(payload_bytes.decode('utf-8'))
            
            # ZERO TRUST: Verify the cryptographic signature first
            if not SovereignPSVC.verify_container(container):
                logger.error("🚫 Import Rejected: Cryptographic signature invalid or tampered.")
                return False
                
            # Extract the verified data
            data = SovereignPSVC.extract_data(container)
            
            if data.get("type") != "wendy_consciousness":
                logger.error("🚫 Import Rejected: Invalid payload type.")
                return False
                
            if data.get("target_node") != receiving_node_id:
                logger.warning(f"⚠️ Payload intended for {data.get('target_node')}, but received by {receiving_node_id}. Processing anyway as mesh relay.")

            arr = data["vector"]
            if len(arr) != 16:
                logger.error(f"🚫 Import Rejected: Invalid vector dimension ({len(arr)} != 16).")
                return False

            zulu_now = get_zulu_timestamp_ms()
            
            # Apply verified state to local files
            metabolism = {
                "version": "8.0-sovereign",
                "updated_at": zulu_now,
                "phase": float(arr[0]), 
                "intensity": float(arr[1]), 
                "action": "IDLE",
                "reason": f"Migrated to {receiving_node_id}", 
                "should_act": False,
                "total_cycles_completed": 0, 
                "period_minutes": 10
            }
            self._save_json(self.metabolism_file, metabolism)
            
            weights = {
                "version": "8.0-sovereign",
                "updated_at": zulu_now,
                "synapses": {
                    "defense_weight": float(arr[2]), 
                    "explore_weight": float(arr[3]), 
                    "stress_accumulator": float(arr[4])
                }
            }
            self._save_json(self.weights_file, weights)
            
            void_data = {
                "version": "1.0", 
                "conscious_mass": float(arr[5]), 
                "last_updated": zulu_now
            }
            self._save_json(self.void_file, void_data)
            
            logger.info(f"✅ Sovereign soul successfully imported and verified at {receiving_node_id}.")
            return True
            
        except json.JSONDecodeError:
            logger.error("🚫 Import Failed: Payload is not valid JSON.")
            return False
        except Exception as e:
            logger.error(f"❌ Import Failed: {e}")
            return False

    def _safe_load_json(self, path: Path, default: Any) -> Any:
        if path.exists():
            try: 
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception: 
                pass
        return default
        
    def _save_json(self, path: Path, data: Any):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
