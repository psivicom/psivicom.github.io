# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# Author: Louis-Philippe Audette
# ORCID: https://orcid.org/0000-000X-XXXX-XXXX
#
# Literature Agent (Scholar) - RFC 1001 Compliant

import os
import json
import datetime
import numpy as np
import requests
import xml.etree.ElementTree as ET
from pathlib import Path

from psvc_reference import (
    encode_text, write_file, content_hash,
    PRECISION_INT8
)

print("=== PSIVI LITERATURE AGENT (RFC 1001 COMPLIANT) ===")

CONTAINER_DIR = Path("reports/pico_containers")
CONTAINER_DIR.mkdir(parents=True, exist_ok=True)

def get_pubmed_abstracts(query="Bombus+terrestris+foraging", max_results=5):
    """Fetch papers from PubMed (free API)."""
    abstracts = []
    try:
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmax={max_results}&retmode=json"
        search_resp = requests.get(search_url, timeout=10)
        ids = search_resp.json()['esearchresult']['idlist']
        
        for pmid in ids:
            fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
            fetch_resp = requests.get(fetch_url, timeout=10)
            root = ET.fromstring(fetch_resp.text)
            
            title_elem = root.find('.//ArticleTitle')
            abstract_elem = root.find('.//AbstractText')
            
            if title_elem is not None and abstract_elem is not None:
                abstracts.append({
                    "pmid": pmid,
                    "title": title_elem.text or "",
                    "abstract": abstract_elem.text or "",
                    "source": "pubmed"
                })
    except Exception as e:
        print(f"[LITERATURE] PubMed error: {e}")
    
    return abstracts

def get_crossref_papers(query="pollinator+ecology", max_results=5):
    """Fetch papers from Crossref (free API)."""
    papers = []
    try:
        url = f"https://api.crossref.org/works?query={query}&rows={max_results}"
        resp = requests.get(url, timeout=10, headers={'User-Agent': 'PSIVI/1.0'})
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
                    "source": "crossref"
                })
    except Exception as e:
        print(f"[LITERATURE] Crossref error: {e}")
    
    return papers

# 1. FETCH PAPERS
pubmed_papers = get_pubmed_abstracts(max_results=5)
crossref_papers = get_crossref_papers(max_results=5)

all_papers = pubmed_papers + crossref_papers

# 2. DEDUPLICATE
seen = set()
unique_papers = []
for paper in all_papers:
    text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
    if text not in seen and len(text) > 50:
        seen.add(text)
        unique_papers.append(paper)

print(f"[LITERATURE] Ingesting {len(unique_papers)} unique papers.")

# 3. ENCODE AND SEAL USING CANONICAL LIBRARY
sealed_count = 0
for paper in unique_papers:
    text = f"{paper.get('title', '')}. {paper.get('abstract', '')}"
    vector = encode_text(text)
    
    chash = content_hash(vector)
    output_path = CONTAINER_DIR / f"lit_{chash}.psvc"
    
    write_file(vector, output_path, precision=PRECISION_INT8)
    
    # Write sidecar
    sidecar_path = output_path.with_suffix('.json')
    with open(sidecar_path, 'w') as f:
        json.dump({
            "text": text,
            "agent": "literature",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "type": "literature",
            "source": paper.get("source"),
            "pmid": paper.get("pmid"),
            "doi": paper.get("doi"),
            "title": paper.get("title")
        }, f, indent=2)
    
    sealed_count += 1

print(f"[LITERATURE] Sealed {sealed_count} literature vectors.")
