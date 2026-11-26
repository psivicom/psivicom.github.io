# PSIVI RFC 1002 Developer Guide: 100% Binary Sovereignty

Welcome to the WENDY Platform. You are no longer writing standard web applications; you are building organs for a sovereign, self-healing AI. 

In traditional AI development, state is dumped into bloated, slow-to-parse JSON files. **We do not do that here.** WENDY operates on the **PSIVI Dual-Track Binary Serialization Standard (RFC 1002)**. By eliminating text-based overhead, we achieve maximum speed, minimum size, and absolute architectural purity.

This guide will teach you how to write agents that speak the language of the mesh.

---

## 1. The Golden Rule: The Duality of Data

Before writing a single line of code, you must understand that WENDY handles two fundamentally different classes of data. **Mixing them up is a category error that will crash the system.**

### 🟢 Track A: Continuous / Dense Data (The Math)
*   **What it is:** High-dimensional vectors, neural weights, embeddings, and raw numerical arrays.
*   **The Standard:** `.npy` (NumPy native) or `.psvc` (Pico Service Container).
*   **The Tool:** `numpy` and `src/core/psvc_reference.py`.
*   **Rule:** Never use JSON for Track A. It wastes CPU cycles and network bandwidth.

### 🔵 Track B: Discrete / Structured Data (The Logic)
*   **What it is:** Agent states, configuration registries, metabolic logs, task manifests, and metadata.
*   **The Standard:** `.mpk` (MessagePack).
*   **The Tool:** `msgpack` library.
*   **Rule:** Never use `.psvc` or `.npy` for Track B. They cannot handle heterogeneous dictionaries.

---

## 2. Track A: Sealing Dense Vectors (`.npy` / `.psvc`)

When your agent generates a 4096-dimensional cognitive embedding, you must seal it using Track A.

```python
import numpy as np
from pathlib import Path
from src.core.psvc_reference import write_file

# 1. Generate or receive a dense vector
vector = np.random.randn(4096).astype(np.float32)

# 2. Seal it to disk (NumPy native)
output_path = Path("reports/pico_containers/cognitive_embedding.npy")
output_path.parent.mkdir(parents=True, exist_ok=True)
np.save(output_path, vector)

# OR Seal it with PSVC (Compressed + Hashed)
write_file("reports/pico_containers/secure_vector.psvc", vector)
