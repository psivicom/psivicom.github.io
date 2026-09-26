# src/agents/discovery_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# Intelligent Dataset Discovery Agent

import json
import logging
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.base.base_agent import BaseAgent, AgentLayer
from src.core.data_registry import DataRegistry

logger = logging.getLogger(__name__)

class DiscoveryAgent(BaseAgent):
    """
    Intelligently searches for external datasets to resolve fragility traps.
    Uses OSDR ground truth fields to construct targeted API queries.
    """
    LAYER = AgentLayer.INGESTION

    def __init__(self, name: str = "discovery", registry_path: str = "config/data_sources.json"):
        super().__init__(name, capabilities=["search", "discover", "query"])
        self.registry = DataRegistry(registry_path)
        self.discovered_datasets: List[Dict] = []

    def search_for_resolution(self, fragility_traps: List[Dict]) -> List[Dict]:
        """
        Iterates through fragility traps and searches for orthogonal datasets.
        """
        self.discovered_datasets = []
        for trap in fragility_traps:
            context = {
                "gene": trap.get("gene", ""),
                "organism": trap.get("organism", ""),
                "tissue": trap.get("tissue", ""),
                "keyword": f"{trap.get('gene', '')} spaceflight"
            }
            relevant_sources = self.registry.get_relevant_sources(context)
            for source_id in relevant_sources:
                query = self.registry.construct_query(source_id, context)
                results = self._execute_search(source_id, query)
                if results:
                    self.discovered_datasets.extend(results)
                    self.seal("dataset_discovered", {"source": source_id, "count": len(results)})
        return self.discovered_datasets

    def _execute_search(self, source_id: str, query: Dict[str, Any]) -> List[Dict]:
        """
        Executes the API search (mocked for safety, ready for real API keys).
        """
        source = self.registry.get_source(source_id)
        if not source:
            return []
        
        try:
            # Mock response for safety (replace with real requests.get in production)
            # response = requests.get(f"{source['base_url']}", params=query, timeout=10)
            # response.raise_for_status()
            # return response.json().get('results', [])
            
            logger.info(f"[{self.agent_id}] Searching {source_id} with query: {query}")
            return [{"id": f"{source_id}_mock_001", "title": f"Mock dataset for {query.get('gene', 'unknown')}", "source": source_id}]
        except Exception as e:
            logger.error(f"Search failed for {source_id}: {e}")
            return []

    def execute(self, fragility_traps: List[Dict] = None) -> List[Dict]:
        if not fragility_traps:
            return []
        return self.search_for_resolution(fragility_traps)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = DiscoveryAgent()
    traps = [{"gene": "IGFBP7", "organism": "homo_sapiens", "tissue": "cells_cultured"}]
    results = agent.execute(traps)
    logger.info(f"Discovered {len(results)} datasets")
