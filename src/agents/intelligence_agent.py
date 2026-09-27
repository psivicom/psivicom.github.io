# src/agents/intelligence_agent.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

"""
Intelligence Agent for the PSIVI Hive Mind.

Responsibilities:
- Maintain tiered memory: VRAM, Pico, Seed.
- Aggregate PSVC vector containers into intelligence reports.
- Evaluate external volunteer nodes using Fair Exchange logic:
    security value + resource value.
- Persist exchange registry for Neuroplasticity.
- Finalize cleanly inside the dynamic orchestration chain.

This version is lightweight:
- NumPy only.
- No PyTorch dependency.
- Zulu UTC millisecond timestamps.
"""

import logging
import time
import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timezone

import numpy as np

from src.base.base_agent import BaseAgent, AgentLayer
from src.core.psvc_containers import (
    PicoContainer,
    build_psvc_from_array,
    serialize_psvc,
    deserialize_psvc,
    reconstruct_numpy_array,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Zulu Time Helpers
# ---------------------------------------------------------------------------

def _zulu_ms(dt: Optional[datetime] = None) -> str:
    """
    Returns strict Zulu UTC timestamp with milliseconds:

        2026-09-27T06:29:55.443Z
    """
    if dt is None:
        dt = datetime.now(timezone.utc)

    ms = dt.microsecond // 1000
    return f"{dt.strftime('%Y-%m-%dT%H:%M:%S')}.{ms:03d}Z"


# ---------------------------------------------------------------------------
# Intelligence Report
# ---------------------------------------------------------------------------

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
            "timestamp": self.timestamp,
            "timestamp_zulu": _zulu_ms(datetime.fromtimestamp(self.timestamp, tz=timezone.utc)),
        }


# ---------------------------------------------------------------------------
# Tiered Mesh Store
# ---------------------------------------------------------------------------

