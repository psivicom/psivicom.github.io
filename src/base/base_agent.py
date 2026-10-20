# src/base/base_agent.py
import numpy as np
from pathlib import Path
from enum import Enum

class AgentLayer(Enum):
    SENSORY = "sensory"
    COGNITIVE = "cognitive"
    VALIDATION = "validation"
    MOTOR = "motor"

class BaseAgent:
    def __init__(self, name: str, capabilities: list = []):
        self.name = name
        self.capabilities = capabilities

    def seal_result(self, data: np.ndarray, path: Path, meta: dict = {}):
        """Utility to save agent results securely."""
        path.mkdir(parents=True, exist_ok=True)
        output_file = path / f"{self.name}_output.npy"
        np.save(output_file, data)
        print(f"💾 Sealed result for {self.name} at {output_file}")
