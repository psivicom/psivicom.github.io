# research_pipeline.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

"""
End-to-End Research Pipeline — Production Demonstration
"""

import hashlib
import time
import logging
from typing import List, Dict, Any

import torch
import numpy as np

from psvc_containers import (
    PicoContainer,
    build_psvc_from_tensor,
    serialize_psvc,
    deserialize_psvc,
    verify_container,
    reconstruct_torch_tensor,
    MathematicalState
)
from src.base.base_agent import BaseAgent, AgentLayer

logger = logging.getLogger(__name__)


class ForageAgent(BaseAgent):
    LAYER = AgentLayer.INGESTION

    def __init__(self, name: str = "forage_agent"):
        super().__init__(name=name)
        self.embedding_matrix = torch.randn(1000, 512, dtype=torch.float16)

    def fetch_weather_data(self, location: str) -> Dict[str, Any]:
        from src.agents.forage_agent import ForageAgent as RealForage
        try:
            real = RealForage(name=self.name)
            return real.fetch_weather(latitude=45.5017, longitude=-73.5673, days=7)
        except Exception as e:
            logger.warning(f"Real API unavailable ({e}), using fallback data")
            return {
                "location": location,
                "temperature": 22.5,
                "humidity": 65,
                "daily": {
                    "temperature_2m_max": [22.0, 23.0, 21.5, 24.0, 22.5, 23.5, 21.0],
                    "temperature_2m_min": [15.0, 16.0, 14.5, 17.0, 15.5, 16.5, 14.0],
                    "precipitation_sum": [0.0, 2.5, 0.0, 0.0, 5.0, 0.0, 1.0],
                    "windspeed_10m_max": [12.0, 15.0, 10.0, 18.0, 14.0, 11.0, 16.0],
                    "relative_humidity_2m_max": [65, 70, 60, 75, 80, 68, 72]
                },
                "fetched_at": time.time()
            }

    def embed_data(self, data: Dict[str, Any]) -> torch.Tensor:
        daily = data.get("daily", {})
        temp_max = np.array(daily.get("temperature_2m_max", []), dtype=np.float32)
        temp_min = np.array(daily.get("temperature_2m_min", []), dtype=np.float32)
        precip = np.array(daily.get("precipitation_sum", []), dtype=np.float32)
        wind = np.array(daily.get("windspeed_10m_max", []), dtype=np.float32)
        humidity = np.array(daily.get("relative_humidity_2m_max", []), dtype=np.float32)

        if len(temp_max) == 0:
            return torch.zeros(35, dtype=torch.float32)

        features = np.stack([temp_max, temp_min, precip, wind, humidity], axis=1)
        features = (features - features.mean(axis=0)) / (features.std(axis=0) + 1e-8)
        return torch.tensor(features.flatten(), dtype=torch.float32)

    def create_containers(self, vectors: torch.Tensor) -> List[PicoContainer]:
        containers = []
        shard_size = 5
        for i in range(0, vectors.shape[0], shard_size):
            shard = vectors[i:i+shard_size]
            container = build_psvc_from_tensor(
                tensor=shard,
                operation=f"embed_weather_shard_{i}",
                agent_id=self.agent_id,
                layer=self.LAYER.name,
                shard_id=f"{self.agent_id}-shard-{i}",
                content_type="weather_vector_shard"
            )
            containers.append(container)
        return containers


class VolunteerWorker(BaseAgent):
    LAYER = AgentLayer.INGESTION

    def __init__(self, name: str = "volunteer_worker"):
        super().__init__(name=name)

    def process_container(self, container_bytes: bytes) -> bytes:
        from src.orchestrator.mesh_governor import audit_psvc_container

        audit_result = audit_psvc_container(container_bytes)
        if not audit_result.is_valid:
            raise PermissionError(f"RFC 1001 Violation: {audit_result.checks_failed}")

        container = deserialize_psvc(container_bytes)
        tensor = reconstruct_torch_tensor(container)
        processed_tensor = tensor * 1.05

        new_container = build_psvc_from_tensor(
            tensor=processed_tensor,
            operation="volunteer_scale_transform",
            agent_id=self.agent_id,
            layer=self.LAYER.name,
            parent_receipt_hash=container.receipt.payload_hash,
            shard_id=f"processed-{container.header.shard_id}",
            content_type=f"processed_{container.header.content_type}"
        )
        return serialize_psvc(new_container)