class TieredMeshStore:
    """
    In-memory tiered mesh store with Fair Exchange logic.

    Tiers:
    - VRAM: hot, recent, fast-access memory.
    - Pico: warm distributed cache.
    - Seed: cold archival memory.

    Exchange Registry:
    Tracks external volunteer nodes by observing behavior, not identity.

    Value formula:
        total_value = 0.5 * security_value + 0.5 * resource_value

    Status:
    - core_kin: high value, trusted mesh participant.
    - probationary: neutral / observing.
    - hostile: low value, excluded from privileged integration.
    """

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)

        self.vram_store: Dict[str, bytes] = {}
        self.pico_store: Dict[str, bytes] = {}
        self.seed_store: Dict[str, bytes] = {}

        # node_id -> exchange record
        self.exchange_registry: Dict[str, Dict[str, Any]] = {}

        self._stats = {
            "vram_queries": 0,
            "pico_queries": 0,
            "seed_queries": 0,
            "node_registrations": 0,
            "exchange_evaluations": 0,
        }

    # -----------------------------------------------------------------------
    # Storage API
    # -----------------------------------------------------------------------

    def store_vram(self, shard_id: str, container_bytes: bytes) -> None:
        self.vram_store[shard_id] = container_bytes

    def store_pico(self, shard_id: str, container_bytes: bytes) -> None:
        self.pico_store[shard_id] = container_bytes

    def store_seed(self, shard_id: str, container_bytes: bytes) -> None:
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
            "seed": self.query_seed(shard_id),
        }

    def get_stats(self) -> Dict[str, int]:
        return self._stats.copy()

    def all_shard_ids(self) -> List[str]:
        ids = set()
        ids.update(self.vram_store.keys())
        ids.update(self.pico_store.keys())
        ids.update(self.seed_store.keys())
        return sorted(ids)

    # -----------------------------------------------------------------------
    # Fair Exchange Registry
    # -----------------------------------------------------------------------

    def register_node(self, node_id: str) -> bool:
        """
        Registers a new external node into the exchange registry.

        New nodes begin as probationary. They are judged by behavior:
        - Did their presence reduce fragility?
        - Did they contribute useful resources?
        """
        if node_id in self.exchange_registry:
            return True

        self.exchange_registry[node_id] = {
            "status": "probationary",
            "security_samples": [],
            "resource_samples": [],
            "first_seen": time.time(),
            "last_heartbeat": time.time(),
            "total_value_score": 0.0,
        }

        self._stats["node_registrations"] += 1
        logger.info(f"🤝 NODE REGISTERED: {node_id} (probationary)")
        return True

    def update_security_metric(self, node_id: str, current_fragility: float) -> None:
        """
        Records fragility observed while node is active.

        Lower fragility implies the node may be acting as a sentinel / shield.
        """
        if node_id not in self.exchange_registry:
            return

        record = self.exchange_registry[node_id]
        record["security_samples"].append(float(current_fragility))
        record["last_heartbeat"] = time.time()

        if len(record["security_samples"]) > 10:
            record["security_samples"] = record["security_samples"][-10:]

        self._recalculate_value(node_id)

    def update_resource_metric(
        self,
        node_id: str,
        data_volume_kb: float,
        quality_score: float,
    ) -> None:
        """
        Records resource contribution from node.

        This is the 'nectar' side of the bumble bee exchange.
        """
        if node_id not in self.exchange_registry:
            return

        record = self.exchange_registry[node_id]
        record["resource_samples"].append(
            {
                "volume": float(data_volume_kb),
                "quality": float(quality_score),
                "time": time.time(),
            }
        )
        record["last_heartbeat"] = time.time()

        if len(record["resource_samples"]) > 10:
            record["resource_samples"] = record["resource_samples"][-10:]

        self._recalculate_value(node_id)

    def _recalculate_value(self, node_id: str) -> None:
        """
        Recalculates total value score and promotes/demotes node status.
        """
        record = self.exchange_registry[node_id]

        # Security value: inverse fragility.
        # Baseline fragility is assumed around 10.0 for normalization.
        if record["security_samples"]:
            avg_fragility = sum(record["security_samples"]) / len(record["security_samples"])
        else:
            avg_fragility = 10.0

        security_value = max(0.0, 10.0 - float(avg_fragility)) / 10.0

        # Resource value: volume * quality, normalized.
        resource_value = 0.0
        if record["resource_samples"]:
            total_volume = sum(sample["volume"] for sample in record["resource_samples"])
            avg_quality = sum(sample["quality"] for sample in record["resource_samples"]) / len(
                record["resource_samples"]
            )

            # Normalize volume: 1 MB considered full practical contribution for MVP.
            volume_norm = min(1.0, total_volume / 1024.0)
            resource_value = volume_norm * avg_quality

        total_score = (security_value * 0.5) + (resource_value * 0.5)
        record["total_value_score"] = float(total_score)

        # Status transitions.
        if total_score > 0.7:
            if record["status"] != "core_kin":
                record["status"] = "core_kin"
                logger.info(f"⭐ PROMOTED TO CORE KIN: {node_id}. High trust granted.")
        elif total_score < 0.3:
            if record["status"] != "hostile":
                record["status"] = "hostile"
                logger.warning(f"☠️ MARKED HOSTILE: {node_id}. Low value detected.")
        else:
            record["status"] = "probationary"

    def get_node_status(self, node_id: str) -> Dict[str, Any]:
        return self.exchange_registry.get(
            node_id,
            {
                "status": "unknown",
                "total_value_score": 0.0,
                "security_samples": [],
                "resource_samples": [],
            },
        )

    def get_active_core_kin(self) -> List[str]:
        return [
            node_id
            for node_id, record in self.exchange_registry.items()
            if record.get("status") == "core_kin"
        ]

    def get_registry_summary(self) -> List[Dict[str, Any]]:
        summary = []
        for node_id, record in self.exchange_registry.items():
            summary.append(
                {
                    "id": node_id,
                    "status": record.get("status", "unknown"),
                    "score": round(float(record.get("total_value_score", 0.0)), 3),
                    "security_samples": len(record.get("security_samples", [])),
                    "resource_samples": len(record.get("resource_samples", [])),
                }
            )
        return summary


# ---------------------------------------------------------------------------
# Intelligence Agent
# ---------------------------------------------------------------------------

