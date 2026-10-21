# src/base/base_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import numpy as np
from pathlib import Path
from enum import Enum

class AgentLayer(Enum):
    SENSORY = "sensory"
    COGNITIVE = "cognitive"
    SYNTHESIS = "synthesis"
    VALIDATION = "validation"
    MOTOR = "motor"
    INGESTION = "ingestion"

class BaseAgent:
    def __init__(self, name: str, capabilities: list = None):
        self.name = name
        self.capabilities = capabilities or []
        self.layer = getattr(self, 'LAYER', AgentLayer.COGNITIVE)

    def seal(self, action: str, meta: dict = None):
        if meta is None:
            meta = {}
        print(f"💾 [SEALED] {self.name} | Action: {action} | Meta: {meta}")

    def seal_result(self, data: np.ndarray, path: Path, meta: dict = None):
        if meta is None:
            meta = {}
        path.mkdir(parents=True, exist_ok=True)
        output_file = path / f"{self.name}_output.npy"
        np.save(output_file, data)
        print(f"💾 Sealed result for {self.name} at {output_file} | Meta: {meta}")
