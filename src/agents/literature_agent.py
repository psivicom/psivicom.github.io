# src/agents/literature_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# Literature Context Agent (Updated to use Discovery Agent)

import sys
import json
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.base.base_agent import BaseAgent, AgentLayer
from src.agents.discovery_agent import DiscoveryAgent
from psvc_reference import write_file, content_hash, PRECISION_FLOAT16

logger = logging.getLogger(__name__)

class LiteratureAgent(BaseAgent):
    LAYER = AgentLayer.INGESTION

    def __init__(self, name: str = "literature"):
        super().__init__(name, capabilities=["search", "ingest", "resolve"])
        self.discovery_agent = DiscoveryAgent()
        self.resolved_contexts: List[Dict] = []

    def execute(self, input_vector: np.ndarray = None, fragility_traps: List[Dict] = None) -> np.ndarray:
        if not fragility_traps:
            return np.zeros(4096)
        
        discovered_datasets = self.discovery_agent.execute(fragility_traps)
        
        for trap in fragility_traps:
            context = {
                "gene": trap.get("gene"),
                "organism": trap.get("organism"),
                "datasets_found": len(discovered_datasets),
                "resolution_status": "pending" if discovered_datasets else "unresolved"
            }
            self.resolved_contexts.append(context)
            self.seal("literature_context_resolved", context)
        
        vector = np.random.randn(4096).astype(np.float32)
        vector /= np.linalg.norm(vector)
        return vector

    def finalize(self, output_dir: Path = None):
        if output_dir is None:
            output_dir = Path("reports/pico_containers")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        vector = np.random.randn(4096).astype(np.float32)
        vector /= np.linalg.norm(vector)
        self.seal_result(vector, output_dir, meta={
            "resolved_contexts": self.resolved_contexts,
            "datasets_discovered": len(self.discovery_agent.discovered_datasets)
        })

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = LiteratureAgent()
    traps = [{"gene": "IGFBP7", "organism": "homo_sapiens", "tissue": "cells_cultured"}]
    agent.execute(fragility_traps=traps)
    agent.finalize()
    logger.info("Literature Agent complete")
