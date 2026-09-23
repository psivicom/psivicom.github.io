# src/agents/literature_agent.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

import logging
import time
from typing import Dict, Any, List
import numpy as np
import torch

from src.base.base_agent import BaseAgent, AgentLayer
from src.core.http_client import ProductionHTTPClient
from src.core.psvc_containers import build_psvc_from_tensor

logger = logging.getLogger(__name__)

class LiteratureAgent(BaseAgent):
    LAYER = AgentLayer.INGESTION

    def __init__(
        self,
        name: str = "literature_agent",
        semantic_scholar_timeout: float = 30.0,
        crossref_timeout: float = 30.0,
        rate_limit_per_second: float = 1.0
    ):
        super().__init__(name=name, capabilities=["search_papers", "fetch_citations", "fetch_references"])

        self.semantic_scholar = ProductionHTTPClient(
            base_url="https://api.semanticscholar.org/graph/v1",
            timeout=semantic_scholar_timeout,
            rate_limit_per_second=rate_limit_per_second,
            headers={"Accept": "application/json"}
        )

        self.crossref = ProductionHTTPClient(
            base_url="https://api.crossref.org",
            timeout=crossref_timeout,
            rate_limit_per_second=rate_limit_per_second,
            headers={"Accept": "application/json", "User-Agent": "PSIVI/1.0 (mailto:contact@psivicom.com)"}
        )
        logger.info(f"LiteratureAgent initialized: {self.agent_id}")

    def search_papers(self, query: str, limit: int = 10, fields: str = "title,abstract,year,citationCount,authors") -> Dict[str, Any]:
        params = {"query": query, "limit": min(limit, 100), "fields": fields}
        data = self.semantic_scholar.get("paper/search", params=params)
        if "data" not in data:
            raise ValueError(f"Invalid Semantic Scholar response: {data}")
        return {"query": query, "total": data.get("total", 0), "papers": data["data"], "fetched_at": time.time()}

    def fetch_paper_details(self, paper_id: str) -> Dict[str, Any]:
        params = {"fields": "title,abstract,year,citationCount,referenceCount,authors,citations,references"}
        data = self.semantic_scholar.get(f"paper/{paper_id}", params=params)
        if "paperId" not in data:
            raise ValueError(f"Invalid paper response: {data}")
        return {"paper": data, "fetched_at": time.time()}

    def search_crossref(self, query: str, limit: int = 10) -> Dict[str, Any]:
        params = {"query": query, "rows": min(limit, 100), "select": "DOI,title,author,published-print,abstract,is-referenced-by-count"}
        data = self.crossref.get("works", params=params)
        if "message" not in data or "items" not in data["message"]:
            raise ValueError(f"Invalid CrossRef response: {data}")
        return {"query": query, "total": data["message"].get("total-results", 0), "papers": data["message"]["items"], "fetched_at": time.time()}

    def embed_papers(self, papers_data: Dict[str, Any]) -> torch.Tensor:
        papers = papers_data.get("papers", [])
        if not papers:
            return torch.zeros(10, dtype=torch.float32)
        features = []
        for paper in papers:
            features.append([
                paper.get("citationCount", 0) or 0,
                paper.get("year", 2000) or 2000,
                paper.get("referenceCount", 0) or 0,
                len(paper.get("abstract", "") or "")
            ])
        features_array = np.array(features, dtype=np.float32)
        features_array = (features_array - features_array.mean(axis=0)) / (features_array.std(axis=0) + 1e-8)
        return torch.tensor(features_array.flatten(), dtype=torch.float32)

    def execute(self, query: str, limit: int = 10) -> bytes:
        papers_data = self.search_papers(query, limit)
        vector = self.embed_papers(papers_data)
        receipt = self.seal(operation="search_and_embed_papers", payload={"query": query, "limit": limit})
        container = build_psvc_from_tensor(
            tensor=vector, operation="literature_embedding", agent_id=self.agent_id,
            layer=self.LAYER.name, parent_receipt_hash=receipt.payload_hash, content_type="literature_vector"
        )
        from src.core.psvc_containers import serialize_psvc
        return serialize_psvc(container)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = LiteratureAgent()
    print("\n=== Searching Real Academic Papers ===")
    container_bytes = agent.execute(query="climate change impact agriculture", limit=10)
    print(f"✓ Container created: {len(container_bytes)} bytes")
    
    from src.core.psvc_containers import deserialize_psvc, verify_container
    container = deserialize_psvc(container_bytes)
    print(f"✓ Verification: {verify_container(container)}")
    print(f"✓ Agent: {container.receipt.agent_id}")
    print(f"✓ Tensor shape: {container.payload.tensor_shape}")
