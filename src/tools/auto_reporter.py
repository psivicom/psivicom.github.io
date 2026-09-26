# src/tools/auto_reporter.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import logging
import sys
from pathlib import Path

from src.agents.instruction_agent import InstructionAgent
from src.agents.agent_factory import AgentFactory
from src.agents.report_generator_agent import ReportGeneratorAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("AutoReporter")

def main():
    logger.info("🚀 Starting PSIVI Mesh Automation Loop")
    
    # 1. Scan and Process Instructions
    logger.info("📥 Scanning instruction queue...")
    instruction_agent = InstructionAgent()
    factory = AgentFactory()
    
    try:
        inst_count = instruction_agent.execute(factory=factory)
        logger.info(f"✅ Executed {inst_count} instruction(s).")
    except Exception as e:
        logger.error(f"❌ Instruction processing failed: {e}")
        inst_count = 0
    
    # 2. Generate Reports if New Instructions Were Found OR Always Check State?
    # Strategy: If instructions were processed, regenerate report to reflect changes.
    # Also, if specific 'request_report' commands were in the queue, they are handled inside 
    # the loop if we pass them correctly. 
    
    # Note: The current InstructionAgent only handles 'spawn_agent'. 
    # We need to ensure 'request_report' is also routed. 
    # For simplicity in this iteration, we assume any activity triggers a status update.
    
    if inst_count > 0:
        logger.info("📊 Triggering report generation for updated mesh state...")
        try:
            report_agent = ReportGeneratorAgent()
            # Construct a generic instruction to force a refresh
            # In a more advanced version, we'd parse the specific command from the queue here
            report_agent.execute({
                "command": "request_report",
                "params": {
                    "topic": "Post-Instruction Status Refresh",
                    "format": "json"
                },
                "path": "internal_trigger"
            })
            logger.info("✅ Report generation complete.")
        except Exception as e:
            logger.error(f"❌ Report generation failed: {e}")
    else:
        logger.info("ℹ️ No new instructions. Mesh state unchanged.")
    
    logger.info("🏁 Automation loop finished successfully.")

if __name__ == "__main__":
    main()
