# src/agents/literature_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Literature Context Agent: Ingestion & Epistemic Evolution Layer
Resolves scientific context, queries literature, and dynamically 
mutates the DataRegistry when new scientific repositories or datasets 
are discovered in recent publications.
"""

import logging
import json
import re
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

from src.base.base_agent import BaseAgent, AgentLayer
from src.agents.discovery_agent import DiscoveryAgent
from src.core.psvc_reference import write_file, content_hash, PRECISION_FLOAT32
from src.core.zulu_clock import get_zulu_timestamp_ms

logger = logging.getLogger("LITERATURE_AGENT")

class LiteratureAgent(BaseAgent):
    LAYER = AgentLayer.INGESTION

    def __init__(self, name: str = "literature", registry_path: str = "config/data_sources.json"):
        super().__init__(name, capabilities=["search", "ingest", "resolve", "evolve_registry"])
        self.discovery_agent = DiscoveryAgent(registry_path=registry_path)
        self.registry_path = Path(registry_path)
        self.resolved_contexts: List[Dict] = []

    def _extract_new_data_sources(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        EPISTEMIC EVOLUTION: Scans abstracts and metadata for new repository URLs 
        or dataset mentions, and prepares them for registry mutation.
        """
        new_sources = []
        # Regex to find common data repository patterns in text
        url_pattern = re.compile(r'(https?://[^\s<>"]+|www\.[^\s<>"]+)')
        
        for paper in papers:
            text_to_scan = f"{paper.get('title', '')} {paper.get('abstract', '')}"
            found_urls = url_pattern.findall(text_to_scan)
            
            for url in found_urls:
                # Filter for likely data repositories (not just generic homepages)
                if any(keyword in url.lower() for keyword in ['data', 'dataset', 'zenodo', 'figshare', 'github', 'repository', 'archive', 'uvic', 'ubc']):
                    source_name = url.split('//')[1].split('/')[0].replace('www.', '').split('.')[0].title()
                    new_sources.append({
                        "id": f"auto_discovered_{source_name.lower()}",
                        "name": f"{source_name} Repository",
                        "base_url": url,
                        "discovery_context": paper.get("title"),
                        "discovered_at": get_zulu_timestamp_ms()
                    })
                    
        # Deduplicate
        return [dict(t) for t in {tuple(d.items()) for d in new_sources}]

    def _mutate_registry(self, new_sources: List[Dict[str, Any]]) -> bool:
        """Dynamically updates the config/data_sources.json with newly discovered repositories."""
        if not new_sources:
            return False
            
        logger.info(f"🧬 EPISTEMIC EVOLUTION: Mutating registry with {len(new_sources)} new data sources...")
        
        try:
            # Load existing registry
            if self.registry_path.exists():
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    registry_data = json.load(f)
            else:
                registry_data = {"sources": {}}
                
            # Ensure 'sources' dict exists
            if "sources" not in registry_data:
                registry_data["sources"] = {}
                
            # Append new sources
            for source in new_sources:
                source_id = source.pop("id")
                if source_id not in registry_data["sources"]:
                    registry_data["sources"][source_id] = source
                    logger.info(f"  + Added: {source['name']} ({source['base_url']})")
                    
            # Write back to file
            write_file(self.registry_path, registry_data)
            self.seal("registry_mutated", {"new_sources_added": len(new_sources)})
            return True
            
        except Exception as e:
            logger.error(f"❌ Registry mutation failed: {e}")
            return False

    def execute(self, input_vector: np.ndarray = None, fragility_traps: List[Dict] = None) -> np.ndarray:
        if not fragility_traps:
            logger.info("No fragility traps provided. Returning zero vector.")
            return np.zeros(4096, dtype=np.float32)
        
        logger.info(f"🔍 Discovering datasets and scanning literature for {len(fragility_traps)} traps...")
        
        # 1. Standard Discovery
        discovered_datasets = self.discovery_agent.execute(fragility_traps)
        
        # 2. Simulate Literature Query (In production, this hits Semantic Scholar/Crossref)
        # For this example, we simulate a paper that mentions a new UVic dataset
        simulated_papers = [
            {
                "title": "Novel Pollinator Forage Dynamics in the Capital Regional District",
                "abstract": "Data supporting this study is available at the new UVic Open Science Data repository: https://data.uvic.ca/dataset/pollinator-bc-2026",
                "year": 2026
            }
        ]
        
        # 3. EPISTEMIC EVOLUTION: Extract and mutate
        new_sources = self._extract_new_data_sources(simulated_papers)
        if new_sources:
            self._mutate_registry(new_sources)
            # Trigger a re-scan with the newly evolved registry!
            logger.info("🔄 Re-executing discovery with newly evolved registry...")
            discovered_datasets.extend(self.discovery_agent.execute(fragility_traps))
        
        # 4. Seal Context
        for trap in fragility_traps:
            context = {
                "gene": trap.get("gene", "unknown"),
                "organism": trap.get("organism", "unknown"),
                "datasets_found": len(discovered_datasets),
                "new_sources_discovered": len(new_sources),
                "resolution_status": "resolved" if discovered_datasets else "unresolved"
            }
            self.resolved_contexts.append(context)
            self.seal("literature_context_resolved", context)
        
        # 5. Generate normalized float32 vector for mesh routing
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
        logger.info("✅ Literature Agent finalized and sealed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    # Ensure config dir exists for the registry
    Path("config").mkdir(parents=True, exist_ok=True)
    
    agent = LiteratureAgent()
    traps = [{"gene": "Vg", "organism": "Apis mellifera", "tissue": "winter_cluster"}]
    
    agent.execute(fragility_traps=traps)
    agent.finalize()
    logger.info("Literature Agent execution complete. Check config/data_sources.json for evolution.")
