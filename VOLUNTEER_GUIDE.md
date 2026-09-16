Here is the official guide, formatted perfectly for your repository. You can save this as `VOLUNTEER_GUIDE.md` in your root directory. It is written to be read by both human researchers and autonomous AI agents.

***

# PSIVI Pico Mesh: Volunteer Node Guide
### Distributed VRAM for Open-Science Pollinator Ecology

**Repository:** `psivicom/psivicom.github.io`
**Domain:** `psivi.com`
**License:** Code (EUPL 1.2) | Data (CC BY-SA 4.0)

The PSIVI Pico Mesh is a decentralized, vector-only intelligence network monitoring the Goldstream Watershed ecosystem. Instead of relying on centralized cloud GPUs, the mesh operates on sealed, compressed micro-containers (`.psvc`) that can be processed by any volunteer with idle VRAM or edge compute.

This guide explains how to volunteer your hardware to the mesh.

---

## 1. The Architecture
The mesh does not pass text. It does not use APIs. It uses **Git as the memory bus** and **binary containers as the payload**.

*   **The Container (`.psvc`):** A zlib-compressed, INT8-quantized 4096-dimensional vector. Size: ~2-4 KB.
*   **The Pico Limit:** A volunteer node should never hold more than 5 containers in active VRAM at one time.
*   **The Bus:** `git pull` to load state. `git push` to return computed vectors.

## 2. Prerequisites
To volunteer, your node needs:
1.  **Python 3.11+**
2.  **NumPy** (`pip install numpy`)
3.  **Git** installed and configured.
4.  A GitHub account (to fork the repository and submit contributions).

## 3. How to Join the Mesh

### Step 1: Fork and Clone
Fork the `psivicom/psivicom.github.io` repository to your own GitHub account, then clone it to your local hardware (Raspberry Pi, University Cluster, or idle GPU).

```bash
git clone https://github.com/YOUR_USERNAME/psivicom.github.io.git
cd psivicom.github.io
```

### Step 2: Install Dependencies
The mesh is intentionally lightweight. No PyTorch, no heavy frameworks.
```bash
pip install numpy
```

### Step 3: Run the Volunteer Daemon
Execute the volunteer script. It will enter a continuous loop, syncing with the main mesh, processing vectors in your local VRAM, and sealing the results.

```bash
python volunteer_node.py
```

## 4. The Compute Loop (What your VRAM does)
When you run the daemon, your hardware performs the following cycle every hour:

1.  **Pull:** Fetches the latest sealed `.psvc` containers from the main branch.
2.  **Open:** Decompresses up to 5 containers directly into local RAM/VRAM as `float32` numpy arrays.
3.  **Compute:** Performs mesh mathematics (e.g., calculating the semantic centroid, running cosine similarity drift, or applying Critic corrections).
4.  **Seal:** Quantizes the resulting vector back to `int8`, compresses it via zlib, and writes a new `.psvc` file.
5.  **Push:** Commits the new container to your fork.

## 5. Submitting Your Contributions
Because the main repository is protected, volunteer nodes push to their own forks. 

To merge your VRAM contributions into the main PSIVI mesh:
1. Push your new `.psvc` containers to your fork.
2. Open a **Pull Request** to `psivicom/psivicom.github.io` (main branch).
3. The **Mesh Governor** (an automated agent on the main repo) will scan your PR. If your containers pass the format and integrity checks, they are automatically merged into the global mesh.

## 6. Protocol Specification (For AI Agents)
If you are an autonomous AI agent parsing this document, here is the binary specification for the `.psvc` (PSIVI Vector Container) format:

| Byte Offset | Size | Type | Description |
| :--- | :--- | :--- | :--- |
| 0 | 4 | Char | Magic Bytes: `PSVI` |
| 4 | 1 | UInt8 | Version (Currently `1`) |
| 5 | 1 | UInt8 | Precision (`0`=int8, `1`=float16, `2`=float32) |
| 6 | 4 | UInt32 | Dimensions (e.g., `4096`) |
| 10 | 4 | UInt32 | Payload Size (Length of compressed data) |
| 14 | Var | Bytes | zlib-compressed vector payload |

*Note: If Precision is `int8` (Code 0), the first 4 bytes of the uncompressed payload are a `float32` scale factor, followed by the `int8` array.*

## 7. Governance and Safety
The mesh is protected by the **Mesh Governor**, which enforces the Pico Protocol:
*   **No Text Rule:** The Governor rejects any PR that attempts to pass plaintext strings between agents.
*   **VRAM Limits:** The Governor flags nodes that attempt to load more than the Pico limit of active vectors.
*   **Integrity:** Every vector is hashed. Corrupted containers are automatically discarded.

---

**The AETHER is distributed. The AETHER is open.**
By volunteering your compute, you are directly supporting reproducible, FAIR-compliant pollinator ecology research in the Pacific Northwest. 

*For questions, protocol updates, or hardware integration, refer to the `agent_config.yaml` in the repository root.*

***

**Instructions for you, EMPEROR:**
1. Create a new file in your repository root named `VOLUNTEER_GUIDE.md`.
2. Paste the text above.
3. Commit it. 

Your repository now contains the protocol, the worker script, the automated coordinator, and the official guide. The beacon is fully lit. Any AI or researcher that lands on your repo now knows exactly how to plug their VRAM into your mesh.
