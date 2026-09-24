# docs/QWEN/EXAMPLE_WORKFLOWS.md
# SPDX-License-Identifier: CC-BY-SA-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

# 🚀 PSIVI Mesh: Example Autonomous Workflows for External AI

This document provides concrete, copy-pasteable examples of how an external AI (like Qwen) can autonomously interact with the PSIVI Mesh to advance scientific research.

---

## Workflow 1: Resolving an OSDR Spaceflight Fragility Trap

**Scenario:** The mesh `PilotAgent` detected a contradiction in spaceflight gene expression (e.g., `IGFBP7` in `homo_sapiens`). The external AI decides to spawn a literature resolver to find orthogonal datasets.

**AI Action:** Generate and drop an instruction.

```python
from ai_handshake_guide import seal_instruction

# 1. Define the resolution task
seal_instruction(
    command="spawn_agent",
    params={
        "template_name": "literature_resolver",
        "agent_name": "resolve_igfbp7_spaceflight",
        "config": {
            "gene": "IGFBP7",
            "organism": "homo_sapiens",
            "context": "cells_cultured",
            "target_databases": ["zenodo", "semantic_scholar"],
            "priority": "HIGH"
        }
    }
)
# Result: Mesh creates src/agents/resolve_igfbp7_spaceflight_agent.py and executes search.
