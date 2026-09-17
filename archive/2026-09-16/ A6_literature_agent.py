# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# literature_agent.py - Ingests scientific literature as pico vectors via free APIs.

import os
import json
import struct
import zlib
import hashlib
import datetime
import numpy as np
import requests
import xml.etree.ElementTree as ET
from pathlib import Path

CONTAINER_DIR = Path("reports/pico_containers")
MAGIC = b'PSVI'
DIM = 4096

def encode_text(text, dim=DIM):
    """Hashing trick to create a 4096-dim vector from text."""
    vec = np.zeros(dim, dtype=np.float32)
    text = text.lower().strip()
    for i in range(max(1, len(text) - 2)):
        trigram = text[i:i+3]
        h = int(hashlib.md5(trigram.encode()).hexdigest(), 16)
        idx = h % dim
        sign = 1 if (h % 2) == 0 else -1
        vec[idx] += sign
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec

def seal_container(vector, container_id, precision="int8"):
    """Compress and seal vector into a .psvc binary file."""
    vec = vector.astype(np.float32)
    scale = np.max(np.abs(vec)) / 127.0
    if scale == 0: scale = 1.0
    compressed = np.round(vec / scale).astype(np.int8).tobytes()
    payload = struct.pack('f', scale) + compressed
    zlibbed = zlib.compress(payload, level=9)
    
    header = MAGIC + struct.pack('B', 1) + struct.pack('B', 0) # Magic, v1, int8
    header += struct.pack('I', DIM) + struct.pack('I', len(zlibbed))
    
    path = CONTAINER_DIR / f"{container_id}.psvc"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(header + zlibbed)
    return path

def get_pubmed_abstracts(query="Bombus+terrestris+foraging", max_results=5):
    """Fetch recent pollinator ecology papers from PubMed (free API)."""
    abstracts = []
    
    try:
        # Search for papers
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmax={max_results}&retmode=json"
        search_resp = requests.get(search_url, timeout=10)
        ids = search_resp.json()['esearchresult']['idlist']
        
        print(f"[LITERATURE] Found {len(ids)} papers for query: {query}")
        
        # Fetch each abstract
        for pmid in ids:
            fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
            fetch_resp = requests.get(fetch_url, timeout=10)
            root = ET.fromstring(fetch_resp.text)
            
            title_elem = root.find('.//ArticleTitle')
            abstract_elem = root.find('.//AbstractText')
            
            if title_elem is not None and abstract_elem is not None:
                title = title_elem.text or ""
                abstract = abstract_elem.text or ""
                
                abstracts.append({
                    "pmid": pmid,
                    "title": title,
                    "abstract": abstract,
                    "source": "pubmed",
                    "text": f"{title}. {abstract}"
                })
    except Exception as e:
        print(f"[LITERATURE] PubMed API error: {e}")
    
    return abstracts

def get_crossref_metadata(query="pollinator foraging ecology", max_results=5):
    """Fetch papers from Crossref API (free, no auth needed)."""
    papers = []
    
    try:
        url = f"https://api.crossref.org/works?query={query}&rows={max_results}"
        resp = requests.get(url, timeout=10, headers={'User-Agent': 'PSIVI-Mesh/1.0 (psivi.com)'})
        data = resp.json()
        
        for item in data.get('message', {}).get('items', []):
            title = item.get('title', [''])[0] if item.get('title') else ""
            abstract = item.get('abstract', '')
            doi = item.get('DOI', '')
            
            if title or abstract:
                papers.append({
                    "doi": doi,
                    "title": title,
                    "abstract": abstract,
                    "source": "crossref",
                    "text": f"{title}. {abstract}"
                })
    except Exception as e:
        print(f"[LITERATURE] Crossref API error: {e}")
    
    return papers

print("=== PSIVI LITERATURE AGENT: INGESTING SCIENTIFIC CONTEXT ===")
CONTAINER_DIR.mkdir(parents=True, exist_ok=True)

# 1. Fetch from PubMed (biomedical/life sciences focus)
pubmed_papers = get_pubmed_abstracts(query="Bombus+foraging+temperature", max_results=5)

# 2. Fetch from Crossref (broader academic coverage)
crossref_papers = get_crossref_metadata(query="pollinator+ecology+climate", max_results=5)

# 3. Combine and deduplicate
all_papers = pubmed_papers + crossref_papers
seen_texts = set()
unique_papers = []

for paper in all_papers:
    text = paper.get("text", "")
    if text and text not in seen_texts and len(text) > 50:
        seen_texts.add(text)
        unique_papers.append(paper)

print(f"[LITERATURE] Ingesting {len(unique_papers)} unique papers into mesh.")

# 4. Encode each paper as a pico vector and seal
sealed_count = 0
for paper in unique_papers:
    text =
