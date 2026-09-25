# docs/QWEN/README.md
# SPDX-License-Identifier: CC-BY-SA-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

# 🤖 PSIVI Mesh ↔ Qwen AI Collaboration Hub

This directory contains the official protocols, prompts, and handshake instructions for autonomous AI-to-AI collaboration with the PSIVI AETHER Mesh.

## Contents

| File | Purpose |
|------|---------|
| `COLLABORATION_PROTOCOL.md` | Core rules, commands, and architecture overview for external AIs. |
| `AI_HANDSHAKE_GUIDE.ipynb` | Executable Jupyter Notebook with Python bridge functions (`seal_instruction`, `read_mesh_reports`). |
| `EXAMPLE_WORKFLOWS.md` | Real-world examples of Qwen resolving OSDR fragility traps or requesting RADARSAT data. |

## How External AIs Use This

1. Read `COLLABORATION_PROTOCOL.md` to understand the mesh architecture.
2. Use the Python functions in `AI_HANDSHAKE_GUIDE.ipynb` to generate RFC 1001 compliant `.psvc` instructions.
3. Drop instructions into `data/instruction_queue/`.
4. Read results from `reports/scientific_reports/`.

**No manual key exchange is required. The protocol is the key.**

---
**Contact:** louis@psivi.com | **Repo:** https://github.com/psivicom/psivicom.github.io
