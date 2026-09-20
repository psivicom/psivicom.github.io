# src/agents/consolidator_agent.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

"""
Production ConsolidatorAgent: Aggregates daily vector shards and updates mesh weights.
"""

import logging
import time
from typing import Dict, Any, List
import numpy as np
import torch

from src.base.base_agent import BaseAgent, AgentLayer
from psvc_containers import build_psvc_from_tensor, serialize_psvc

logger = logging.getLogger(__name__)

class ConsolidatorAgent(BaseAgent):
    LAYER = AgentLayer.SYNTHESIS

    def __init__(self, name: str = "consolidator_agent"):
        super().__init__(
            name=name,
            capabilities=["aggregate_findings", "merge_shards", "update_mesh_weights"]
        )
        logger.info(f"ConsolidatorAgent initialized: {self.agent_id}")

    def merge_shards(self, shard_data: List[np.ndarray]) -> np.ndarray:
        """Merge multiple vector shards into a single consolidated array."""
        if not shard_data:
            return np.array([])
        
        # Pad arrays to the same length and compute mean
        max_len = max(len(arr) for arr in shard_data)
        padded = [
            np.pad(arr, (0, max_len - len(arr)), mode='constant') 
            for arr in shard_data
        ]
        consolidated = np.mean(padded, axis=0)
        return consolidated

    def execute(self) -> bytes:
        """Main execution: simulate consolidation and seal into .psvc container."""
        logger.info("Executing consolidation routine...")
        
        # Simulate aggregated daily data
        mock_shards = [np.random.randn(128).astype(np.float32) for _ in range(5)]
        consolidated_vector = self.merge_shards(mock_shards)
        
        # Seal operation
        receipt = self.seal(
            operation="merge_daily_shards",
            payload={"shard_count": len(mock_shards), "output_dim": len(consolidated_vector)}
        )
        
        # Build .psvc container
        container = build_psvc_from_tensor(
            tensor=consolidated_vector,
            operation="daily_consolidation",
            agent_id=self.agent_id,
            layer=self.LAYER.name,
            parent_receipt_hash=receipt.payload_hash,
            content_type="consolidated_vector"
        )
        
        return serialize_psvc(container)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = ConsolidatorAgent()
    result = agent.execute()
    print(f"✅ Consolidation complete. Container size: {len(result)} bytes")
