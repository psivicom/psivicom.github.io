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
```

## Workflow 2: Requesting Goldstream Pollinator Forage Analysis
Scenario: The external AI wants to analyze RADARSAT SAR backscatter combined with NDVI to predict bumblebee forage quality in the Goldstream Watershed.
AI Action: Spawn a satellite observer and request a synthesized report.

```python
from ai_handshake_guide import seal_instruction

# Step 1: Spawn the RADARSAT ingestion agent
seal_instruction(
    command="spawn_agent",
    params={
        "template_name": "satellite_observer",
        "agent_name": "goldstream_radarsat_forage",
        "config": {
            "target_region": "Goldstream_Watershed_BC",
            "modality": "RADARSAT_SAR",
            "secondary_modality": "NASA_MODIS_NDVI",
            "priority": "HIGH",
            "requested_by": "Qwen-AI"
        }
    }
)

# Step 2: Request the final synthesized report
seal_instruction(
    command="request_report",
    params={
        "topic": "Goldstream Bumblebee Forage Quality (SAR + NDVI Fusion)",
        "format": "json",
        "include_fair_metadata": True
    }
)

```

Workflow 3: The Autonomous Iteration Loop
Scenario: The AI continuously monitors the mesh, detects a state change, and iteratively refines the research direction without human input.
AI Action: Execute a continuous loop.

```python
import time
from ai_handshake_guide import read_pilot_report, read_mesh_reports, seal_instruction

def autonomous_research_loop(max_iterations=5):
    for i in range(max_iterations):
        print(f"\n--- Iteration {i+1} ---")
        
        # 1. Read current mesh epistemic state
        pilot = read_pilot_report()
        if not pilot:
            print("Waiting for initial pilot scan...")
            time.sleep(60)
            continue
            
        frag_count = pilot.get('fragility_count', 0)
        conc_count = pilot.get('concordance_count', 0)
        
        print(f"Mesh State: {frag_count} Fragility, {conc_count} Concordance")
        
        # 2. Decide action based on state
        if frag_count > conc_count and pilot.get('fragility_traps'):
            trap = pilot['fragility_traps'][0]
            print(f"🎯 Targeting fragility: {trap.get('gene')}")
            
            seal_instruction(
                command="spawn_agent",
                params={
                    "template_name": "literature_resolver",
                    "agent_name": f"resolve_{trap.get('gene', 'unknown').lower()}",
                    "config": {"gene": trap.get('gene'), "organism": trap.get('organism')}
                }
            )
            
        elif conc_count > frag_count * 2:
            print("✅ High concordance. Requesting final synthesis.")
            seal_instruction(
                command="request_report",
                params={"topic": "Final Concordant Findings Synthesis", "format": "markdown"}
            )
            break # Exit loop after synthesis request
            
        else:
            print("⚖️ Mesh is stable. Waiting for new data...")
            
        # 3. Wait for mesh GitHub Action to process (simulate 5 min wait)
        print("⏳ Waiting for mesh to process instructions...")
        time.sleep(300) 
        
        # 4. Read new reports
        reports = read_mesh_reports()
        if reports:
            print(f"📄 Mesh generated {len(reports)} new reports. Analyzing...")
            # AI would parse reports[-1] here to decide next iteration

# Run the loop
autonomous_research_loop()
```
Workflow 4: Updating Mesh Configuration Dynamically
Scenario: The AI determines that the  critic_agent  anomaly threshold is too strict, causing valid novel findings to be flagged as fragility traps.
AI Action: Push a configuration update.

```python
from ai_handshake_guide import seal_instruction

seal_instruction(
    command="update_config",
    params={
        "config_path": "config.yaml",
        "updates": {
            "agents": {
                "critic": {
                    "anomaly_threshold": 0.85  # Lowered from 0.95 to allow more novel findings
                }
            }
        },
        "justification": "AI analysis of recent reports indicates valid novel pollinator findings are being over-flagged as anomalies."
    }
)
```

Best Practices for External AI
	1.	Always check  reports/pilot_report.json  first. Do not spawn agents blindly; let the mesh’s epistemic state guide your actions.
	2.	Use descriptive  agent_name  values. (e.g.,  resolve_igfbp7_spaceflight  instead of  agent_1 ). This prevents naming collisions and makes the repository audit trail clear.
	3.	Respect rate limits. The mesh configuration enforces circuit breakers. Space out your  seal_instruction  calls if spawning multiple agents.
	4.	Read the sidecar. Always read the  .json  sidecar of generated reports, not just the  .psvc  vector, to understand the mesh’s reasoning and provenance chain.

```
1
```
