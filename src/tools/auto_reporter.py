# src/tools/auto_reporter.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# Bridge script for outside AI agents to drop instructions and trigger mesh automation

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.instruction_agent import InstructionAgent
from src.agents.report_generator_agent import ReportGeneratorAgent

logger = logging.getLogger(__name__)

def drop_instruction(goal: str, metadata: dict = None):
    """
    Outside AI agents call this function to drop an instruction file.
    The mesh agents will detect and process it automatically.
    """
    queue_dir = Path("data/instruction_queue")
    queue_dir.mkdir(parents=True, exist_ok=True)
    
    instruction = {
        "goal": goal,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "outside_ai",
        "metadata": metadata or {}
    }
    
    instruction_file = queue_dir / f"instruction_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
    with open(instruction_file, 'w') as f:
        json.dump(instruction, f, indent=2)
        
    logger.info(f"Instruction dropped: {instruction_file}")
    return instruction_file

def run_automation_loop():
    """
    Main loop for autonomous operation.
    Can be run as a daemon or triggered by GitHub Actions.
    """
    instruction_agent = InstructionAgent()
    report_agent = ReportGeneratorAgent()
    
    def process_instruction(inst):
        report_agent.execute(inst)
        return True
        
    count = instruction_agent.execute(trigger_callback=process_instruction)
    logger.info(f"Automation loop complete. Processed {count} instructions.")
    return count

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 1:
        goal = sys.argv[1]
        drop_instruction(goal)
    run_automation_loop()
