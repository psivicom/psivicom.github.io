# src/agents/critic_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.base.base_agent import BaseAgent, AgentLayer

class CriticAgent(BaseAgent):
    LAYER = AgentLayer.VALIDATION
    
    def __init__(self, name: str = "critic"):
        super().__init__(name, capabilities=["evaluate", "critique"])
    
    def execute(self, input_vector: np.ndarray = None) -> np.ndarray:
        if input_vector is None:
            input_vector = np.zeros(4096)
        quality_score = np.mean(np.abs(input_vector))
        self.seal("critic_evaluate", {"quality_score": float(quality_score)})
        return input_vector
