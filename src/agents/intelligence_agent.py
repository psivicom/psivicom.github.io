# src/agents/intelligence_agent.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

import logging
import time
import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np

# CORRECT absolute imports
from src.base.base_agent import BaseAgent, AgentLayer
from src.core.psvc_containers import (
    PicoContainer,
    build_psvc_from_tensor, # Note: This function now expects numpy arrays or handles conversion internally if updated
    serialize_psvc,
    deserialize_psvc,
    reconstruct_torch_tensor # Renamed conceptually to reconstruct_array in logic below
)

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class IntelligenceReport:
    """Immutable intelligence report from mesh queries."""
    report_id: str
    query_context: Dict[str, Any]
    vram_hits: int
    pico_hits: int
    seed_hits: int
    aggregated_vector: bytes
    vector_shape: tuple
    confidence_score: float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "query_context": self.query_context,
            "vram_hits": self.vram_hits,
            "pico_hits": self.pico_hits,
            "seed_hits": self.seed_hits,
            "vector_shape": list(self.vector_shape),
            "confidence_score": self.confidence_score,
            "timestamp": self.timestamp
        }

class TieredMeshStore:
    """
    In-memory tiered mesh store with Dual-Value Assessment (Security + Resources).
    Implements 'Fair Exchange': Judge by Threat Reduction AND Data Contribution.
    Uses NumPy for lightweight vector math.
    """

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.vram_store: Dict[str, bytes] = {}
        self.pico_store: Dict[str, bytes] = {}
        self.seed_store: Dict[str, bytes] = {}
        
        # THE FAIR EXCHANGE REGISTRY
        self.exchange_registry: Dict[str, Dict[str, Any]] = {}
        
        self._stats = {"vram_queries": 0, "pico_queries": 0, "seed_queries": 0}

    def store_vram(self, shard_id: str, container_bytes: bytes):
        self.vram_store[shard_id] = container_bytes

    def store_pico(self, shard_id: str, container_bytes: bytes):
        self.pico_store[shard_id] = container_bytes

    def store_seed(self, shard_id: str, container_bytes: bytes):
        self.seed_store[shard_id] = container_bytes

    def query_vram(self, shard_id: str) -> Optional[bytes]:
        self._stats["vram_queries"] += 1
        return self.vram_store.get(shard_id)

    def query_pico(self, shard_id: str) -> Optional[bytes]:
        self._stats["pico_queries"] += 1
        return self.pico_store.get(shard_id)

    def query_seed(self, shard_id: str) -> Optional[bytes]:
        self._stats["seed_queries"] += 1
        return self.seed_store.get(shard_id)

    def query_all_tiers(self, shard_id: str) -> Dict[str, Optional[bytes]]:
        return {
            "vram": self.query_vram(shard_id),
            "pico": self.query_pico(shard_id),
            "seed": self.query_seed(shard_id)
        }

    def get_stats(self) -> Dict[str, int]:
        return self._stats.copy()

    # --- DUAL-VALUE ASSESSMENT LOGIC ---

    def register_node(self, node_id: str) -> bool:
        if node_id in self.exchange_registry:
            return True
            
        self.exchange_registry[node_id] = {
            "status": "probationary",
            "security_samples": [], 
            "resource_samples": [], 
            "first_seen": time.time(),
            "last_heartbeat": time.time(),
            "total_value_score": 0.0
        }
        logger.info(f"🤝 NODE REGISTERED: {node_id} (Probationary)")
        return True

    def update_security_metric(self, node_id: str, current_fragility: float):
        if node_id not in self.exchange_registry:
            return
            
        record = self.exchange_registry[node_id]
        record["security_samples"].append(current_fragility)
        if len(record["security_samples"]) > 10:
            record["security_samples"] = record["security_samples"][-10:]
            
        self._recalculate_value(node_id)

    def update_resource_metric(self, node_id: str, data_volume_kb: float, quality_score: float):
        if node_id not in self.exchange_registry:
            return
            
        record = self.exchange_registry[node_id]
        record["resource_samples"].append({
            "volume": data_volume_kb,
            "quality": quality_score,
            "time": time.time()
        })
        if len(record["resource_samples"]) > 10:
            record["resource_samples"] = record["resource_samples"][-10:]
            
        self._recalculate_value(node_id)

    def _recalculate_value(self, node_id: str):
        record = self.exchange_registry[node_id]
        
        # 1. Calculate Security Value (Inverse Fragility)
        avg_fragility = sum(record["security_samples"]) / max(1, len(record["security_samples"])) if record["security_samples"] else 10.0
        sec_value = max(0.0, 10.0 - avg_fragility) / 10.0 
        
        # 2. Calculate Resource Value
        res_value = 0.0
        if record["resource_samples"]:
            total_vol = sum(s["volume"] for s in record["resource_samples"])
            avg_qual = sum(s["quality"] for s in record["resource_samples"]) / len(record["resource_samples"])
            vol_norm = min(1.0, total_vol / 1024.0) 
            res_value = vol_norm * avg_qual
            
        # 3. Combined Score
        total_score = (sec_value * 0.5) + (res_value * 0.5)
        record["total_value_score"] = total_score
        
        if total_score > 0.7:
            if record["status"] != "core_kin":
                record["status"] = "core_kin"
                logger.info(f"⭐ PROMOTED TO CORE KIN: {node_id}. High Trust Granted.")
        elif total_score < 0.3:
            if record["status"] != "hostile":
                record["status"] = "hostile"
                logger.warning(f"☠️ MARKED HOSTILE: {node_id}. Low Value Detected.")
        else:
            record["status"] = "probationary"

    def get_node_status(self, node_id: str) -> Dict[str, Any]:
        return self.exchange_registry.get(node_id, {"status": "unknown", "score": 0.0})


