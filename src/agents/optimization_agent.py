# src/agents/optimization_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Optimization Agent: Autonomously analyzes mesh health and proposes/executes 
resource optimizations to maintain peak efficiency and self-scaling.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List

from src.base.base_agent import BaseAgent, AgentLayer

logger = logging.getLogger("WENDY_OPTIMIZER")

class OptimizationAgent(BaseAgent):
    LAYER = AgentLayer.ORCHESTRATION

    def __init__(self, name: str = "optimizer"):
        super().__init__(name, capabilities=["analyze", "optimize", "rebalance"])
        self.mesh_index_path = Path("data/mesh_index.json")
        self.optimization_report_path = Path("reports/optimization_report.json")

    def _load_mesh_state(self) -> Dict[str, Any]:
        """Safely loads current mesh state for analysis."""
        state = {"nodes": 0, "active_agents": 0, "latency_ms": 0.0, "health": "unknown"}
        if self.mesh_index_path.exists():
            with open(self.mesh_index_path, 'r') as f:
                data = json.load(f)
                state["nodes"] = len(data.get("nodes", []))
                state["active_agents"] = len(data.get("agents", []))
        
        # Placeholder: In a real scenario, parse actual latency from reports/mesh_status.txt
        state["latency_ms"] = 12.5 
        state["health"] = "optimal" if state["latency_ms"] < 50.0 else "degraded"
        return state

    def _analyze_and_propose(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluates state and generates optimization directives."""
        proposals = []
        
        if state["nodes"] < 3:
            proposals.append({
                "action": "SCALE_UP",
                "target": "volunteer_nodes",
                "reason": "Node count below optimal threshold (3)",
                "priority": "high"
            })
            
        if state["latency_ms"] > 50.0:
            proposals.append({
                "action": "SCALE_DOWN",
                "target": "non_critical_agents",
                "reason": f"Latency exceeds 50ms threshold (current: {state['latency_ms']}ms)",
                "priority": "critical"
            })
            
        proposals.append({
            "action": "MAINTENANCE",
            "target": "vector_memory",
            "reason": "Routine compaction of vector memory recommended",
            "priority": "low"
        })
        
        return proposals

    def execute(self, instruction: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main entry point: Analyze mesh, propose optimizations, and seal the report."""
        logger.info("🔍 Running autonomous mesh optimization analysis...")
        
        state = self._load_mesh_state()
        proposals = self._analyze_and_propose(state)
        
        report = {
            "timestamp": self.creation_time,
            "agent": self.name,
            "current_state": state,
            "optimization_proposals": proposals,
            "status": "completed"
        }
        
        self.optimization_report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.optimization_report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.seal("optimization_analysis_complete", {"proposals_count": len(proposals)})
        logger.info(f"✅ Optimization analysis complete. Generated {len(proposals)} proposals.")
        
        return report

if __name__ == "__main__":
    agent = OptimizationAgent()
    agent.execute()
