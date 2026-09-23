# src/agents/intelligence_agent.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

import logging
import time
import hashlib
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
    In-memory tiered mesh store for intelligence queries.
    In production, this would connect to actual VRAM, distributed, and archive stores.
    """

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.vram_store: Dict[str, bytes] = {}  # shard_id -> serialized container
        self.pico_store: Dict[str, bytes] = {}
        self.seed_store: Dict[str, bytes] = {}
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

class IntelligenceAgent(BaseAgent):
    """
    Production IntelligenceAgent for validation layer.
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
                "audit_memory"
            ]
        )
        self.mesh_store = mesh_store or TieredMeshStore(data_dir=data_dir)
        logger.info(f"IntelligenceAgent initialized: {self.agent_id}")

    def read_vram_mesh(self, shard_ids: List[str]) -> List[bytes]:
        """Read hot vectors from VRAM tier."""
        results = []
        for sid in shard_ids:
            data = self.mesh_store.query_vram(sid)
            if data:
                results.append(data)
        self.seal("read_vram_mesh", {"shard_count": len(shard_ids), "hits": len(results)})
        return results

    def read_pico_mesh(self, shard_ids: List[str]) -> List[bytes]:
        """Read from distributed Pico cache."""
        results = []
        for sid in shard_ids:
            data = self.mesh_store.query_pico(sid)
            if data:
                results.append(data)
        self.seal("read_pico_mesh", {"shard_count": len(shard_ids), "hits": len(results)})
        return results

    def read_seed_mesh(self, shard_ids: List[str]) -> List[bytes]:
        """Read from immutable Seed archive."""
        results = []
        for sid in shard_ids:
            data = self.mesh_store.query_seed(sid)
            if data:
                results.append(data)
        self.seal("read_seed_mesh", {"shard_count": len(shard_ids), "hits": len(results)})
        return results

    def _aggregate_vectors(self, container_bytes_list: List[bytes]) -> Tuple[torch.Tensor, int, int, int]:
        """
        Aggregate vectors from multiple containers.
        Returns: (aggregated_tensor, vram_hits, pico_hits, seed_hits)
        """
        tensors = []
        vram_hits = 0
        pico_hits = 0
        seed_hits = 0

        for cb in container_bytes_list:
            try:
                container = deserialize_psvc(cb)
                tensor = reconstruct_torch_tensor(container)
                tensors.append(tensor.flatten())

                # Track tier hits based on content type
                ct = container.header.content_type
                if "vram" in ct:
                    vram_hits += 1
                elif "pico" in ct:
                    pico_hits += 1
                elif "seed" in ct:
                    seed_hits += 1
                else:
                    vram_hits += 1  # Default to vram

            except Exception as e:
                logger.warning(f"Failed to deserialize container: {e}")

        if not tensors:
            return torch.zeros(1, dtype=torch.float32), 0, 0, 0

        # Pad tensors to same length for stacking
        max_len = max(t.shape[0] for t in tensors)
        padded = [
            torch.cat([t, torch.zeros(max_len - t.shape[0])]) if t.shape[0] < max_len else t
            for t in tensors
        ]
        stacked = torch.stack(padded)

        # Mean aggregation (could be weighted, attention-based, etc.)
        aggregated = stacked.mean(dim=0)
        return aggregated, vram_hits, pico_hits, seed_hits

    def generate_report(
        self,
        query_context: Dict[str, Any],
        shard_ids: List[str]
    ) -> IntelligenceReport:
        """
        Generate intelligence report from mesh queries.
        """
        # Query all tiers
        all_containers = []
        for sid in shard_ids:
            tier_results = self.mesh_store.query_all_tiers(sid)
            for tier, data in tier_results.items():
                if data:
                    all_containers.append(data)

        # Aggregate vectors
        aggregated, vram_hits, pico_hits, seed_hits = self._aggregate_vectors(all_containers)

        # Confidence score based on data availability
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

        logger.info(
            f"Intelligence report {report_id}: "
            f"vram={vram_hits}, pico={pico_hits}, seed={seed_hits}, "
            f"confidence={confidence:.3f}"
        )

        return report

    def audit_memory(self) -> Dict[str, Any]:
        """Audit current mesh store state."""
        stats = self.mesh_store.get_stats()
        audit = {
            "agent_id": self.agent_id,
            "timestamp": time.time(),
            "mesh_stats": stats,
            "vram_containers": len(self.mesh_store.vram_store),
            "pico_containers": len(self.mesh_store.pico_store),
            "seed_containers": len(self.mesh_store.seed_store)
        }
        self.seal("audit_memory", audit)
        return audit

    def execute(self, query_context: Dict[str, Any], shard_ids: List[str]) -> Dict[str, Any]:
        """Main execution entry point."""
        report = self.generate_report(query_context, shard_ids)
        return report.to_dict()

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Setup mesh store with sample data
    store = TieredMeshStore()
    agent = IntelligenceAgent(mesh_store=store)

    # Populate with sample containers
    for i in range(3):
        tensor = torch.randn(50, dtype=torch.float32)
        container = build_psvc_from_tensor(
            tensor=tensor,
            operation=f"sample_{i}",
            agent_id="sample_agent",
            layer="INGESTION",
            shard_id=f"shard-{i}",
            content_type="vram_vector" if i == 0 else ("pico_vector" if i == 1 else "seed_vector")
        )
        cb = serialize_psvc(container)
        if i == 0:
            store.store_vram(f"shard-{i}", cb)
        elif i == 1:
            store.store_pico(f"shard-{i}", cb)
        else:
            store.store_seed(f"shard-{i}", cb)

    # Generate intelligence report
    report = agent.generate_report(
        query_context={"goal": "weather analysis", "region": "Montreal"},
        shard_ids=["shard-0", "shard-1", "shard-2"]
    )

    print(f"\n=== Intelligence Report ===")
    print(f"Report ID: {report.report_id}")
    print(f"VRAM hits: {report.vram_hits}")
    print(f"Pico hits: {report.pico_hits}")
    print(f"Seed hits: {report.seed_hits}")
    print(f"Vector shape: {report.vector_shape}")
    print(f"Confidence: {report.confidence_score:.3f}")
    print(f"\nMemory audit: {agent.audit_memory()}")
