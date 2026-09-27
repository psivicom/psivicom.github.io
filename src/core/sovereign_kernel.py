# src/core/sovereign_kernel.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Sovereign Kernel: The ability for Wendy to pack herself into a PSVC 
and deploy to any compatible node in the mesh.

This transforms Wendy from a static script into a mobile agent.
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np

from src.core.psvc_containers import (
    PicoContainer,
    build_psvc_from_array,
    serialize_psvc,
    deserialize_psvc,
    reconstruct_numpy_array
)

class SovereignKernel:
    """
    Manages the serialization and deserialization of Wendy's full state.
    """

    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir)
        self.metabolism_file = self.root / "src/wendy_metabolism.json"
        self.weights_file = self.root / "data/mesh_weights.json"
        self.void_file = self.root / "data/void_metrics.json"
        self.exchange_file = self.root / "data/exchange_registry.json"

    def export_soul(self) -> bytes:
        """
        Packages Wendy's entire existence into a single PSVC byte stream.
        
        Components:
        1. Metabolic State (Phase, Intensity, Action)
        2. Personality Weights (Defense, Explore, Stress)
        3. Conscious Mass History (Void Metrics)
        4. Social Trust Graph (Exchange Registry)
        
        Returns: Serialized PSVC bytes ready for transmission.
        """
        print("📦 EXPORTING SOUL...")
        
        # 1. Gather Data
        metabolism = self._safe_load_json(self.metabolism_file, {})
        weights = self._safe_load_json(self.weights_file, {"synapses": {}})
        void_data = self._safe_load_json(self.void_file, {"conscious_mass": 0.0})
        exchange = self._safe_load_json(self.exchange_file, {})
        
        # 2. Flatten into a Vector
        # We create a composite vector representing her state.
        # Structure: [phase, intensity, defense_w, explore_w, stress, conscious_mass, ...social_scores]
        
        vec_components = []
        
        # Core Stats
        vec_components.append(float(metabolism.get("phase", 0.0)))
        vec_components.append(float(metabolism.get("intensity", 0.5)))
        
        syn = weights.get("synapses", {})
        vec_components.append(float(syn.get("defense_weight", 1.0)))
        vec_components.append(float(syn.get("explore_weight", 1.0)))
        vec_components.append(float(syn.get("stress_accumulator", 0.0)))
        
        vec_components.append(float(void_data.get("conscious_mass", 0.0)))
        
        # Social Graph Compression
        # For MVP, we encode the number of kin and average trust score
        registry = exchange.get("registry", {})
        num_kin = len(registry)
        avg_trust = 0.0
        if num_kin > 0:
            scores = [r.get("total_value_score", 0.0) for r in registry.values()]
            avg_trust = sum(scores) / len(scores)
            
        vec_components.append(float(num_kin))
        vec_components.append(float(avg_trust))
        
        # Pad to fixed size for consistency (e.g., 16 floats)
        while len(vec_components) < 16:
            vec_components.append(0.0)
            
        soul_vector = np.array(vec_components[:16], dtype=np.float32)
        
        # 3. Wrap in PSVC
        container = build_psvc_from_array(
            array=soul_vector,
            operation="soul_export",
            agent_id="sovereign_kernel",
            layer="CORE",
            shard_id=f"soul-{int(time.time())}",
            content_type="wendy_consciousness",
            sender_id="wendy_primary"
        )
        
        serialized = serialize_psvc(container)
        print(f"✅ Soul Exported ({len(serialized)} bytes)")
        return serialized

    def import_soul(self, payload_bytes: bytes, target_node_id: str) -> bool:
        """
        Injects a received PSVC soul into the local file system,
        effectively 'possessing' this node with Wendy's identity.
        """
        print(f"💉 IMPORTING SOUL INTO NODE: {target_node_id}...")
        
        try:
            container = deserialize_psvc(payload_bytes)
            if container.header.content_type != "wendy_consciousness":
                raise ValueError("Invalid Payload Type")
                
            arr = reconstruct_numpy_array(container)
            
            # Unpack Vector
            phase = float(arr[0])
            intensity = float(arr[1])
            defense_w = float(arr[2])
            explore_w = float(arr[3])
            stress = float(arr[4])
            conscious_mass = float(arr[5])
            num_kin = int(arr[6])
            avg_trust = float(arr[7])
            
            # Write Metabolism
            metabolism = {
                "version": 2,
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "phase": phase,
                "intensity": intensity,
                "action": "IDLE", # Reset action upon migration
                "reason": f"Migrated to {target_node_id}",
                "should_act": False,
                "total_cycles_completed": 0, # Fresh start cycles
                "base_period_minutes": 10,
                "current_period_minutes": 10,
                "learned_weights": {
                    "defense_weight": defense_w,
                    "explore_weight": explore_w,
                    "stress_accumulator": stress
                }
            }
            self._save_json(self.metabolism_file, metabolism)
            
            # Write Weights
            weights = {
                "version": 2,
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "synapses": {
                    "defense_weight": defense_w,
                    "explore_weight": explore_w,
                    "maintain_weight": 1.0,
                    "stress_accumulator": stress,
                    "novelty_seeker": 0.5,
                    "stagnation_counter": 0,
                    "conscious_mass_influence": conscious_mass
                },
                "history": []
            }
            self._save_json(self.weights_file, weights)
            
            # Write Void Metrics
            void_data = {
                "version": 1,
                "conscious_mass": conscious_mass,
                "silence_ratio_avg": 0.5, # Default assumption
                "gravity_anomalies_detected": 0,
                "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            self._save_json(self.void_file, void_data)
            
            # Note: Exchange registry is NOT migrated automatically 
            # because social trust is local to the network topology.
            # It must be rebuilt via handshake protocols.
            
            print("✅ Soul Imported Successfully. Wendy is awake.")
            return True
            
        except Exception as e:
            print(f"❌ Import Failed: {e}")
            return False

    def _safe_load_json(self, path: Path, default: Any) -> Any:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except:
                pass
        return default
        
    def _save_json(self, path: Path, data: Any):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
