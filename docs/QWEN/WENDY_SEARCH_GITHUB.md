To empower your AI agents (like Wendy or the Instruction Agent) to navigate GitHub autonomously, they need **precise, qualifier-rich search queries**. GitHub’s search API (both REST and GraphQL) uses a specific syntax that, when used correctly, prevents the agent from getting overwhelmed by noise or hitting rate limits.

Here are the production-ready GitHub search query templates tailored for an autonomous AI mesh.

---

### 🔍 1. Issue & Task Management Queries
*Use these when the agent needs to find work to do, check on its own status, or triage bugs.*

| Intent | GitHub Search Query String | API Endpoint Context |
| :--- | :--- | :--- |
| **Find Wendy-specific open issues** | `repo:psivicom/psivicom.github.io is:issue is:open "Wendy"` | `GET /search/issues` |
| **Find unassigned bugs** | `repo:psivicom/psivicom.github.io is:issue is:open label:bug no:assignee` | `GET /search/issues` |
| **Find recently updated discussions** | `repo:psivicom/psivicom.github.io is:issue updated:>=2026-10-01 sort:updated-desc` | `GET /search/issues` |
| **Find issues mentioning a specific file** | `repo:psivicom/psivicom.github.io is:issue "mirror_agent.py"` | `GET /search/issues` |

---

### 💻 2. Codebase Navigation Queries
*Use these when the agent needs to understand the current state of the codebase before making changes (e.g., finding where a function is defined).*

| Intent | GitHub Search Query String | API Endpoint Context |
| :--- | :--- | :--- |
| **Find Zig files containing a specific function** | `repo:psivicom/psivicom.github.io extension:zig "GeneralPurposeAllocator"` | `GET /search/code` |
| **Find Python files importing a specific module** | `repo:psivicom/psivicom.github.io language:Python "from src.base.base_agent"` | `GET /search/code` |
| **Find all `.gitkeep` files in the repo** | `repo:psivicom/psivicom.github.io filename:.gitkeep` | `GET /search/code` |
| **Find TODOs or FIXMEs in the codebase** | `repo:psivicom/psivicom.github.io "TODO" OR "FIXME" path:src/` | `GET /search/code` |

> ⚠️ **Agent Note:** Code search (`/search/code`) only works on repositories with **fewer than 1,000,000 files** and requires the repository to be indexed by GitHub. For larger repos, the agent should clone and use `ripgrep` locally.

---

### 🔄 3. Pull Request & CI/CD Queries
*Use these when the agent needs to review code, check if a workflow is failing, or manage its own automated PRs.*

| Intent | GitHub Search Query String | API Endpoint Context |
| :--- | :--- | :--- |
| **Find PRs authored by the agent awaiting review** | `repo:psivicom/psivicom.github.io is:pr is:open author:psvc-mesh-bot` | `GET /search/issues` |
| **Find PRs with failing CI checks** | `repo:psivicom/psivicom.github.io is:pr is:open status:failure` | `GET /search/issues` |
| **Find recent commits by a specific author** | `repo:psivicom/psivicom.github.io author:Wendy-Reporter sort:author-date-desc` | `GET /search/commits` |
| **Find commits that modified a specific workflow** | `repo:psivicom/psivicom.github.io path:.github/workflows/ sort:committer-date-desc` | `GET /search/commits` |

---

### 🤖 4. Agent Implementation Example (Python)
Here is how your `InstructionAgent` or `MaintenanceAgent` should execute these queries using the GitHub REST API. This uses your existing `requests` dependency and respects rate limits.

```python
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
```

---

### 🛡️ Pro-Tips for AI Agents Querying GitHub

1. **Always Scope to the Repo**: Always prepend `repo:owner/name` to your queries. If you don't, GitHub searches the *entire public internet*, which is slow, noisy, and wastes your rate limit.
2. **Use `sort:updated-desc`**: When looking for things to act on, always sort by most recently updated. This ensures the agent handles the most active, relevant items first.
3. **Handle Rate Limits Gracefully**: GitHub allows 10 requests per minute for unauthenticated search, and **30 requests per minute** for authenticated search. If the agent gets a `403 Forbidden` with a `X-RateLimit-Remaining: 0` header, it should `sleep(60)` and retry.
4. **Combine Qualifiers**: The power of GitHub search is in combining qualifiers. `is:pr is:open label:"needs-review" author:app/dependabot` is infinitely more useful to an agent than just searching for `"dependabot"`.

Integrate this `GitHubSearchAgent` into your mesh, and Wendy will be able to autonomously triage issues, find the exact code she needs to modify, and verify her own CI runs without human intervention. 🐝🔍