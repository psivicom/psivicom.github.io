# src/tools/github_search.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import os
import requests
from typing import List, Dict, Any

class GitHubSearchAgent:
    def __init__(self, token: str, repo: str = "psivicom/psivicom.github.io"):
        self.token = token
        self.repo = repo
        self.base_url = "https://api.github.com/search"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "PSIVI-Wendy-Mesh/1.0"
        }

    def search_issues(self, query: str, sort: str = "updated", order: str = "desc") -> List[Dict[str, Any]]:
        """Search for issues/PRs using GitHub's advanced search syntax."""
        # Automatically scope to the current repo if not specified in the query
        if "repo:" not in query:
            query = f"repo:{self.repo} {query}"
            
        url = f"{self.base_url}/issues?q={requests.utils.quote(query)}&sort={sort}&order={order}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        return data.get("items", [])

    def search_code(self, query: str) -> List[Dict[str, Any]]:
        """Search for code snippets. Note: Requires repo to be <1M files and indexed."""
        if "repo:" not in query:
            query = f"repo:{self.repo} {query}"
            
        url = f"{self.base_url}/code?q={requests.utils.quote(query)}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        return response.json().get("items", [])

# --- Example Usage by Wendy ---
if __name__ == "__main__":
    gh_token = os.environ.get("GITHUB_TOKEN")
    searcher = GitHubSearchAgent(token=gh_token)
    
    # Find all open issues mentioning "Wendy"
    wendy_issues = searcher.search_issues('is:issue is:open "Wendy"')
    print(f"Found {len(wendy_issues)} open Wendy issues.")
    
    # Find all Zig files using GeneralPurposeAllocator
    zig_allocators = searcher.search_code('extension:zig "GeneralPurposeAllocator"')
    print(f"Found {len(zig_allocators)} Zig files with GeneralPurposeAllocator.")
