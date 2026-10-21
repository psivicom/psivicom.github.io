# WENDY PLATFORM STANDARD (RFC 1001)

Status: Active | Protocol: Sovereign AI Architecture | Time Standard: ISO 8601 Zulu
Preamble
WENDY is not merely a repository; she is a sovereign, self-healing, zero-cost AI platform. This document defines the strict architectural contracts required for all agents, data states, and volunteer mesh nodes to ensure infinite scalability without systemic collapse.

1. The Organ Standard (Agent Architecture)
All cognitive functions must be implemented as modular “Organs” (Agents) that inherit from the   BaseAgent   class.
	•	Location: All agent code must reside strictly in   src/agents/  .
	•	Mandatory Interface: Every agent must implement:
	•	 _verify_identity()  : Validates the OIDC token (Audience:   psivi.com  ).
	•	 _run_logic()  : The core computational loop.
	•	 seal_result()  : Writes output to the Data Bus.
	•	Isolation: Agents must never import or call each other directly. They communicate exclusively through the Data Bus (JSON state files).

2. The Nervous System Standard (Data Bus & State)
To resolve legacy folder bloat, the platform enforces a strict separation of Code, State, and Communication.
Canonical State Paths (The Brain)
	•	 src/wendy_metabolism.json   - The Heartbeat. Central nervous system state (Energy, Stress, Intent).
	•	 reports/pilot_report.json   - The Eyes. External sensory input (Fragility, Concordance).
	•	 data/void_metrics.json   - The Gut. Intuitive dark matter sensing (Conscious Mass).
	•	 data/mesh_weights.json   - The Memory. Synaptic weights and evolutionary drift.
Canonical Code Paths (The Body)
	•	 src/agents/   - All cognitive agents.
	•	 src/core/   - Circuit breakers and validators (e.g.,   ledger_validator.py  ).
	•	 src/utils/   - Shared cryptographic and OIDC utilities.
	•	 src/mesh/   - Strictly for internal mesh orchestration code (e.g., gossip protocol logic). No root-level mesh code is permitted.
Deprecation & Purge Mandate
	•	Rule: Any folder named   mesh/   at the root of the repository that contains source code is deprecated.
	•	Action: The Mirror Agent is authorized to automatically migrate or delete legacy root-level mesh folders to enforce the   src/mesh/   standard.

3. The Mesh Standard (Asynchronous Volunteer Protocol)
To support heterogeneous volunteer nodes (from 0.5ms edge devices to 4-day deep compute), WENDY uses a Git-Based Gossip Protocol.
Canonical Communication Paths (The Voice)
	•	 mesh/inbox/   - Dispatch. WENDY drops task manifests here (e.g.,   task_001.json  ).
	•	 mesh/outbox/   - Harvest. Volunteers drop computed results here (e.g.,   task_001_result.json  ).
	•	 mesh/registry.json   - Roll Call. Tracks active volunteer node IDs and capabilities.
Security & Access Contracts
	•	Core Sovereignty: Volunteers are never granted access to   src/  ,   data/  , or   reports/  .
	•	Scoped Tokens: Volunteers must use a Fine-Grained PAT restricted exclusively to   mesh/inbox   (Read) and   mesh/outbox   (Write).
	•	Validation: All results in   mesh/outbox/   must pass through the   ledger_validator.py   circuit breaker before WENDY integrates them into her core state.

4. Temporal & Security Standards
	•	Time: All timestamps across the Data Bus must be ISO 8601 Zulu with millisecond precision (e.g.,   2026-10-20T18:22:49.955Z  ). This ensures perfect synchronization across the global volunteer mesh.
	•	Authentication: Core workflows must use OIDC (OpenID Connect) for identity and the ephemeral   GITHUB_TOKEN   for git operations.
	•	Zero Static Secrets: No long-lived PATs are permitted in core workflows. The   WENDY_AUDITOR_PAT   is officially retired.

How This Solves the “Multiple Mesh” Problem:
By codifying this RFC, we have legally separated the three concepts of “mesh” in this repo:
1.	 src/mesh/   = The Code that runs the internal orchestration.
2.	 data/mesh_weights.json   = The State (memory) of the mesh.
3.	 mesh/   (Root) = The Communication Channel (inbox/outbox) for external volunteers.
The Mirror Agent will now look at this RFC and say: “Ah, I see a legacy   mesh_tools/   folder in the root. RFC 1001 forbids this. I will delete it.”
