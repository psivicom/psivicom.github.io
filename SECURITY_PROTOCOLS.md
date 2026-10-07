# 🛡️ WENDY SECURITY & ESCALATION PROTOCOLS

**SPDX-License-Identifier:** EUPL-1.2  
**SPDX-FileCopyrightText:** 2026 Louis-Philippe Audette | PSIVI.COM

## 1. SHA Resolution Protocol (How to pin new actions)
When you are instructed to create a new workflow that requires a GitHub Action you have not used before, you **MUST** resolve the mutable tag (e.g., `@v4`) to its immutable 40-character SHA.

**Execution Steps:**
1. Query the GitHub API for the action's repository to find the commit SHA associated with the requested tag.
   ```bash
   curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/repos/actions/checkout/commits/v4 | jq -r '.sha'
