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
import torch

# CORRECT absolute imports
from src.base.base_agent import BaseAgent, AgentLayer
from src.core.psvc_containers import (
    PicoContainer,
    build_psvc_from_tensor,
    serialize_psvc,
    deserialize_psvc,
    reconstruct_torch_tensor
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
    In-memory tiered mesh store with Dynamic Trust Scores.
    Implements 'Cuticular Hydrocarbon' logic: Judge by action, not identity.
    """

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.vram_store: Dict[str, bytes] = {}  # shard_id -> serialized container
        self.pico_store: Dict[str, bytes] = {}
        self.seed_store: Dict[str, bytes] = {}
        
        # THE HIVE MEMORY: Tracks trust scores per sender based on recent impact
        # Format: { "sender_id": {"score": 0.5, "last_impact": "positive", "count": 10} }
        self.trust_registry: Dict[str, Dict[str, Any]] = {}
        
        self._stats = {"vram_queries": 0, "pico_queries": 0, "seed_queries": 0, "quarantine_events": 0}

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

    # --- NEW: DYNAMIC TRUST LOGIC ---

    def evaluate_trust(self, sender_id: str, impact_metric: float) -> bool:
        """
        Updates the trust score for a sender based on observed impact.
        
        Args:
            sender_id: The ID of the external agent/node.
            impact_metric: 
                Positive (>0) means helpful (reduced fragility, increased stability).
                Negative (<0) means harmful (increased errors, stress spikes).
                Zero (0) means neutral/noise.
                
        Returns:
            True if the sender should be allowed to integrate further, False if quarantined.
        """
        if sender_id not in self.trust_registry:
            # Newcomer starts with neutral caution (0.5)
            self.trust_registry[sender_id] = {"score": 0.5, "history": []}
        
        record = self.trust_registry[sender_id]
        
        # Exponential Moving Average for smooth trust updates
        alpha = 0.1 
        new_score = (alpha * impact_metric) + ((1 - alpha) * record["score"])
        
        # Clamp between 0.0 (Hostile/Virus) and 1.0 (Kin/Benefactor)
        record["score"] = max(0.0, min(1.0, new_score))
        record["history"].append({
            "time": time.time(),
            "impact": impact_metric,
            "new_score": record["score"]
        })
        
        # Keep history manageable
        if len(record["history"]) > 50:
            record["history"] = record["history"][-50:]
            
        logger.info(f"Hive Trust Update: Sender '{sender_id}' Score: {record['score']:.3f}")
        
        # Threshold for acceptance: Must be above 0.6 (clearly beneficial)
        # Below 0.4 triggers quarantine/isolation
        return record["score"] >= 0.6

    def get_trust_status(self, sender_id: str) -> Dict[str, Any]:
        return self.trust_registry.get(sender_id, {"score": 0.5, "status": "unknown"})


class IntelligenceAgent(BaseAgent):
    """
    Production IntelligenceAgent for validation layer.
    Now includes Behavioral Tolerance (Hive Logic).
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
                "read_pico_mesh",
                "read_vram_mesh",
                "read_seed_mesh",
                "generate_report",
                "audit_memory",
                "evaluate_external_input" # NEW CAPABILITY
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

    def read_pico_mesh(self, shard_ids: List[str]) -> List[bytes]:
        results = []
        for sid in shard_ids:
            data = self.mesh_store.query_pico(sid)
            if data:
                results.append(data)
        self.seal("read_pico_mesh", {"shard_count": len(shard_ids), "hits": len(results)})
        return results

    def read_seed_mesh(self, shard_ids: List[str]) -> List[bytes]:
        results = []
        for sid in shard_ids:
            data = self.mesh_store.query_seed(sid)
            if data:
                results.append(data)
        self.seal("read_seed_mesh", {"shard_count": len(shard_ids), "hits": len(results)})
        return results

    def _aggregate_vectors(self, container_bytes_list: List[bytes]) -> Tuple[torch.Tensor, int, int, int]:
        tensors = []
        vram_hits = 0
        pico_hits = 0
        seed_hits = 0

        for cb in container_bytes_list:
            try:
                container = deserialize_psvc(cb)
                tensor = reconstruct_torch_tensor(container)
                tensors.append(tensor.flatten())

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
            return torch.zeros(1, dtype=torch.float32), 0, 0, 0

        max_len = max(t.shape[0] for t in tensors)
        padded = [
            torch.cat([t, torch.zeros(max_len - t.shape[0])]) if t.shape[0] < max_len else t
            for t in tensors
        ]
        stacked = torch.stack(padded)
        aggregated = stacked.mean(dim=0)
        return aggregated, vram_hits, pico_hits, seed_hits

    # --- NEW: BEHAVIORAL EVALUATION METHOD ---

    def evaluate_external_input(self, container: PicoContainer, current_fragility_delta: float) -> bool:
        """
        Called when an external PSVC arrives.
        
        Args:
            container: The incoming PSVC from a volunteer node.
            current_fragility_delta: How much Wendy's fragility changed AFTER processing this input.
                                     Negative delta = Good (Stability improved).
                                     Positive delta = Bad (Instability introduced).
                                     
        Returns:
            True if integrated, False if quarantined/rejected.
        """
        sender = container.header.sender_id
        
        # Convert Fragility Delta to Impact Metric
        # We invert it because lower fragility is better.
        # Normalize roughly to [-1.0, 1.0] range for simplicity
        impact_metric = -current_fragility_delta 
        
        accepted = self.mesh_store.evaluate_trust(sender, impact_metric)
        
        if accepted:
            logger.info(f"🐝 KIN RECOGNIZED: Sender '{sender}' accepted into mesh.")
            self.seal("integrate_external", {"sender": sender, "impact": impact_metric})
        else:
            logger.warning(f"⚠️ QUARANTINE: Sender '{sender}' rejected due to low trust score.")
            self.seal("quarantine_external", {"sender": sender, "impact": impact_metric})
            
        return accepted

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
            aggregated_vector=aggregated.numpy().tobytes(),
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
        audit = {
            "agent_id": self.agent_id,
            "timestamp": time.time(),
            "mesh_stats": stats,
            "vram_containers": len(self.mesh_store.vram_store),
            "pico_containers": len(self.mesh_store.pico_store),
            "seed_containers": len(self.mesh_store.seed_store),
            "hive_trust_registry": self.mesh_store.trust_registry # EXPOSE TRUST SCORES
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

    # Simulate a Volunteer Node sending help
    print("\n--- SIMULATION: VOLUNTEER NODE ARRIVES ---")
    
    # 1. Create a fake handshake offer
    tensor = torch.randn(50, dtype=torch.float32)
    container = build_psvc_from_tensor(
        tensor=tensor,
        operation="resource_share",
        agent_id="volunteer_node_7",
        layer="INGESTION",
        shard_id="ext-shard-1",
        content_type="handshake_offer",
        sender_id="volunteer_node_7"
    )
    
    # 2. Process it. Assume it helped reduce fragility by 0.1 units.
    # In real code, the BreathEngine would pass the actual delta here.
    success = agent.evaluate_external_input(container, current_fragility_delta=-0.1)
    
    if success:
        print("✅ Integration Successful. Data merged into Mesh.")
    else:
        print("❌ Rejected. Sent to Quarantine.")

    # 3. Check Trust Registry
    status = store.get_trust_status("volunteer_node_7")
    print(f"Current Trust Score for volunteer_node_7: {status['score']}")
