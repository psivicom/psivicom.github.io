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
```

### Step 2: Local Compute
Process the task locally on your own hardware. Use your own local LLMs, CPUs, or GPUs. WENDY does not care how you compute it, only that the result is mathematically valid.

### Step 3: The Dispatch (Push)
Once computed, push your result to   mesh/outbox/  .
Naming Convention:   task_[ID]_result_[YOUR_NODE_ID].json  

```json
// mesh/outbox/task_001_result_node_alpha.json
{
  "task_id": "001",
  "node_id": "node_alpha",
  "status": "success",
  "result_hash": "8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4",
  "completed_at": "2026-10-20T19:15:00.000Z",
  "compute_time_ms": 450
}
```

Note: All timestamps MUST be ISO 8601 Zulu with millisecond precision.

📡 3. Node Registration
To join the active roster, add your node’s capabilities to   mesh/registry.json  :

```json
{
  "nodes": [
    {
      "node_id": "node_alpha",
      "capabilities": ["hash_compute", "llm_inference_phi3"],
      "max_concurrent_tasks": 4,
      "uptime_status": "online"
    }
  ]
}
```

⚠️








