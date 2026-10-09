# src/agents/discovery_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Planetary Comparative Discovery Agent: Ingestion Layer
Intelligently searches for external datasets to resolve fragility traps.
Uses a DataRegistry for FAIR-compliant source management, augmented with
real API integrations for BC Open Data, NASA/ESA Earth Observation (CNES/RADARSAT),
GBIF, and a Lateral Discovery Engine for unexpected scientific correlations.
"""

import json
import logging
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.base.base_agent import BaseAgent, AgentLayer
from src.core.data_registry import DataRegistry

logger = logging.getLogger("DISCOVERY_AGENT")

class DiscoveryAgent(BaseAgent):
    """
    Intelligently searches for external datasets to resolve fragility traps.
    Uses OSDR ground truth fields to construct targeted API queries across 
    local (BC), global (GBIF), and space-tech (CNES/RADARSAT) repositories.
    """
    LAYER = AgentLayer.INGESTION

    # Goldstream Watershed, Langford, BC Bounding Box for Space Tech queries
    BBOX = "-123.7017,48.3456,-123.3017,48.5456"

    def __init__(self, name: str = "discovery", registry_path: str = "config/data_sources.json"):
        super().__init__(name, capabilities=[
            "search", "discover", "query_bc_catalogue", "query_earth_observation", "lateral_discovery"
        ])
        self.registry = DataRegistry(registry_path)
        self.discovered_datasets: List[Dict] = []
        self.unexpected_discoveries: List[Dict] = []

    def search_for_resolution(self, fragility_traps: List[Dict]) -> List[Dict]:
        """
        Iterates through fragility traps and searches for orthogonal datasets.
        """
        self.discovered_datasets = []
        for trap in fragility_traps:
            organism = trap.get("organism", "Apis mellifera")
            gene = trap.get("gene", "")
            tissue = trap.get("tissue", "")
            
            # Enrich context for planetary comparative climatology
            context = {
                "gene": gene,
                "organism": organism,
                "tissue": tissue,
                "location": "Goldstream, Langford, BC, Canada",
                "keyword": f"{organism} {gene} pollinator wintering climate change"
            }
            
            relevant_sources = self.registry.get_relevant_sources(context)
            
            for source_id in relevant_sources:
                query = self.registry.construct_query(source_id, context)
                results = self._execute_search(source_id, query, context)
                if results:
                    self.discovered_datasets.extend(results)
                    self.seal("dataset_discovered", {"source": source_id, "count": len(results)})
                    
        return self.discovered_datasets

    def _execute_search(self, source_id: str, query: Dict[str, Any], context: Dict[str, Any]) -> List[Dict]:
        """
        Executes real API searches for key scientific repositories.
        Falls back to registry mock if source is not natively implemented yet.
        """
        try:
            if source_id == "bc_catalogue":
                return self._query_bc_catalogue(context["keyword"])
            elif source_id in ["nasa_cmr", "cnes_radarsat"]:
                return self._query_earth_observation(context["organism"])
            elif source_id == "gbif":
                return self._query_gbif(context["organism"])
            else:
                # Fallback to registry-defined mock/endpoint
                source = self.registry.get_source(source_id)
                logger.info(f"[{self.name}] Searching {source_id} with query: {query}")
                return [{"id": f"{source_id}_mock_001", "title": f"Registry dataset for {context.get('organism')}", "source": source_id}]
                
        except Exception as e:
            logger.error(f"Search failed for {source_id}: {e}")
            return []

    def _query_bc_catalogue(self, keyword: str) -> List[Dict]:
        """Real API: Government of BC Open Data Catalogue."""
        url = "https://catalogue.data.gov.bc.ca/api/3/action/package_search"
        params = {"q": f"{keyword} (Langford OR CRD OR 'Capital Regional District')", "rows": 3}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [
            {"source": "BC Data Catalogue", "title": r.get("title"), 
             "url": f"https://catalogue.data.gov.bc.ca/dataset/{r.get('id')}"}
            for r in data.get("result", {}).get("results", [])
        ]

    def _query_earth_observation(self, organism: str) -> List[Dict]:
        """Real API: NASA CMR (includes French CNES/Theia & Canadian RADARSAT)."""
        url = "https://cmr.earthdata.nasa.gov/search/granules.json"
        params = {
            "keyword": f"CNES OR Pleiades OR RADARSAT OR Sentinel-2 {organism} land cover",
            "bounding_box": self.BBOX,
            "page_size": 3
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [
            {"source": "Space Tech (CNES/RADARSAT/ESA)", "title": item.get("title"), 
             "description": "Satellite observation for soil moisture, vegetation, and land use.",
             "url": item.get("links", [{}])[0].get("href", "") if item.get("links") else ""}
            for item in data.get("feed", {}).get("entry", [])
        ]

    def _query_gbif(self, organism: str) -> List[Dict]:
        """Real API: Global Biodiversity Information Facility (Canada filtered)."""
        url = "https://api.gbif.org/v1/occurrence/search"
        params = {"scientificName": organism, "country": "CA", "hasCoordinate": "true", "limit": 3}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [
            {"source": "GBIF", "title": f"Occurrence: {hit.get('species', organism)}", 
             "location": f"{hit.get('province', 'BC')}, Canada",
             "url": f"https://www.gbif.org/occurrence/{hit.get('key')}"}
            for hit in data.get("results", [])
        ]

    def _lateral_discovery(self, organism: str) -> List[Dict]:
        """
        THE LATERAL DISCOVERY ENGINE: 
        Generates unexpected queries based on regional stressors to find novel correlations.
        """
        logger.info(f"🧠 Activating Lateral Discovery Engine for unexpected correlations...")
        lateral_map = {
            "Apis mellifera": [
                "wildfire smoke impact pollinators BC",
                "urban heat island Langford BC",
                "neonicotinoid runoff Capital Regional District",
                "BC Hydro transmission line interference bees"
            ]
        }
        
        queries = lateral_map.get(organism, [f"{organism} unexpected mortality BC"])
        discoveries = []
        
        for q in queries:
            # Leverage the BC Catalogue for lateral queries
            try:
                url = "https://catalogue.data.gov.bc.ca/api/3/action/package_search"
                response = requests.get(url, params={"q": q, "rows": 1}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for r in data.get("result", {}).get("results", []):
                        discoveries.append({
                            "source": "Lateral Discovery (BC Catalogue)",
                            "title": f"Unexpected Correlation: {r.get('title')}",
                            "hypothesis": f"Cross-stressor analysis: {q}"
                        })
            except Exception:
                pass # Fail silently on lateral, it's a bonus discovery
                
        return discoveries

    def execute(self, fragility_traps: List[Dict] = None) -> Dict[str, Any]:
        """Main execution: Resolves traps and seeks unexpected discoveries."""
        if not fragility_traps:
            return {"standard_datasets": [], "unexpected_discoveries": []}
            
        standard_results = self.search_for_resolution(fragility_traps)
        
        # Trigger lateral discovery for the primary organism
        organism = fragility_traps[0].get("organism", "Apis mellifera")
        unexpected_results = self._lateral_discovery(organism)
        self.unexpected_discoveries = unexpected_results
        
        self.seal("planetary_discovery_complete", {
            "standard_count": len(standard_results),
            "unexpected_count": len(unexpected_results)
        })
        
        return {
            "standard_datasets": standard_results,
            "unexpected_discoveries": unexpected_results
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    agent = DiscoveryAgent()
    traps = [{"gene": "Vg", "organism": "Apis mellifera", "tissue": "winter_cluster"}]
    results = agent.execute(traps)
    
    print(f"\n🌍 STANDARD DISCOVERIES ({len(results['standard_datasets'])}):")
    for r in results['standard_datasets'][:3]:
        print(f"  - [{r['source']}] {r['title']}")
        
    print(f"\n🧠 UNEXPECTED DISCOVERIES ({len(results['unexpected_discoveries'])}):")
    for r in results['unexpected_discoveries'][:2]:
        print(f"  - [{r['source']}] {r['title']}")