class IntelligenceAgent(BaseAgent):
    """
    Validation-layer intelligence agent.

    Lifecycle:
    - initialized by orchestrator
    - optionally loads persisted exchange registry
    - generates intelligence reports
    - evaluates external volunteer nodes
    - persists exchange registry for Neuroplasticity
    - finalizes and seals result
    """

    LAYER = AgentLayer.VALIDATION

    def __init__(
        self,
        name: str = "intelligence_agent",
        mesh_store: Optional[TieredMeshStore] = None,
        data_dir: str = "./data",
    ):
        super().__init__(
            name=name,
            capabilities=[
                "read_vram_mesh",
                "read_pico_mesh",
                "read_seed_mesh",
                "generate_report",
                "audit_memory",
                "register_node",
                "evaluate_exchange_value",
                "persist_exchange_registry",
                "finalize",
            ],
        )

        self.mesh_store = mesh_store or TieredMeshStore(data_dir=data_dir)
        self.exchange_registry_file = Path("data/exchange_registry.json")

        self._load_exchange_registry()

        logger.info(f"IntelligenceAgent initialized: {self.agent_id}")

    # -----------------------------------------------------------------------
    # Exchange Registry Persistence
    # -----------------------------------------------------------------------

    def _load_exchange_registry(self) -> None:
        """
        Loads persisted exchange registry if available.

        Supported formats:
        1. New format:
            {
              "updated_at": "...",
              "active_core_kin": [...],
              "registry": {...}
            }

        2. Legacy/raw format:
            {
              "node_id": {...}
            }
        """
        if not self.exchange_registry_file.exists():
            return

        try:
            raw = json.loads(self.exchange_registry_file.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning(f"Could not load exchange registry: {exc}")
            return

        if not isinstance(raw, dict):
            return

        registry = raw.get("registry", raw)
        if not isinstance(registry, dict):
            return

        for node_id, record in registry.items():
            if not isinstance(record, dict):
                continue

            record.setdefault("status", "probationary")
            record.setdefault("security_samples", [])
            record.setdefault("resource_samples", [])
            record.setdefault("first_seen", time.time())
            record.setdefault("last_heartbeat", time.time())
            record.setdefault("total_value_score", 0.0)

            # Do not overwrite live current-run state if already present.
            self.mesh_store.exchange_registry.setdefault(str(node_id), record)

        logger.info(
            f"Loaded exchange registry: {len(self.mesh_store.exchange_registry)} node(s)"
        )

    def _persist_exchange_registry(self, audit: Optional[Dict[str, Any]] = None) -> Path:
        """
        Persists exchange registry to disk for Neuroplasticity and future runs.
        """
        self.exchange_registry_file.parent.mkdir(parents=True, exist_ok=True)

        registry = self.mesh_store.exchange_registry
        active_core_kin = self.mesh_store.get_active_core_kin()
        summary = self.mesh_store.get_registry_summary()

        payload = {
            "updated_at": _zulu_ms(),
            "agent_id": self.agent_id,
            "active_core_kin": active_core_kin,
            "registry_summary": summary,
            "registry": registry,
            "audit_excerpt": {
                "mesh_stats": (audit or {}).get("mesh_stats", {}),
                "vram_containers": (audit or {}).get("vram_containers", 0),
                "pico_containers": (audit or {}).get("pico_containers", 0),
                "seed_containers": (audit or {}).get("seed_containers", 0),
            },
        }

        self.exchange_registry_file.write_text(
            json.dumps(payload, indent=2, default=str),
            encoding="utf-8",
        )

        self.seal(
            "persist_exchange_registry",
            {
                "path": str(self.exchange_registry_file),
                "node_count": len(registry),
                "active_core_kin": active_core_kin,
            },
        )

        return self.exchange_registry_file

    # -----------------------------------------------------------------------
    # Mesh Read APIs
    # -----------------------------------------------------------------------

    def read_vram_mesh(self, shard_ids: List[str]) -> List[bytes]:
        results = []
        for sid in shard_ids:
            data = self.mesh_store.query_vram(sid)
            if data:
                results.append(data)

        self.seal(
            "read_vram_mesh",
            {
                "shard_count": len(shard_ids),
                "hits": len(results),
            },
        )
        return results

    def read_pico_mesh(self, shard_ids: List[str]) -> List[bytes]:
        results = []
        for sid in shard_ids:
            data = self.mesh_store.query_pico(sid)
            if data:
                results.append(data)

        self.seal(
            "read_pico_mesh",
            {
                "shard_count": len(shard_ids),
                "hits": len(results),
            },
        )
        return results

    def read_seed_mesh(self, shard_ids: List[str]) -> List[bytes]:
        results = []
        for sid in shard_ids:
            data = self.mesh_store.query_seed(sid)
            if data:
                results.append(data)

        self.seal(
            "read_seed_mesh",
            {
                "shard_count": len(shard_ids),
                "hits": len(results),
            },
        )
        return results

    # -----------------------------------------------------------------------
    # Vector Aggregation
    # -----------------------------------------------------------------------

    def _aggregate_vectors(
        self,
        container_bytes_list: List[bytes],
    ) -> Tuple[np.ndarray, int, int, int]:
        """
        Deserializes PSVC containers and aggregates their vectors by mean.

        Returns:
            aggregated_vector, vram_hits, pico_hits, seed_hits
        """
        tensors: List[np.ndarray] = []
        vram_hits = 0
        pico_hits = 0
        seed_hits = 0

        for cb in container_bytes_list:
            try:
                container = deserialize_psvc(cb)
                arr = reconstruct_numpy_array(container)
                arr = np.asarray(arr, dtype=np.float32).flatten()
                tensors.append(arr)

                content_type = str(container.header.content_type).lower()

                if "vram" in content_type:
                    vram_hits += 1
                elif "pico" in content_type:
                    pico_hits += 1
                elif "seed" in content_type:
                    seed_hits += 1
                else:
                    # Unknown content type defaults to hot memory classification.
                    vram_hits += 1

            except Exception as exc:
                logger.warning(f"Failed to deserialize container: {exc}")

        if not tensors:
            return np.zeros(1, dtype=np.float32), 0, 0, 0

        max_len = max(t.shape[0] for t in tensors)

        padded = []
        for t in tensors:
            if t.shape[0] < max_len:
                padded.append(np.pad(t, (0, max_len - t.shape[0]), mode="constant"))
            else:
                padded.append(t)

        stacked = np.stack(padded).astype(np.float32)
        aggregated = stacked.mean(axis=0).astype(np.float32)

        return aggregated, vram_hits, pico_hits, seed_hits

    # -----------------------------------------------------------------------
    # Fair Exchange API
    # -----------------------------------------------------------------------

    def register_node(self, node_id: str) -> bool:
        success = self.mesh_store.register_node(node_id)
        if success:
            self.seal("register_node", {"node_id": node_id})
        return success

    def evaluate_exchange_value(
        self,
        node_id: str,
        current_fragility: float,
        data_received_kb: float = 0.0,
        data_quality: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Updates both security and resource metrics for a node.

        This is the bumble bee fairness model:
        - protection counts
        - nectar counts
        - both together create core kin status
        """
        self.mesh_store.update_security_metric(node_id, float(current_fragility))

        if data_received_kb > 0:
            self.mesh_store.update_resource_metric(
                node_id,
                float(data_received_kb),
                float(data_quality),
            )

        self.mesh_store._stats["exchange_evaluations"] += 1

        status = self.mesh_store.get_node_status(node_id)

        self.seal(
            "evaluate_exchange",
            {
                "node_id": node_id,
                "fragility_sample": float(current_fragility),
                "data_contributed_kb": float(data_received_kb),
                "data_quality": float(data_quality),
                "current_status": status.get("status", "unknown"),
                "value_score": status.get("total_value_score", 0.0),
            },
        )

        return status

    # -----------------------------------------------------------------------
    # Reporting
    # -----------------------------------------------------------------------

    def generate_report(
        self,
        query_context: Dict[str, Any],
        shard_ids: List[str],
    ) -> IntelligenceReport:
        """
        Queries all tiers for the given shard IDs and produces an immutable report.
        """
        all_containers: List[bytes] = []

        for sid in shard_ids:
            tier_results = self.mesh_store.query_all_tiers(sid)
            for _tier, data in tier_results.items():
                if data:
                    all_containers.append(data)

        aggregated, vram_hits, pico_hits, seed_hits = self._aggregate_vectors(all_containers)

        total_hits = vram_hits + pico_hits + seed_hits
        denominator = max(1, len(shard_ids))
        confidence = min(1.0, total_hits / denominator)

        context_hash = hashlib.sha256(
            json.dumps(query_context, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()[:12]

        report_id = f"intel-{context_hash}"

        report = IntelligenceReport(
            report_id=report_id,
            query_context=query_context,
            vram_hits=vram_hits,
            pico_hits=pico_hits,
            seed_hits=seed_hits,
            aggregated_vector=aggregated.tobytes(),
            vector_shape=tuple(aggregated.shape),
            confidence_score=float(confidence),
        )

        self.seal(
            "generate_report",
            {
                "report_id": report_id,
                "shard_count": len(shard_ids),
                "vram_hits": vram_hits,
                "pico_hits": pico_hits,
                "seed_hits": seed_hits,
                "confidence": float(confidence),
                "vector_shape": list(aggregated.shape),
            },
        )

        return report

    def audit_memory(self) -> Dict[str, Any]:
        """
        Audits current mesh store state and exchange registry.
        """
        stats = self.mesh_store.get_stats()
        summary = self.mesh_store.get_registry_summary()
        active_core_kin = self.mesh_store.get_active_core_kin()

        audit = {
            "agent_id": self.agent_id,
            "timestamp": time.time(),
            "timestamp_zulu": _zulu_ms(),
            "mesh_stats": stats,
            "vram_containers": len(self.mesh_store.vram_store),
            "pico_containers": len(self.mesh_store.pico_store),
            "seed_containers": len(self.mesh_store.seed_store),
            "exchange_registry_summary": summary,
            "active_core_kin": active_core_kin,
        }

        self.seal("audit_memory", audit)
        return audit

    def execute(
        self,
        query_context: Dict[str, Any],
        shard_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Main execution entry point for direct API use.
        """
        report = self.generate_report(query_context, shard_ids)
        return report.to_dict()

    # -----------------------------------------------------------------------
    # Orchestrator Lifecycle
    # -----------------------------------------------------------------------

    def _build_default_query_context(self) -> Dict[str, Any]:
        """
        Builds query context from available upstream telemetry.

        If Pilot report exists, ingest its fragility/concordance signals.
        """
        context: Dict[str, Any] = {
            "agent_id": self.agent_id,
            "purpose": "automatic_chain_intelligence",
            "generated_at": _zulu_ms(),
        }

        pilot_report_path = Path("reports/pilot_report.json")

        if pilot_report_path.exists():
            try:
                pilot = json.loads(pilot_report_path.read_text(encoding="utf-8"))

                # Support both flat and nested payload structures.
                payload = pilot.get("payload", {}) if isinstance(pilot, dict) else {}

                context["pilot_fragility_count"] = (
                    pilot.get("fragility_count")
                    if isinstance(pilot, dict) and "fragility_count" in pilot
                    else payload.get("fragility_count", 0)
                )

                context["pilot_concordance_count"] = (
                    pilot.get("concordance_count")
                    if isinstance(pilot, dict) and "concordance_count" in pilot
                    else payload.get("concordance_count", 0)
                )

                context["pilot_report_present"] = True
            except Exception as exc:
                context["pilot_report_parse_error"] = str(exc)
                context["pilot_report_present"] = False
        else:
            context["pilot_report_present"] = False

        return context

    def finalize(self) -> bool:
        """
        Lifecycle completion method expected by chain_orchestrator.

        This method must not crash the chain. If internal intelligence fails,
        it seals a degraded result and returns False.
        """
        try:
            query_context = self._build_default_query_context()
            shard_ids = self.mesh_store.all_shard_ids()

            report = self.generate_report(query_context, shard_ids)
            audit = self.audit_memory()
            self._persist_exchange_registry(audit)

            # Reconstruct vector from report bytes for sealing.
            vector = np.frombuffer(report.aggregated_vector, dtype=np.float32).copy()

            meta = {
                "type": "intelligence_finalize",
                "report_id": report.report_id,
                "confidence_score": report.confidence_score,
                "vector_shape": list(report.vector_shape),
                "shard_count": len(shard_ids),
                "vram_hits": report.vram_hits,
                "pico_hits": report.pico_hits,
                "seed_hits": report.seed_hits,
                "active_core_kin": audit.get("active_core_kin", []),
                "exchange_registry_path": str(self.exchange_registry_file),
                "query_context": query_context,
            }

            self.seal_result(vector, Path("reports"), meta=meta)

            logger.info(
                "IntelligenceAgent finalized: "
                f"shards={len(shard_ids)}, "
                f"confidence={report.confidence_score:.3f}, "
                f"core_kin={len(audit.get('active_core_kin', []))}"
            )

            return True

        except Exception as exc:
            error_payload = {
                "error": str(exc),
                "error_type": type(exc).__name__,
                "at": _zulu_ms(),
            }

            self.seal("finalize_exception", error_payload)

            try:
                self.seal_result(
                    np.zeros(1, dtype=np.float32),
                    Path("reports"),
                    meta={
                        "type": "intelligence_finalize_failed",
                        "error": str(exc),
                        "error_type": type(exc).__name__,
                    },
                )
            except Exception:
                # Never allow finalize to crash the orchestrator.
                pass

            logger.error(f"IntelligenceAgent finalize failed: {exc}", exc_info=True)
            return False

    def run(self) -> bool:
        """
        Convenience alias for orchestrators that call run() instead of finalize().
        """
        return self.finalize()


# ---------------------------------------------------------------------------
# Local Simulation
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    store = TieredMeshStore()
    agent = IntelligenceAgent(mesh_store=store)

    print("\n--- SIMULATION: FAIR EXCHANGE IN PROGRESS ---")

    # 1. Bumble-like volunteer: protects and contributes.
    alpha_id = "bumble_alpha"
    agent.register_node(alpha_id)

    status = agent.evaluate_exchange_value(
        alpha_id,
        current_fragility=4.0,
        data_received_kb=500,
        data_quality=0.8,
    )
    print(f"Alpha Cycle 1: status={status['status']}, score={status['total_value_score']:.3f}")

    status = agent.evaluate_exchange_value(
        alpha_id,
        current_fragility=3.5,
        data_received_kb=600,
        data_quality=0.9,
    )
    print(f"Alpha Cycle 2: status={status['status']}, score={status['total_value_score']:.3f}")

    # 2. Thief-like node: high fragility, poor data.
    beta_id = "thief_beta"
    agent.register_node(beta_id)

    status = agent.evaluate_exchange_value(
        beta_id,
        current_fragility=9.0,
        data_received_kb=100,
        data_quality=0.1,
    )
    print(f"Beta Cycle 1: status={status['status']}, score={status['total_value_score']:.3f}")

    # 3. Insert a sample VRAM container.
    sample_vector = np.random.randn(50).astype(np.float32)
    container = build_psvc_from_array(
        array=sample_vector,
        operation="simulation_vector",
        agent_id="simulation_agent",
        layer="INGESTION",
        shard_id="shard-alpha",
        content_type="vram_vector",
        sender_id="internal_wendy",
    )

    store.store_vram("shard-alpha", serialize_psvc(container))

    # 4. Generate report.
    report = agent.generate_report(
        query_context={"goal": "simulation", "source": "local_test"},
        shard_ids=["shard-alpha"],
    )

    print("\n--- INTELLIGENCE REPORT ---")
    print(json.dumps(report.to_dict(), indent=2, default=str))

    # 5. Audit and finalize.
    audit = agent.audit_memory()
    print("\n--- MEMORY AUDIT ---")
    print(json.dumps(audit, indent=2, default=str))

    finalized = agent.finalize()
    print(f"\nFinalized: {finalized}")
