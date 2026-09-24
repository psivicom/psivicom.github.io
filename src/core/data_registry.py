# src/core/data_registry.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# Intelligent Data Source Registry for Automated Dataset Discovery

import json
from pathlib import Path
from typing import Dict, List, Any

class DataRegistry:
    """
    Registry of known scientific data sources with API endpoints and query schemas.
    Enables intelligent dataset discovery based on OSDR/Pollinator ground truth fields.
    """
    
    def __init__(self, config_path: str = "config/data_sources.json"):
        self.config_path = Path(config_path)
        self.sources: Dict[str, Dict] = self._load_sources()
    
    def _load_sources(self) -> Dict[str, Dict]:
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        return self._get_default_sources()
    
    def _get_default_sources(self) -> Dict[str, Dict]:
        return {
            "osdr": {
                "name": "NASA Open Science Data Repository",
                "base_url": "https://opensciencedatacloud.org/api",
                "query_params": ["gene", "organism", "tissue", "study"],
                "auth_required": False,
                "format": "json"
            },
            "nasa_earthdata": {
                "name": "NASA Earthdata Search",
                "base_url": "https://cmr.earthdata.nasa.gov/search",
                "query_params": ["keyword", "polygon", "temporal"],
                "auth_required": True,
                "format": "json"
            },
            "zenodo": {
                "name": "Zenodo Open Research",
                "base_url": "https://zenodo.org/api/records",
                "query_params": ["query", "keywords"],
                "auth_required": False,
                "format": "json"
            },
            "gbif": {
                "name": "Global Biodiversity Information Facility",
                "base_url": "https://api.gbif.org/v1/occurrence",
                "query_params": ["species", "decimalLatitude", "decimalLongitude", "year"],
                "auth_required": False,
                "format": "json"
            }
        }
    
    def get_source(self, source_id: str) -> Dict:
        return self.sources.get(source_id, {})
    
    def get_relevant_sources(self, context: Dict[str, Any]) -> List[str]:
        """
        Intelligently selects data sources based on the scientific context.
        """
        relevant = []
        organism = context.get("organism", "").lower()
        tissue = context.get("tissue", "").lower()
        
        if "homo_sapiens" in organism or "mus_musculus" in organism or "drosophila" in organism:
            relevant.append("osdr")
            relevant.append("zenodo")
        
        if "arabidopsis" in organism:
            relevant.append("osdr")
            relevant.append("zenodo")
        
        if "apis" in organism or "bombus" in organism or "pollinator" in tissue:
            relevant.append("gbif")
            relevant.append("zenodo")
        
        if "radarsat" in context.get("keyword", "").lower() or "earthdata" in context.get("keyword", "").lower():
            relevant.append("nasa_earthdata")
            
        return relevant
    
    def construct_query(self, source_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constructs API-specific query parameters based on OSDR ground truth fields.
        """
        source = self.get_source(source_id)
        if not source:
            return {}
        
        query = {}
        if source_id == "osdr":
            query["gene"] = context.get("gene", "")
            query["organism"] = context.get("organism", "")
            query["tissue"] = context.get("tissue", "")
        elif source_id == "gbif":
            query["species"] = context.get("organism", "")
            query["hasCoordinate"] = True
        elif source_id == "zenodo":
            query["q"] = f"{context.get('gene', '')} {context.get('organism', '')} spaceflight"
        elif source_id == "nasa_earthdata":
            query["keyword"] = context.get("keyword", "Goldstream")
            
        return query