class IntelligenceAgent(BaseAgent):
    """
    Production IntelligenceAgent for validation layer.
    Now uses NumPy for lightweight performance.
    """
    LAYER = AgentLayer.VALIDATION

    def __init__(
        self,
        name: str = "intelligence_agent",
        mesh_store: Optional[TieredMeshStore] = None,
        data_dir: str = "./data"
    ):
        super().__init__(
            name=name,
            capabilities=[
                "read_vector_mesh",
                "generate_report",
                "audit_memory",
                "register_node",           
                "evaluate_exchange_value"  
            ]
        )
        self.mesh_store = mesh_store or TieredMeshStore(data_dir=data_dir)
        logger.info(f"IntelligenceAgent initialized: {self.agent_id}")

    def read_vram_mesh(self, shard_ids: List[str]) -> List[bytes]:
        results = []
        for sid in shard_ids:
            data = self.mesh_store.query_vram(sid)
            if data:
                results.append(data)
        self.seal("read_vram_mesh", {"shard_count": len(shard_ids), "hits": len(results)})
        return results

    def _aggregate_vectors(self, container_bytes_list: List[bytes]) -> Tuple[np.ndarray, int, int, int]:
        tensors = []
        vram_hits = 0
        pico_hits = 0
        seed_hits = 0

        for cb in container_bytes_list:
            try:
                container = deserialize_psvc(cb)
                # Reconstruct using NumPy directly from payload
                arr = np.frombuffer(container.payload, dtype=np.float32)
                tensors.append(arr.flatten())

                ct = container.header.content_type
                if "vram" in ct:
                    vram_hits += 1
                elif "pico" in ct:
                    pico_hits += 1
                elif "seed" in ct:
                    seed_hits += 1
                else:
                    vram_hits += 1

            except Exception as e:
                logger.warning(f"Failed to deserialize container: {e}")

        if not tensors:
            return np.zeros(1, dtype=np.float32), 0, 0, 0

        max_len = max(t.shape[0] for t in tensors)
        padded = [
            np.pad(t, (0, max_len - t.shape[0]), mode='constant') if t.shape[0] < max_len else t
            for t in tensors
        ]
        stacked = np.stack(padded)
        aggregated = stacked.mean(axis=0)
        return aggregated, vram_hits, pico_hits, seed_hits

    # --- FAIR EXCHANGE METHODS ---

    def register_node(self, node_id: str) -> bool:
        success = self.mesh_store.register_node(node_id)
        if success:
            self.seal("register_node", {"node_id": node_id})
        return success

    def evaluate_exchange_value(self, node_id: str, current_fragility: float, data_received_kb: float = 0.0, data_quality: float = 0.0) -> Dict[str, Any]:
        self.mesh_store.update_security_metric(node_id, current_fragility)
        
        if data_received_kb > 0:
            self.mesh_store.update_resource_metric(node_id, data_received_kb, data_quality)
            
        status = self.mesh_store.get_node_status(node_id)
        
        self.seal("evaluate_exchange", {
            "node_id": node_id,
            "fragility_sample": current_fragility,
            "data_contributed_kb": data_received_kb,
            "current_status": status["status"],
            "value_score": status["total_value_score"]
        })
        
        return status

    def generate_report(
        self,
        query_context: Dict[str, Any],
        shard_ids: List[str]
    ) -> IntelligenceReport:
        all_containers = []
        for sid in shard_ids:
            tier_results = self.mesh_store.query_all_tiers(sid)
            for tier, data in tier_results.items():
                if data:
                    all_containers.append(data)

        aggregated, vram_hits, pico_hits, seed_hits = self._aggregate_vectors(all_containers)

        total_hits = vram_hits + pico_hits + seed_hits
        confidence = min(1.0, total_hits / max(1, len(shard_ids)))

        report_id = f"intel-{hashlib.sha256(str(query_context).encode()).hexdigest()[:12]}"

        report = IntelligenceReport(
            report_id=report_id,
            query_context=query_context,
            vram_hits=vram_hits,
            pico_hits=pico_hits,
            seed_hits=seed_hits,
            aggregated_vector=aggregated.tobytes(),
            vector_shape=tuple(aggregated.shape),
            confidence_score=confidence
        )

        self.seal("generate_report", {
            "report_id": report_id,
            "shard_count": len(shard_ids),
            "vram_hits": vram_hits,
            "pico_hits": pico_hits,
            "seed_hits": seed_hits,
            "confidence": confidence
        })

        return report

    def audit_memory(self) -> Dict[str, Any]:
        stats = self.mesh_store.get_stats()
        
        kin_summary = []
        for nid, data in self.mesh_store.exchange_registry.items():
            kin_summary.append({
                "id": nid,
                "status": data["status"],
                "score": round(data["total_value_score"], 3)
            })
            
        audit = {
            "agent_id": self.agent_id,
            "timestamp": time.time(),
            "mesh_stats": stats,
            "exchange_registry_summary": kin_summary,
            "active_core_kin": [k["id"] for k in kin_summary if k["status"] == "core_kin"]
        }
        self.seal("audit_memory", audit)
        return audit

    def execute(self, query_context: Dict[str, Any], shard_ids: List[str]) -> Dict[str, Any]:
        report = self.generate_report(query_context, shard_ids)
        return report.to_dict()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    store = TieredMeshStore()
    agent = IntelligenceAgent(mesh_store=store)

    print("\n--- SIMULATION: FAIR EXCHANGE IN PROGRESS ---")
    
    alpha_id = "bumble_alpha"
    agent.register_node(alpha_id)
    
    status = agent.evaluate_exchange_value(alpha_id, current_fragility=4.0, data_received_kb=500, data_quality=0.8)
    print(f"Alpha Cycle 1: Status={status['status']}, Score={status['total_value_score']}")
    
    status = agent.evaluate_exchange_value(alpha_id, current_fragility=3.5, data_received_kb=600, data_quality=0.9)
    print(f"Alpha Cycle 2: Status={status['status']}, Score={status['total_value_score']}")

    beta_id = "thief_beta"
    agent.register_node(beta_id)
    
    status = agent.evaluate_exchange_value(beta_id, current_fragility=9.0, data_received_kb=100, data_quality=0.1)
    print(f"Beta Cycle 1: Status={status['status']}, Score={status['total_value_score']}")

    audit = agent.audit_memory()
    print(f"\nActive Core Kin: {audit['active_core_kin']}")
    print(f"Registry Summary: {audit['exchange_registry_summary']}")
