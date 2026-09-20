# src/core/vector_pixelizer.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

"""
Vector Pixelizer: Shards high-dimensional vectors into .psvc containers.
"""

import hashlib
import numpy as np
from typing import List

from psvc_containers import (
    PicoContainer,
    PSVCHeader,
    PSVCPayload,
    MathematicalState,
    AgentReceipt,
    build_psvc_from_tensor
)


class VectorPixelizer:
    def __init__(self, shard_size: int = 128):
        self.shard_size = shard_size

    def pixelize(self, vector: np.ndarray, receipt: AgentReceipt) -> List[PicoContainer]:
        """
        Split a 1D vector into sharded .psvc containers with chained receipts.
        """
        if vector.ndim != 1:
            raise ValueError(f"Vector must be 1D, got {vector.ndim}D")

        containers = []
        total_shards = (len(vector) + self.shard_size - 1) // self.shard_size

        for i in range(total_shards):
            start = i * self.shard_size
            end = min(start + self.shard_size, len(vector))
            shard = vector[start:end]

            container = build_psvc_from_tensor(
                tensor=shard,
                operation=f"pixelize_shard_{i}",
                agent_id="vector_pixelizer",
                layer="ORCHESTRATION",
                parent_receipt_hash=receipt.payload_hash,
                shard_id=f"{receipt.agent_id}-shard-{i}",
                content_type="vector_shard"
            )
            containers.append(container)

        return containers
