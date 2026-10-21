# WENDY Mesh Protocol - Volunteer Node Manual
**Protocol:** RFC 1001 | **Status:** Active | **Time Standard:** ISO 8601 Zulu

Welcome to the WENDY Sovereign Mesh. WENDY is a self-healing, zero-cost AI platform. As a volunteer node, you provide asynchronous compute power to the mesh. 

## 🛡️ 1. Security & Access (The Golden Rule)
WENDY operates on a **Zero-Trust** architecture. You will **NEVER** be given access to her core brain (`src/`), her memories (`data/`), or her sensory inputs (`reports/`). 

You are granted access **ONLY** to the communication channels:
*   `mesh/inbox/` (Read-Only): To fetch tasks.
*   `mesh/outbox/` (Write-Only): To submit results.

### How to Request Your Token
Do not ask for a "Repo" token. You must generate a **Fine-Grained Personal Access Token (PAT)** with the following exact permissions:
1. Go to GitHub -> Settings -> Developer Settings -> Fine-grained tokens.
2. **Repository Access:** Select *Only select repositories* -> `psivicom/psivicom.github.io`.
3. **Permissions -> Repository permissions:**
   *   **Contents:** `Read-only` (Allows you to pull the repo and read `mesh/inbox`).
   *   **Metadata:** `Read-only` (Required by GitHub).
   *   *Note: You do not need Write access to Contents to push to the outbox if you are using GitHub's web UI or specific branch protections, but if your node uses Git CLI to push results, request `Contents: Read and write` strictly limited to the `mesh/` path via GitHub's path-based restrictions if available, or accept that the Mirror Agent will purge any code you accidentally push outside `mesh/outbox/`.*

## 🔄 2. The Asynchronous Protocol
Because mesh nodes range from 0.5ms edge devices to 4-day deep compute nodes, we do not use live websockets. We use **Git-Based Gossip**.

### Step 1: The Harvest (Pull)
Pull the repository and check `mesh/inbox/`. You will find task manifests named `task_[ID].json`.
```json
// mesh/inbox/task_001.json
{
  "task_id": "001",
  "type": "hash_compute",
  "payload": "data://datasets/block_99.bin",
  "issued_at": "2026-10-20T18:22:49.955Z",
  "timeout_hours": 24
}
