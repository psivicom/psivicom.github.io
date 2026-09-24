# src/agents/consolidator_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.base.base_agent import BaseAgent, AgentLayer

class ConsolidatorAgent(BaseAgent):
    LAYER = AgentLayer.SYNTHESIS
    
    def __init__(self, name: str = "consolidator"):
        super().__init__(name, capabilities=["synthesize", "prune"])
    
    def execute(self, input_vector: np.ndarray = None) -> np.ndarray:
        if input_vector is None:
            input_vector = np.zeros(4096)
        self.seal("consolidator_prune", {"input_norm": float(np.linalg.norm(input_vector))})
        return input_vector
