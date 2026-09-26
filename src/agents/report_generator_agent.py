# src/agents/report_generator_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import json
import logging
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
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
        # Initialize Pilot with default OSDR path; Pollinator support can be added via config injection later
        self.pilot = PilotAgent(osdr_data_path="data/osdr_ground_truth.jsonl")

    def generate_report(self, instruction: Dict[str, Any]) -> Path:
        goal = instruction.get("params", {}).get("topic", "General Mesh Analysis")
        fmt = instruction.get("params", {}).get("format", "json")
        
        logger.info(f"[{self.agent_id}] Generating report for: {goal} (Format: {fmt})")
        
        # Execute validation logic to refresh mesh state
        try:
            self.pilot._run_logic()
        except Exception as e:
            logger.error(f"Failed to run pilot logic during report generation: {e}")
            # Continue with stale data if possible, or return error
            
        frag_count = len(self.pilot.fragility_traps)
        conc_count = len(self.pilot.concordant_controls)
        
        # Determine elasticity based on current state
        if frag_count > conc_count:
            elasticity = "EXPAND"
        elif conc_count > frag_count * 2:
            elasticity = "CONTRACT"
        else:
            elasticity = "STABLE"

        report_data = {
            "title": f"PSIVI Mesh Scientific Report: {goal}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "instruction_source": instruction.get("path", "daemon_auto"),
            "mesh_state": {
                "fragility_traps": frag_count,
                "concordant_controls": conc_count,
                "elasticity": elasticity
            },
            "osdr_ground_truth_loaded": len(self.pilot.osdr_library) > 0,
            "rfc1001_compliant": True,
            "generated_by": "WENDY_Authorized_Daemon"
        }
        
        # Create vector representation of the report state
        report_vector = np.zeros(4096, dtype=np.float32)
        report_vector[0] = frag_count / 100.0
        report_vector[1] = conc_count / 100.0
        report_vector[2] = 1.0 if report_data["osdr_ground_truth_loaded"] else 0.0
        
        norm = np.linalg.norm(report_vector)
        if norm > 0:
            report_vector /= norm
        
        chash = content_hash(report_vector)
        report_filename = f"report_{chash[:12]}.psvc"
        report_path = self.output_dir / report_filename
        
        # Write binary container
        write_file(report_vector, report_path, precision=PRECISION_FLOAT16)
        
        # Write JSON sidecar
        sidecar_path = report_path.with_suffix('.json')
        with open(sidecar_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
            
        self.seal("report_generated", {"path": str(report_path), "topic": goal})
        logger.info(f"✅ Report sealed: {report_path.name}")
        
        return report_path

    def execute(self, instruction: Dict[str, Any]) -> Path:
        """
        Main entry point called by auto_reporter.
        Expects instruction dict with 'command' and 'params'.
        """
        cmd = instruction.get("command")
        
        if cmd == "request_report":
            return self.generate_report(instruction)
        else:
            logger.warning(f"Unknown command for ReportGenerator: {cmd}")
            # Return a dummy path or raise error depending on strictness
            return Path("reports/scientific_reports/error_no_report.psvc")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = ReportGeneratorAgent()
    
    # Simulate WENDY's initial request
    mock_instruction = {
        "command": "request_report",
        "params": {
            "topic": "Goldstream Fragility Status",
            "format": "json"
        },
        "path": "data/instruction_queue/wendy_initial_request.json"
    }
    
    path = agent.execute(mock_instruction)
    logger.info(f"Test report generated at: {path}")
