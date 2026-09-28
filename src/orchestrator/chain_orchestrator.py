# src/orchestrator/chain_orchestrator.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Chain Orchestrator: Manages the execution flow of multi-agent pipelines.
Ensures deterministic, auditable, and FAIR-compliant sequencing of tasks
(e.g., Forage -> Literature -> Satellite -> Critic -> Intelligence).
"""

import json
import logging
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from src.core.zulu_clock import get_zulu_timestamp_ms
from src.core.psvc_containers import build_psvc_from_array, serialize_psvc

logger = logging.getLogger("CHAIN_ORCHESTRATOR")

class ChainOrchestrator:
    """
    Orchestrates a sequence of agent executions, managing state, 
    error handling, and PSVC artifact generation for each step.
    """
    
    def __init__(self, chain_id: Optional[str] = None):
        self.chain_id = chain_id or uuid.uuid4().hex[:16]
        self.steps: List[Dict[str, Any]] = []
        self.current_step = 0
        self.status = "INITIALIZED"
        self.start_time = get_zulu_timestamp_ms()
        self.artifacts_dir = Path("reports/pico_containers")
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def add_step(self, agent_name: str, input_data: Dict[str, Any]) -> None:
        """Adds a step to the execution chain."""
        self.steps.append({
            "step_index": len(self.steps),
            "agent": agent_name,
            "input": input_data,
            "status": "PENDING",
            "output": None,
            "timestamp": None
        })

    def execute_chain(self) -> Dict[str, Any]:
        """
        Executes the entire chain. 
        In a full implementation, this would dynamically import and run agents.
        For validation and baseline operation, it simulates the chain progression.
        """
        logger.info(f"🚀 Starting Chain Execution: {self.chain_id}")
        self.status = "RUNNING"
        
        for i, step in enumerate(self.steps):
            logger.info(f"⚙️ Executing Step {i}: {step['agent']}")
            try:
                # Simulate agent execution
                step["status"] = "SUCCESS"
                step["output"] = {"result": f"Processed by {step['agent']}", "chain_id": self.chain_id}
                step["timestamp"] = get_zulu_timestamp_ms()
                
                # Generate PSVC artifact for this step
                self._save_step_artifact(step)
                
            except Exception as e:
                logger.error(f"❌ Step {i} failed: {e}")
                step["status"] = "FAILED"
                step["error"] = str(e)
                self.status = "FAILED"
                break
                
        self.status = "COMPLETED" if self.status == "RUNNING" else self.status
        logger.info(f"✅ Chain Execution {self.status}: {self.chain_id}")
        
        return self.get_chain_summary()

    def _save_step_artifact(self, step: Dict[str, Any]) -> None:
        """Saves the step output as a PSVC container and JSON sidecar."""
        import numpy as np
        
        step_id = uuid.uuid4().hex[:16]
        ts_safe = get_zulu_timestamp_ms().replace(':', '').replace('-', '').replace('.', '')
        
        # Create a state vector representing the step's execution
        state_vector = np.array([float(step['step_index']), 1.0, 0.0], dtype=np.float32)
        
        container = build_psvc_from_array(
            array=state_vector,
            operation="chain_step",
            agent_id=step["agent"],
            layer="ORCHESTRATION",
            shard_id=step_id,
            content_type="chain_step_output",
            sender_id="chain_orchestrator"
        )
        
        serialized = serialize_psvc(container)
        
        # Save PSVC
        psvc_path = self.artifacts_dir / f"chain_{ts_safe}_step{step['step_index']}_{step['agent']}_{step_id}.psvc"
        psvc_path.write_bytes(serialized)
        
        # Save JSON sidecar
        json_path = psvc_path.with_suffix('.json')
        json_path.write_text(json.dumps({
            "chain_id": self.chain_id,
            "step_index": step["step_index"],
            "agent": step["agent"],
            "status": step["status"],
            "output": step["output"],
            "timestamp": step["timestamp"]
        }, indent=2), encoding="utf-8")

    def get_chain_summary(self) -> Dict[str, Any]:
        """Returns a summary of the chain execution."""
        return {
            "chain_id": self.chain_id,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": get_zulu_timestamp_ms(),
            "total_steps": len(self.steps),
            "successful_steps": sum(1 for s in self.steps if s["status"] == "SUCCESS"),
            "artifacts_path": str(self.artifacts_dir)
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')
    
    orchestrator = ChainOrchestrator()
    orchestrator.add_step("forage_agent", {"query": "pollinator_data"})
    orchestrator.add_step("literature_agent", {"context": "forage_results"})
    
    summary = orchestrator.execute_chain()
    print(json.dumps(summary, indent=2))
