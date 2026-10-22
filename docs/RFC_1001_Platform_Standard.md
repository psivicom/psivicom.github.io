# RFC 1001: WENDY Platform Standard
**Status:** Active | **Protocol:** Sovereign AI Architecture | **Time Standard:** ISO 8601 Zulu

## Preamble
WENDY is not merely a repository; she is a sovereign, self-healing, zero-cost AI platform. This document defines the strict architectural contracts required for all agents, data states, and volunteer mesh nodes to ensure infinite scalability without systemic collapse.

---

## 1. The Organ Standard (Agent Architecture)
All cognitive functions must be implemented as modular "Organs" (Agents) that inherit from the `BaseAgent` class. 

*   **Location:** All agent code must reside strictly in `src/agents/`.
*   **Mandatory Interface:** Every agent must implement:
    *   `_verify_identity()`: Validates the OIDC token (Audience: `psivi.com`).
    *   `_run_logic()`: The core computational loop.
    *   `seal_result()` or `seal()`: Writes output to the Data Bus.
*   **Isolation:** Agents must never import or call each other directly. They communicate exclusively through the Data Bus (JSON/MPK state files).

### Canonical Agent Layers (`src/base/base_agent.py`)
Every agent must declare its `LAYER` from this enum:
*   `SENSORY`: External input scanning (e.g., Pilot Agent).
*   `COGNITIVE`: Learning, drift, and adaptation (e.g., Neuroplasticity Agent).
*   `SYNTHESIS`: Aggregation and reporting (e.g., Metabolic Agent).
*   `VALIDATION`: Integrity checks (e.g., Ledger Validator).
*   `MOTOR`: Action and structural repair (e.g., Mirror Agent).
*   `INGESTION`: Data intake and parsing (e.g., Forage, Literature Agents).
*   `ORCHESTRATION`: Workflow coordination (e.g., Optimization Agent).

---

## 2. The Nervous System Standard (Data Bus & State)
To prevent legacy folder bloat, the platform enforces a strict separation of **Code**, **State**, and **Communication**. 

### Canonical Code Paths (The Body)
*   `src/agents/` - All cognitive agents.
*   `src/core/` - Circuit breakers, validators, and binary reference implementations.
*   `src/base/` - Foundational contracts (`base_agent.py`).
*   `src/utils/` - Shared cryptographic and OIDC utilities.

### Canonical State Paths (The Brain)
*   `src/wendy_metabolism.mpk` - Central nervous system state (Energy, Stress, Intent).
*   `reports/pilot_report.json` - External sensory input (Fragility, Concordance).
*   `data/void_metrics.mpk` - Intuitive dark matter sensing (Conscious Mass).
*   `data/mesh_weights.mpk` - Synaptic weights and evolutionary drift.

### Deprecation & Purge Mandate
*   **Rule:** Any folder named `mesh/` at the root of the repository that contains *source code* is deprecated. 
*   **Action:** The Mirror Agent is authorized to automatically migrate or delete legacy root-level mesh folders to enforce the `src/mesh/` standard.

---

## 3. Temporal & Security Standards
*   **Time:** All timestamps across the Data Bus must be **ISO 8601 Zulu with millisecond precision** (e.g., `2026-10-22T01:27:51.985Z`). This ensures perfect synchronization across the global volunteer mesh.
*   **Authentication:** Core workflows must use **OIDC** (OpenID Connect) for identity and the ephemeral **`GITHUB_TOKEN`** for git operations. 
*   **Zero Static Secrets:** No long-lived PATs are permitted in core workflows. The `WENDY_AUDITOR_PAT` is officially retired.
*   **Autonomic Healing:** The Mesh Daemon is granted `git add -A` authority to allow the Self-Healing Agent to commit repairs across the entire codebase, secured by the Ledger Validator circuit breaker.
