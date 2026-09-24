# src/automation/ai_planner.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# Lightweight AI Planner | Deterministic Step Mapping | Branch-Free

import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger(__name__)

class AIPlanner:
    STEP_TEMPLATES = {
        "EXPAND": [
            {"step_id": "step_2", "agent_id": "literature_agent", "operation": "resolve_discordance", "dependencies": ["step_1"]},
            {"step_id": "step_3", "agent_id": "critic_agent", "operation": "evaluate_significance", "dependencies": ["step_2"]}
        ],
        "CONTRACT": [
            {"step_id": "step_2", "agent_id": "consolidator_agent", "operation": "prune_redundant", "dependencies": ["step_1"]}
        ],
        "STABLE": [
            {"step_id": "step_2", "agent_id": "synthesizer_agent", "operation": "generate_insight", "dependencies": ["step_1"]}
        ]
    }

    def __init__(self, model_endpoint: str = "http://localhost:11434/api/generate", model_name: str = "phi3:mini"):
        self.model_endpoint = model_endpoint
        self.model_name = model_name
        self.use_local_mock = True

    def generate_workflow_dag(self, goal: str, pilot_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        fragility_count = pilot_report.get("fragility_count", 0)
        concordance_count = pilot_report.get("concordance_count", 0)
        score = int(np.clip(fragility_count - concordance_count, -1, 1))
        decision = ["CONTRACT", "STABLE", "EXPAND"][score + 1]
        base_step = [{"step_id": "step_1", "agent_id": "forage_agent", "operation": "collect_data", "dependencies": []}]
        extension = self.STEP_TEMPLATES.get(decision, [])
        return base_step + extension

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    planner = AIPlanner()
    report = {"fragility_count": 5, "concordance_count": 2}
    dag = planner.generate_workflow_dag("Test Goal", report)
    logger.info(f"Generated DAG: {json.dumps(dag, indent=2)}")
