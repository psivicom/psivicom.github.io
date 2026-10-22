# src/base/base_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import numpy as np
from pathlib import Path
from enum import Enum

class AgentLayer(Enum):
    """RFC 1001: Canonical Agent Layers for the WENDY Platform."""
    SENSORY = "sensory"
    COGNITIVE = "cognitive"
    SYNTHESIS = "synthesis"
    VALIDATION = "validation"
    MOTOR = "motor"
    INGESTION = "ingestion"
    ORCHESTRATION = "orchestration"

class BaseAgent:
    """The foundational contract for all WENDY agents."""
    def __init__(self, name: str, capabilities: list = None):
        self.name = name
        self.capabilities = capabilities or []
        self.layer = getattr(self, 'LAYER', AgentLayer.COGNITIVE)

    def seal(self, action: str, meta: dict = None):
        """Utility to log and seal an agent's action/result securely."""
        if meta is None:
            meta = {}
        print(f"💾 [SEALED] {self.name} | Action: {action} | Meta: {meta}")

    def seal_result(self, data: np.ndarray, path: Path, meta: dict = None):
        """Utility to save agent results securely and consistently to disk."""
        if meta is None:
            meta = {}
        path.mkdir(parents=True, exist_ok=True)
        output_file = path / f"{self.name}_output.npy"
        np.save(output_file, data)
        print(f"💾 Sealed result for {self.name} at {output_file} | Meta: {meta}")
