# src/core/bare_metal_vector.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Bare-Metal VRAM Vector Engine.
Provides deterministic, low-level mathematical operations and memory management
for WENDY's cognitive state. Prioritizes raw byte-level precision for PSVC encapsulation.
"""

import logging
import numpy as np
from typing import Tuple, Optional
from src.core.zulu_clock import get_zulu_timestamp_ms

logger = logging.getLogger("BARE_METAL_VECTOR")

class VRAMVectorEngine:
    def __init__(self, dimension: int, dtype: np.dtype = np.float32):
        """
        Initializes a deterministic vector space in memory.
        In production, this maps directly to CUDA/Metal VRAM via CuPy or JAX.
        """
        self.dimension = dimension
        self.dtype = dtype
        # Allocate zeroed memory to prevent data leakage from previous states
        self.state = np.zeros(dimension, dtype=dtype)
        self.allocation_timestamp = get_zulu_timestamp_ms()
        logger.info(f"🧮 VRAM Vector Engine initialized: {dimension}D, {dtype}, {self.state.nbytes} bytes allocated.")

    def load_state(self, raw_bytes: bytes) -> bool:
        """Deserializes a raw byte payload directly into the VRAM state."""
        try:
            loaded_array = np.frombuffer(raw_bytes, dtype=self.dtype)
            if loaded_array.shape[0] != self.dimension:
                logger.error(f"❌ Dimension mismatch: expected {self.dimension}, got {loaded_array.shape[0]}")
                return False
            self.state = loaded_array
            logger.debug("✅ Vector state loaded from bare-metal payload.")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load vector state: {e}")
            return False

    def apply_transformation(self, matrix: np.ndarray) -> 'VRAMVectorEngine':
        """
        Applies a deterministic linear transformation.
        Ensures mathematical integrity before sealing.
        """
        if matrix.shape != (self.dimension, self.dimension):
            raise ValueError(f"Transformation matrix must be {self.dimension}x{self.dimension}")
        
        # Perform bare-metal matrix multiplication
        self.state = np.dot(matrix, self.state)
        logger.debug(f"⚡ Transformation applied. New state norm: {np.linalg.norm(self.state):.6f}")
        return self

    def get_raw_payload(self) -> bytes:
        """
        Extracts the absolute raw byte representation of the vector state.
        This is the exact payload that will be cryptographically sealed in a PSVC.
        """
        return self.state.tobytes()

    def get_metadata(self) -> dict:
        """Returns the cryptographic and structural metadata for the PSVC container."""
        return {
            "timestamp": get_zulu_timestamp_ms(),
            "dimension": self.dimension,
            "dtype": str(self.dtype),
            "byte_size": self.state.nbytes,
            "checksum": hex(hash(self.state.tobytes()) & 0xFFFFFFFF)
        }
