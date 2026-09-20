# src/agents/synthesizer_agent.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

"""
Production SynthesizerAgent: Aggregates validated shards and produces
the final research output.

Responsibilities:
- Aggregate validated .psvc containers
- Reconstruct full mathematical state
- Generate structured research output
- Produce final .psvc container for licensing
"""

import logging
import time
import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

import numpy as np
import torch

from src.base.base_agent import BaseAgent, AgentLayer
from psvc_containers import (
    PicoContainer,
    build_psvc_from_tensor,
    serialize_psvc,
    deserialize_psvc,
    reconstruct_torch_tensor,
    verify_container
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SynthesisResult:
    """Immutable synthesis output."""
    synthesis_id: str
    aggregated_tensor: bytes
    tensor_shape: tuple
    tensor_dtype: str
    statistics: Dict[str, float]
    source_container_count: int
    source_receipt_chain: List[str]
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "synthesis_id": self.synthesis_id,
            "tensor_shape": list(self.tensor_shape),
            "tensor_dtype": self.tensor_dtype,
            "statistics": self.statistics,
            "source_container_count": self.source_container_count,
            "source_receipt_chain": self.source_receipt_chain,
            "timestamp": self.timestamp
        }


class SynthesizerAgent(BaseAgent):
    """
    Production SynthesizerAgent for synthesis layer.
    """
    LAYER = AgentLayer.SYNTHESIS

    def __init__(
        self,
        name: str = "synthesizer_agent",
        aggregation_method: str = "mean",
        output_formats: Optional[List[str]] = None
    ):
        super().__init__(
            name=name,
            capabilities=[
                "aggregate_findings",
                "merge_shards",
                "compose_report",
                "generate_output"
            ]
        )
        self.aggregation_method = aggregation_method
        self.output_formats = output_formats or ["json"]
        self._stats = {
            "total_syntheses": 0,
            "containers_aggregated": 0,
            "failed_syntheses": 0
        }
        logger.info(
            f"SynthesizerAgent initialized: {self.agent_id} | "
            f"method={aggregation_method}"
        )

    def _validate_container(self, container_bytes: bytes) -> Tuple[bool, Optional[PicoContainer]]:
        """Validate a container before aggregation."""
        try:
            container = deserialize_psvc(container_bytes)
            verification = verify_container(container)
            if not all(verification.values()):
                return False, None
            return True, container
        except Exception as e:
            logger.error(f"Container validation failed: {e}")
            return False, None

    def aggregate_findings(self, container_bytes_list: List[bytes]) -> SynthesisResult:
        """
        Aggregate validated containers into a single synthesis result.
        """
        self._stats["total_syntheses"] += 1

        if not container_bytes_list:
            self._stats["failed_syntheses"] += 1
            raise ValueError("No containers to aggregate")

        # 1. Validate all containers
        valid_containers = []
        receipt_chain = []
        for cb in container_bytes_list:
            is_valid, container = self._validate_container(cb)
            if is_valid and container is not None:
                valid_containers.append(container)
                receipt_chain.append(container.receipt.payload_hash)

        if not valid_containers:
            self._stats["failed_syntheses"] += 1
            raise ValueError("No valid containers after validation")

        # 2. Reconstruct tensors
        tensors = []
        for container in valid_containers:
            tensor = reconstruct_torch_tensor(container)
            tensors.append(tensor.flatten())

        # 3. Aggregate based on method
        if self.aggregation_method == "mean":
            # Pad to same length if needed
            max_len = max(t.shape[0] for t in tensors)
            padded = [
                torch.cat([t, torch.zeros(max_len - t.shape[0])]) if t.shape[0] < max_len else t
                for t in tensors
            ]
            aggregated = torch.stack(padded).mean(dim=0)
        elif self.aggregation_method == "concat":
            aggregated = torch.cat(tensors, dim=0)
        elif self.aggregation_method == "weighted_mean":
            # Weight by container's flops_estimate
            weights = torch.tensor([
                c.payload.math_state.flops_estimate for c in valid_containers
            ], dtype=torch.float32)
            weights = weights / weights.sum()
            max_len = max(t.shape[0] for t in tensors)
            padded = [
                torch.cat([t, torch.zeros(max_len - t.shape[0])]) if t.shape[0] < max_len else t
                for t in tensors
            ]
            stacked = torch.stack(padded)
            aggregated = (stacked * weights.unsqueeze(1)).sum(dim=0)
        else:
            raise ValueError(f"Unknown aggregation method: {self.aggregation_method}")

        # 4. Compute statistics
        agg_np = aggregated.cpu().numpy()
        statistics = {
            "mean": float(np.mean(agg_np)),
            "std": float(np.std(agg_np)),
            "min": float(np.min(agg_np)),
            "max": float(np.max(agg_np)),
            "median": float(np.median(agg_np)),
            "l2_norm": float(np.linalg.norm(agg_np))
        }

        # 5. Build synthesis ID
        synthesis_id = f"synth-{hashlib.sha256(agg_np.tobytes()).hexdigest()[:12]}"

        result = SynthesisResult(
            synthesis_id=synthesis_id,
            aggregated_tensor=agg_np.tobytes(),
            tensor_shape=tuple(agg_np.shape),
            tensor_dtype=str(agg_np.dtype),
            statistics=statistics,
            source_container_count=len(valid_containers),
            source_receipt_chain=receipt_chain
        )

        self._stats["containers_aggregated"] += len(valid_containers)

        # 6. Seal the synthesis
        self.seal("aggregate_findings", {
            "synthesis_id": synthesis_id,
            "source_count": len(valid_containers),
            "method": self.aggregation_method,
            "statistics": statistics
        })

        logger.info(
            f"Synthesis {synthesis_id}: {len(valid_containers)} containers, "
            f"shape={result.tensor_shape}, method={self.aggregation_method}"
        )

        return result

    def compose_report(self, synthesis: SynthesisResult, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Compose a structured research report from synthesis."""
        report = {
            "synthesis_id": synthesis.synthesis_id,
            "metadata": metadata,
            "tensor_shape": list(synthesis.tensor_shape),
            "tensor_dtype": synthesis.tensor_dtype,
            "statistics": synthesis.statistics,
            "source_container_count": synthesis.source_container_count,
            "source_receipt_chain": synthesis.source_receipt_chain,
            "generated_at": time.time(),
            "generated_by": self.agent_id,
            "aggregation_method": self.aggregation_method
        }

        self.seal("compose_report", {
            "synthesis_id": synthesis.synthesis_id,
            "metadata_keys": list(metadata.keys())
        })

        return report

    def generate_output(
        self,
        synthesis: SynthesisResult,
        metadata: Dict[str, Any]
    ) -> bytes:
        """
        Generate final .psvc container output for licensing.
        """
        # Reconstruct tensor from synthesis
        tensor = torch.from_numpy(
            np.frombuffer(synthesis.aggregated_tensor, dtype=np.dtype(synthesis.tensor_dtype))
        ).reshape(synthesis.tensor_shape)

        # Build .psvc container
        container = build_psvc_from_tensor(
            tensor=tensor,
            operation="synthesis_output",
            agent_id=self.agent_id,
            layer=self.LAYER.name,
            shard_id=synthesis.synthesis_id,
            content_type="synthesized_report"
        )

        output_bytes = serialize_psvc(container)

        self.seal("generate_output", {
            "synthesis_id": synthesis.synthesis_id,
            "output_size": len(output_bytes)
        })

        logger.info(f"Generated output: {len(output_bytes)} bytes for {synthesis.synthesis_id}")
        return output_bytes

    def get_stats(self) -> Dict[str, int]:
        return self._stats.copy()

    def execute(
        self,
        container_bytes_list: List[bytes],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Main execution entry point."""
        metadata = metadata or {}
        synthesis = self.aggregate_findings(container_bytes_list)
        return self.generate_output(synthesis, metadata)


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create sample containers
    containers_bytes = []
    for i in range(5):
        tensor = torch.randn(50, dtype=torch.float32)
        container = build_psvc_from_tensor(
            tensor=tensor,
            operation=f"sample_{i}",
            agent_id="sample_agent",
            layer="INGESTION",
            shard_id=f"shard-{i}"
        )
        containers_bytes.append(serialize_psvc(container))

    # Run synthesizer
    synth = SynthesizerAgent(aggregation_method="mean")
    output_bytes = synth.execute(
        container_bytes_list=containers_bytes,
        metadata={"goal": "weather analysis", "region": "Montreal"}
    )

    print(f"\n=== Synthesis Output ===")
    print(f"Output size: {len(output_bytes)} bytes")
    print(f"Stats: {synth.get_stats()}")

    # Verify output
    output_container = deserialize_psvc(output_bytes)
    print(f"Output content type: {output_container.header.content_type}")
    print(f"Output tensor shape: {output_container.payload.tensor_shape}")
