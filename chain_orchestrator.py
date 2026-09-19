# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# Author: Louis-Philippe Audette
# ORCID: https://orcid.org/0000-000X-XXXX-XXXX
#
# Chain Orchestrator (The Vector-Native Leda)
# RFC 1001 Compliant - Sequential Adaptive Vector Chaining.
# Replaces text-based LLM chaining with pure mathematical vector passing.

import os
import sys
import json
import datetime
import numpy as np
from pathlib import Path
from psvc_reference import (
    read_file, write_file, content_hash, validate_file,
    encode_text, PRECISION_INT8, PRECISION_FLOAT16, PSVCError
)

CONTAINER_DIR = Path("reports/pico_containers")
CHAIN_DIR = Path("reports/chains")

def execute_chain(goal_text, pipeline):
    """
    Executes a sequential chain of agents.
    pipeline = ["forage", "critic", "intelligence"]
    """
    print(f"\n=== CHAIN ORCHESTRATOR: {goal_text} ===")
    print(f"[CHAIN] Pipeline: {' -> '.join(pipeline)}\n")
    
    CHAIN_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Encode the Goal as the Seed Vector
    goal_vector = encode_text(goal_text)
    current_vector = goal_vector
    chain_id = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    chain_log = []
    
    # 2. Execute the Sequential Chain
    for step, agent_type in enumerate(pipeline):
        print(f"[CHAIN] Step {step + 1}/{len(pipeline)}: Executing {agent_type}...")
        
        # Simulate Agent Execution
        # In a real system, this would call the specific agent's logic.
        # Here, we simulate the agent transforming the input vector.
        
        if agent_type == "forage":
            # Forage adds environmental context (simulated by vector math)
            noise = np.random.randn(4096).astype(np.float32) * 0.1
            current_vector = current_vector + noise
            current_vector /= np.linalg.norm(current_vector)
            action = "Added environmental telemetry"
            
        elif agent_type == "critic":
            # Critic applies error correction (simulated by shifting vector)
            correction = np.random.randn(4096).astype(np.float32) * 0.05
            current_vector = current_vector - correction
            current_vector /= np.linalg.norm(current_vector)
            action = "Applied drift correction"
            
        elif agent_type == "literature":
            # Literature grounds in science (simulated by blending)
            science_vector = encode_text("Bombus terrestris optimal foraging theory")
            current_vector = (current_vector * 0.7) + (science_vector * 0.3)
            current_vector /= np.linalg.norm(current_vector)
            action = "Grounded in scientific literature"
            
        elif agent_type == "intelligence":
            # Intelligence audits the result
            norm = np.linalg.norm(current_vector)
            action = f"Audited final state (Norm: {norm:.4f})"
            
        else:
            action = "Unknown agent type, passed through"
            
        # 3. Seal the Intermediate Step
        chash = content_hash(current_vector)
        step_filename = f"chain_{chain_id}_step{step}_{agent_type}_{chash}.psvc"
        step_path = CONTAINER_DIR / step_filename
        
        write_file(current_vector, step_path, precision=PRECISION_FLOAT16)
        
        # Write step sidecar
        sidecar_path = step_path.with_suffix('.json')
        with open(sidecar_path, 'w') as f:
            json.dump({
                "agent": agent_type,
                "chain_id": chain_id,
                "step": step + 1,
                "action": action,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "type": "chain_step"
            }, f, indent=2)
            
        print(f"  -> {action}")
        print(f"  -> Sealed: {step_filename}")
        
        chain_log.append({
            "step": step + 1,
            "agent": agent_type,
            "action": action,
            "file": step_filename
        })
    
    # 4. Seal the Final Chain Result
    final_chash = content_hash(current_vector)
    final_filename = f"chain_{chain_id}_FINAL_{final_chash}.psvc"
    final_path = CONTAINER_DIR / final_filename
    
    write_file(current_vector, final_path, precision=PRECISION_FLOAT16)
    
    # Write final sidecar
    final_sidecar = final_path.with_suffix('.json')
    with open(final_sidecar, 'w') as f:
        json.dump({
            "agent": "orchestrator",
            "chain_id": chain_id,
            "goal": goal_text,
            "pipeline": pipeline,
            "steps_completed": len(pipeline),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "type": "chain_result"
        }, f, indent=2)
        
    print(f"\n[CHAIN] === CHAIN COMPLETE ===")
    print(f"[CHAIN] Final result sealed: {final_filename}")
    print(f"[CHAIN] The mesh executed a {len(pipeline)}-step sequential workflow autonomously.")
    
    return final_path

if __name__ == "__main__":
    # Example: A complex goal that requires multiple agents to work in sequence
    GOAL = "Analyze today's Goldstream forage window against recent pollinator heat-stress literature and audit the prediction confidence."
    
    # The Adaptive Chain (The Vector-Native Leda)
    PIPELINE = [
        "forage",       # Step 1: Get the raw data
        "literature",   # Step 2: Ground it in science
        "critic",       # Step 3: Correct for recent weather drift
        "intelligence"  # Step 4: Audit the final confidence
    ]
    
    execute_chain(GOAL, PIPELINE)
