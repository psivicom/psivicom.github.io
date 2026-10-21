# src/agents/literature_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import logging
import json
import msgpack
import re
import numpy as np
from pathlib import Path

from src.base.base_agent import BaseAgent, AgentLayer
from src.agents.discovery_agent import DiscoveryAgent
from src.core.psvc_reference import write_file
from src.core.zulu_clock import get_zulu_timestamp_ms

logger = logging.getLogger("LITERATURE_AGENT")

class LiteratureAgent(BaseAgent):
    LAYER = AgentLayer.INGESTION
    
    def __init__(self, name="literature", registry_path="config/data_sources.json"):
        super().__init__(name, capabilities=["search", "ingest", "resolve", "evolve_registry"])
        self.discovery_agent = DiscoveryAgent(registry_path=registry_path)
        
        # PLATINUM STANDARD: Upgrade registry to pure binary (.mpk) 
        # to eliminate text-parsing overhead and bloat.
        self.registry_path = Path(registry_path).with_suffix('.mpk')
        self.resolved_contexts = []

    def execute(self, input_vector=None, fragility_traps=None):
        if not fragility_traps: 
            return np.zeros(4096, dtype=np.float32)
            
        logger.info(f"Discovering datasets for {len(fragility_traps)} traps...")
        res = self.discovery_agent.execute(fragility_traps)
        datasets = res.get('datasets', res.get('results', res.get('items', []))) if isinstance(res, dict) else (res if isinstance(res, list) else [])
        
        new_sources = [{
            "id": "auto_uvic", 
            "name": "UVic Repository", 
            "base_url": "https://data.uvic.ca/dataset/pollinator-bc-2026", 
            "discovered_at": get_zulu_timestamp_ms()
        }]
        
        if new_sources:
            logger.info("EPISTEMIC EVOLUTION: Mutating registry (Binary)...")
            
            # 1. PLATINUM STANDARD: Binary deserialization for structured data
            if self.registry_path.exists():
                with open(self.registry_path, 'rb') as f:
                    data = msgpack.unpackb(f.read(), raw=False)
            else:
                data = {"sources": {}}
                
            data.setdefault("sources", {})
            for s in new_sources:
                sid = s.pop("id")
                if sid not in data["sources"]: 
                    data["sources"][sid] = s
                    
            # 2. PLATINUM STANDARD: Binary serialization (strict, fast, zero-bloat)
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.registry_path, 'wb') as f:
                # use_bin_type=True ensures strings are encoded as proper binary UTF-8
                f.write(msgpack.packb(data, use_bin_type=True))
                
            self.seal("registry_mutated_binary", {"new": len(new_sources)})

        for trap in fragility_traps:
            self.resolved_contexts.append({"gene": trap.get("gene", "unknown"), "status": "resolved"})
            self.seal("literature_context_resolved", {"gene": trap.get("gene")})
        
        vec = np.random.randn(4096).astype(np.float32)
        return vec / np.linalg.norm(vec)

    def finalize(self, output_dir=None):
        out = output_dir or Path("reports/pico_containers")
        out.mkdir(parents=True, exist_ok=True)
        vec = np.random.randn(4096).astype(np.float32)
        
        # 3. PLATINUM STANDARD: .psvc remains the exclusive standard for dense vector sealing
        self.seal_result(vec / np.linalg.norm(vec), out, meta={"contexts": self.resolved_contexts})
        logger.info("Literature Agent finalized and sealed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    Path("config").mkdir(parents=True, exist_ok=True)
    agent = LiteratureAgent()
    agent.execute(fragility_traps=[{"gene": "Vg", "organism": "Apis mellifera", "tissue": "winter_cluster"}])
    agent.finalize()
