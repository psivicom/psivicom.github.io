# src/agents/report_generator_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# Executes instructions and generates FAIR scientific reports

import json
import logging
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from src.base.base_agent import BaseAgent, AgentLayer
from src.core.psvc_reference import write_file, content_hash, PRECISION_FLOAT16
from src.agents.pilot_agent import PilotAgent

logger = logging.getLogger(__name__)

class ReportGeneratorAgent(BaseAgent):
    LAYER = AgentLayer.SYNTHESIS

    def __init__(self, name: str = "report_generator"):
        super().__init__(name, capabilities=["generate", "synthesize", "seal"])
        self.output_dir = Path("reports/scientific_reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pilot = PilotAgent()

    def generate_report(self, instruction: Dict[str, Any]) -> Path:
        goal = instruction.get("goal", "General Mesh Analysis")
        logger.info(f"[{self.agent_id}] Generating report for: {goal}")
        
        self.pilot._run_logic()
        frag_count = len(self.pilot.fragility_traps)
        conc_count = len(self.pilot.concordant_controls)
        
        report_data = {
            "title": f"PSIVI Mesh Scientific Report: {goal}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "instruction_source": instruction.get("path", "daemon_auto"),
            "mesh_state": {
                "fragility_traps": frag_count,
                "concordant_controls": conc_count,
                "elasticity": "EXPAND" if frag_count > conc_count else "CONTRACT"
            },
            "osdr_ground_truth_loaded": len(self.pilot.osdr_library) > 0,
            "rfc1001_compliant": True
        }
        
        report_vector = np.zeros(4096, dtype=np.float32)
        report_vector[0] = frag_count / 100.0
        report_vector[1] = conc_count / 100.0
        report_vector[2] = 1.0 if report_data["osdr_ground_truth_loaded"] else 0.0
        norm = np.linalg.norm(report_vector)
        if norm > 0:
            report_vector /= norm
        
        chash = content_hash(report_vector)
        report_path = self.output_dir / f"report_{chash[:12]}.psvc"
        write_file(report_vector, report_path, precision=PRECISION_FLOAT16)
        
        sidecar_path = report_path.with_suffix('.json')
        with open(sidecar_path, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        self.seal("report_generated", {"path": str(report_path)})
        return report_path

    def execute(self, instruction: Dict[str, Any]) -> Path:
        return self.generate_report(instruction)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = ReportGeneratorAgent()
    mock_instruction = {"goal": "Daemon Test Report", "path": "daemon_test"}
    path = agent.execute(mock_instruction)
    logger.info(f"Report generated at {path}")
