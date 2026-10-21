# src/base/base_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import numpy as np
from pathlib import Path
from enum import Enum

class AgentLayer(Enum):
    """
    RFC 1001: Canonical Agent Layers for the WENDY Platform.
    Ensures every organ has a defined, non-overlapping role in the sovereign architecture.
    """
    SENSORY = "sensory"       # e.g., Pilot Scan (External input scanning)
    COGNITIVE = "cognitive"   # e.g., Neuroplasticity (Learning, drift, adaptation)
    SYNTHESIS = "synthesis"   # e.g., Metabolic Sync, Report Generator (Aggregation)
    VALIDATION = "validation" # e.g., Ledger Validator, Void Metrics (Integrity checks)
    MOTOR = "motor"           # e.g., Mirror Agent (Action, commit, structural repair)
    INGESTION = "ingestion"   # e.g., Discovery Agent, Literature Agent (Data intake/parsing)

class BaseAgent:
    """
    The foundational contract for all WENDY agents.
    """
    def __init__(self, name: str, capabilities: list = None):
        self.name = name
        self.capabilities = capabilities or []
        # Graceful fallback if an agent forgets to define its LAYER
        self.layer = getattr(self, 'LAYER', AgentLayer.COGNITIVE)

    def seal_result(self, data: np.ndarray, path: Path, meta: dict = None):
        """
        Utility to save agent results securely and consistently.
        """
        if meta is None:
            meta = {}
            
        path.mkdir(parents=True, exist_ok=True)
        output_file = path / f"{self.name}_output.npy"
        np.save(output_file, data)
        print(f"💾 Sealed result for {self.name} at {output_file} | Meta: {meta}")
