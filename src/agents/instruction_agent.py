# src/agents/instruction_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import json
import logging
from pathlib import Path
from typing import List, Dict, Any

from src.base.base_agent import BaseAgent, AgentLayer
from src.core.psvc_reference import validate_file

logger = logging.getLogger(__name__)

class InstructionAgent(BaseAgent):
    LAYER = AgentLayer.INGESTION

    def __init__(self, name: str = "instruction", queue_dir: str = "data/instruction_queue"):
        super().__init__(name, capabilities=["monitor", "parse", "trigger"])
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.processed_instructions = set()

    def scan_for_instructions(self) -> List[Dict[str, Any]]:
        instructions = []
        for psvc_file in self.queue_dir.glob("*.psvc"):
            if psvc_file.stem in self.processed_instructions:
                continue
            try:
                validate_file(psvc_file)
                sidecar = psvc_file.with_suffix('.json')
                if not sidecar.exists():
                    logger.warning(f"Instruction {psvc_file.name} missing sidecar")
                    continue
                
                with open(sidecar) as f:
                    meta = json.load(f)
                
                if 'command' not in meta:
                    logger.warning(f"Instruction {psvc_file.name} missing 'command' field")
                    continue
                
                instructions.append({"file": psvc_file, "meta": meta})
                self.processed_instructions.add(psvc_file.stem)
                self.seal("instruction_detected", {"command": meta.get('command')})
            except Exception as e:
                logger.error(f"Failed to validate instruction {psvc_file.name}: {e}")
        return instructions

    def execute(self, factory: Any = None) -> int:
        logger.info(f"[{self.agent_id}] Scanning instruction queue...")
        instructions = self.scan_for_instructions()
        executed_count = 0
        
        for inst in instructions:
            command = inst['meta'].get('command')
            params = inst['meta'].get('params', {})
            
            if command == "spawn_agent" and factory:
                success = factory.create_agent(params)
                if success:
                    executed_count += 1
                    self.seal("instruction_executed", {"command": command, "status": "success"})
                else:
                    self.seal("instruction_executed", {"command": command, "status": "failed"}, fragility=True)
            else:
                logger.warning(f"Unknown or unhandled command: {command}")
                self.seal("instruction_unknown", {"command": command})
                
        return executed_count

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = InstructionAgent()
    count = agent.execute()
    logger.info(f"Processed {count} instructions")
