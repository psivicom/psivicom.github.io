# src/agents/instruction_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# Detects instruction files dropped by outside AI agents and queues them for execution

import sys
import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.base.base_agent import BaseAgent, AgentLayer
from src.core.psvc_reference import validate_file, read_file

logger = logging.getLogger(__name__)

class InstructionAgent(BaseAgent):
    """
    Monitors data/instruction_queue/ for new .psvc or .json instruction files.
    When detected, validates the instruction and triggers the ReportGeneratorAgent.
    """
    LAYER = AgentLayer.INGESTION

    def __init__(self, name: str = "instruction", queue_dir: str = "data/instruction_queue"):
        super().__init__(name, capabilities=["monitor", "validate", "trigger"])
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.processed_instructions = set()

    def scan_for_instructions(self) -> List[Dict[str, Any]]:
        instructions = []
        for file_path in self.queue_dir.glob("*"):
            if file_path.stem in self.processed_instructions:
                continue
            try:
                if file_path.suffix in ['.psvc', '.json']:
                    meta = {"path": str(file_path), "type": "instruction"}
                    if file_path.suffix == '.psvc':
                        validate_file(file_path)
                        meta["validated"] = True
                    instructions.append(meta)
                    self.processed_instructions.add(file_path.stem)
                    self.seal("instruction_detected", {"file": file_path.name})
            except Exception as e:
                logger.error(f"Failed to validate instruction {file_path.name}: {e}")
        return instructions

    def execute(self, trigger_callback: callable = None) -> int:
        logger.info(f"[{self.agent_id}] Scanning instruction queue...")
        instructions = self.scan_for_instructions()
        triggered = 0
        for inst in instructions:
            if trigger_callback:
                success = trigger_callback(inst)
                if success:
                    triggered += 1
                    self.seal("instruction_executed", {"file": inst["path"], "status": "success"})
        return triggered

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = InstructionAgent()
    count = agent.execute(lambda x: True)
    logger.info(f"Processed {count} instructions")
