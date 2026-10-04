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
        # Use the correct method name 'process_queue' to read the JSON files
        inst_count = instruction_agent.process_queue()
        logger.info(f"✅ Executed {inst_count} instruction(s).")
    except Exception as e:
        logger.error(f"❌ Instruction processing failed: {e}")
        inst_count = 0
    
    # 2. Generate Reports if New Instructions Were Found
    if inst_count > 0:
        logger.info("📊 Triggering report generation for updated mesh state...")
        try:
            report_agent = ReportGeneratorAgent()
            
            # Pass the instruction dictionary directly to the execute method
            report_agent.execute({
                "command": "request_report",
                "params": {
                    "topic": "Post-Instruction Status Refresh",
                    "format": "markdown"
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
