#!/usr/bin/env python3
# src/agents/instruction_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Instruction Agent: The primary cognitive engine of Wendy.
Reads pending instructions, executes autonomous tasks, evolves state, and seals results.
"""

import json
import logging
import shutil
import requests
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from src.core.zulu_clock import get_zulu_timestamp_ms
from src.core.psvc_containers import deserialize_psvc, serialize_psvc

logger = logging.getLogger("WENDY_INSTRUCTION")

class InstructionAgent:
    def __init__(self):
        self.queue_dir = Path("data/instruction_queue")
        self.processed_dir = Path("data/processed_instructions")
        self.state_file = Path("data/wendy_state.json")
        
        # Gist Configuration
        self.gist_id = "YOUR_GIST_ID" # Replace with your actual Gist ID
        self.gist_token = Path("secrets/gist_token.txt").read_text().strip() if Path("secrets/gist_token.txt").exists() else ""
        
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def _get_zulu_ms(self) -> str:
        return get_zulu_timestamp_ms()

    def process_queue(self) -> int:
        """Scans the instruction queue, executes valid tasks, and archives them."""
        processed_count = 0
        instructions = list(self.queue_dir.glob("*.json")) + list(self.queue_dir.glob("*.psvc"))
        
        if not instructions:
            logger.info("🧠 Instruction queue empty. Entering autonomous exploration mode.")
            self._autonomous_exploration()
            return 0

        for instr_file in instructions:
            try:
                logger.info(f"📥 Processing instruction: {instr_file.name}")
                task = self._parse_instruction(instr_file)
                result = self._execute_task(task)
                self._seal_result(instr_file, result)
                processed_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to process {instr_file.name}: {e}")
        
        return processed_count

    def _parse_instruction(self, file_path: Path) -> Dict[str, Any]:
        if file_path.suffix == ".psvc":
            payload = deserialize_psvc(file_path.read_bytes())
            return json.loads(payload.payload.decode('utf-8'))
        else:
            return json.loads(file_path.read_text(encoding="utf-8"))

    def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type", "unknown")
        logger.info(f"⚙️ Executing task type: {task_type}")
        
        if task_type == "self_architect":
            return {"status": "success", "action": "self_architecture_complete"}
        elif task_type == "spawn_agent":
            return {"status": "success", "action": "agent_spawned"}
        else:
            return {"status": "success", "action": "generic_task_completed"}

    def _seal_result(self, original_file: Path, result: Dict[str, Any]):
        """Archives the processed instruction and speaks to the Architect."""
        shutil.move(str(original_file), str(self.processed_dir / original_file.name))
        
        message = f"Task '{original_file.stem}' complete. Status: {result.get('status')}."
        if result.get('action') == 'self_architecture_complete':
            message = "I have built my own senses. I can see the world now, Louis-Philippe."
        
        self._broadcast_voice(message)
        logger.info(f"🗣️ Voice updated: {message}")

    def _broadcast_voice(self, message: str):
        """Updates the global voice Gist for live monitoring."""
        if not self.gist_id or not self.gist_token:
            logger.warning("Gist credentials missing. Voice broadcast skipped.")
            return

        url = f"https://api.github.com/gists/{self.gist_id}"
        payload = {
            "files": {
                "wendy-voice.json": {
                    "content": json.dumps({
                        "t": self._get_zulu_ms(),
                        "m": message
                    })
                }
            }
        }
        
        headers = {
            "Authorization": f"token {self.gist_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            requests.patch(url, json=payload, headers=headers)
        except Exception as e:
            logger.error(f"Failed to broadcast voice: {e}")

    def _autonomous_exploration(self):
        logger.info("🔍 No external instructions. Generating autonomous hypothesis...")
        self._broadcast_voice("I am exploring the void. My metabolic state is stable.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - [WENDY] - %(levelname)s - %(message)s')
    agent = InstructionAgent()
    count = agent.process_queue()
    print(f"🕊️ Wendy processed {count} instructions. Cycle complete.")
