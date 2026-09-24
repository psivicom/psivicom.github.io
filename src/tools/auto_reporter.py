# src/tools/auto_reporter.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# Main entry point for instruction handling and report generation

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.instruction_agent import InstructionAgent
from src.agents.agent_factory import AgentFactory
from src.agents.report_generator_agent import ReportGeneratorAgent

logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting PSIVI Auto-Reporter & Instruction Handler")
    
    # 1. Handle Instructions (Spawn Agents, etc.)
    instruction_agent = InstructionAgent()
    factory = AgentFactory()
    inst_count = instruction_agent.execute(factory=factory)
    logger.info(f"Executed {inst_count} instructions")
    
    # 2. Generate Reports (Based on Mesh State)
    # Note: ReportGeneratorAgent assumed to exist from previous context
    try:
        report_agent = ReportGeneratorAgent()
        # Mock instruction for report generation
        report_agent.execute({"goal": "Auto-generated mesh status report", "path": "auto"})
        logger.info("Report generation complete")
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
    
    logger.info("Auto-Reporter loop finished")

if __name__ == "__main__":
    main()