class SynthesizerAgent(BaseAgent):
    LAYER = AgentLayer.SYNTHESIS

    def __init__(self, name: str = "synthesizer_agent"):
        super().__init__(name=name)

    def aggregate_containers(self, container_bytes_list: List[bytes]) -> torch.Tensor:
        from src.orchestrator.mesh_governor import audit_psvc_container
        tensors = []
        for cb in container_bytes_list:
            audit_result = audit_psvc_container(cb)
            if not audit_result.is_valid:
                raise PermissionError(f"Aggregation failed: {audit_result.checks_failed}")
            container = deserialize_psvc(cb)
            tensors.append(reconstruct_torch_tensor(container))
        return torch.cat(tensors, dim=0)

    def generate_report(self, tensor: torch.Tensor, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "summary": f"Processed {tensor.shape[0]} vector dimensions",
            "tensor_shape": list(tensor.shape),
            "tensor_mean": tensor.mean().item(),
            "tensor_std": tensor.std().item(),
            "metadata": metadata,
            "timestamp": time.time()
        }


class LicenseAgent(BaseAgent):
    LAYER = AgentLayer.GOVERNANCE

    def __init__(self, name: str = "license_agent"):
        super().__init__(name=name)

    def stamp_fair(self, report: Dict[str, Any]) -> Dict[str, Any]:
        report["_psivi_fair_metadata"] = {
            "psivi_license": "CC-BY-4.0",
            "author": "Louis-Philippe Audette",
            "project": "psivicom.github.io",
            "timestamp": time.time(),
            "findable": True,
            "accessible": True,
            "interoperable": True,
            "reusable": True,
            "rfc1001_compliant": True
        }
        self.seal("stamp_fair", report)
        return report


def run_research_pipeline():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logger.info("=" * 80)
    logger.info("PSIVI Open Science Research Pipeline")
    logger.info("=" * 80)

    forage = ForageAgent()
    worker = VolunteerWorker()
    synthesizer = SynthesizerAgent()
    licensor = LicenseAgent()

    logger.info(f"Agents: {forage.agent_id}, {worker.agent_id}, {synthesizer.agent_id}, {licensor.agent_id}")

    # Step 1: Fetch
    logger.info("Step 1: Fetching weather data...")
    raw_data = forage.fetch_weather_data("Montreal")
    logger.info(f"  Fetched: {raw_data.get('location', 'unknown')}")

    # Step 2: Embed
    logger.info("Step 2: Embedding to tensor...")
    vectors = forage.embed_data(raw_data)
    logger.info(f"  Shape: {vectors.shape}")

    # Step 3: Containerize
    logger.info("Step 3: Creating .psvc containers...")
    containers = forage.create_containers(vectors)
    serialized = [serialize_psvc(c) for c in containers]
    logger.info(f"  Created {len(serialized)} containers, {sum(len(s) for s in serialized)} bytes total")

    # Step 4: Volunteer processing
    logger.info("Step 4: Volunteer worker processing...")
    processed = []
    for i, cb in enumerate(serialized):
        result = worker.process_container(cb)
        processed.append(result)
        logger.info(f"  Shard {i+1}/{len(serialized)} processed")

    # Step 5: Synthesize
    logger.info("Step 5: Synthesizing results...")
    aggregated = synthesizer.aggregate_containers(processed)
    report = synthesizer.generate_report(aggregated, {"goal": "Analyze weather patterns in Montreal"})
    logger.info(f"  {report['summary']}")

    # Step 6: FAIR stamp
    logger.info("Step 6: FAIR compliance stamping...")
    final = licensor.stamp_fair(report)
    logger.info(f"  License: {final['_psivi_fair_metadata']['psivi_license']}")

    # Final verification
    logger.info("Final verification...")
    all_valid = True
    for cb in processed:
        c = deserialize_psvc(cb)
        v = verify_container(c)
        if not all(v.values()):
            all_valid = False
            logger.warning(f"  FAILED: {v}")
    if all_valid:
        logger.info("  ✓ All containers verified")

    logger.info("=" * 80)
    logger.info("PIPELINE COMPLETE")
    return final


if __name__ == "__main__":
    final_report = run_research_pipeline()
    print("\n📊 FINAL OUTPUT:")
    for k, v in final_report.items():
        if k != "_psivi_fair_metadata":
            print(f"  {k}: {v}")
    print("\n🔒 FAIR METADATA:")
    for k, v in final_report["_psivi_fair_metadata"].items():
        print(f"  {k}: {v}")
