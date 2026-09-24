# src/agents/forage_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.base.base_agent import BaseAgent, AgentLayer
from psvc_reference import write_file, content_hash, PRECISION_FLOAT16

class ForageAgent(BaseAgent):
    LAYER = AgentLayer.INGESTION
    
    def __init__(self, name: str = "forage"):
        super().__init__(name, capabilities=["collect", "observe"])
    
    def execute(self, input_vector: np.ndarray = None) -> np.ndarray:
        vector = np.random.randn(4096).astype(np.float32)
        vector /= np.linalg.norm(vector)
        self.seal("forage_collect", {"vector_shape": vector.shape})
        return vector
