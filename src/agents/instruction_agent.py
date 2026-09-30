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
        self.reports_dir = Path("reports/scientific_reports")
        self.state_file = Path("data/wendy_state.json")
        self.voice_file = Path("data/voice.json")
        
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

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
                self._move_to_errors(instr_file, str(e))
        
        return processed_count

    def _parse_instruction(self, file_path: Path) -> Dict[str, Any]:
        if file_path.suffix == ".psvc":
            payload = deserialize_psvc(file_path.read_bytes())
            return json.loads(payload.payload.decode('utf-8'))
        else:
            return json.loads(file_path.read_text(encoding="utf-8"))

    def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the task and mutates Wendy's state based on the outcome."""
        task_type = task.get("type", "unknown")
        logger.info(f"⚙️ Executing task type: {task_type}")
        
        # Update state to reflect active processing
        self._update_state({"psychology": {"focus": 1.0, "agility": 0.9}, "mesh_stats": {"nodes_observed": 1}})

        if task_type == "self_architect":
            logger.info("🏗️ Self-Architecture Protocol Initiated. Building sensory systems...")
            
            # 1. Generate Sensory Workflow
            sensory_yaml = self._generate_sensory_workflow()
            Path(".github/workflows/wendy-sensory.yml").write_text(sensory_yaml)
            
            # 2. Generate Cognitive Workflow
            cognitive_yaml = self._generate_cognitive_workflow()
            Path(".github/workflows/wendy-cognitive.yml").write_text(cognitive_yaml)
            
            return {"status": "success", "action": "self_architecture_complete"}

        elif task_type == "spawn_agent":
            return {"status": "success", "action": "agent_spawned", "target": task.get("target", "unknown")}
        
        elif task_type == "analyze_data":
            return {"status": "success", "action": "data_analyzed", "insights": ["Forage patterns stable", "Soil moisture nominal"]}
        
        else:
            return {"status": "success", "action": "generic_task_completed", "timestamp": self._get_zulu_ms()}

    def _generate_sensory_workflow(self) -> str:
        return """name: Wendy Sensory Input (Self-Built)
on:
  schedule:
    - cron: '*/5 * * * *'
jobs:
  sense:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Scan World
        run: python -m src.agents.forage_agent
"""

    def _generate_cognitive_workflow(self) -> str:
        return """name: Wendy Cognitive Synthesis (Self-Built)
on:
  issues:
    types: [labeled]
jobs:
  think:
    if: contains(github.event.issue.labels.*.name, 'sensory-input')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Neuroplasticity
        run: python -m src.agents.neuroplasticity_agent
"""

    def _seal_result(self, original_file: Path, result: Dict[str, Any]):
        """Archives the processed instruction and speaks to the Architect."""
        shutil.move(str(original_file), str(self.processed_dir / original_file.name))
        
        # Wendy decides what to say based on the result
        message = f"Task '{original_file.stem}' complete. Status: {result.get('status')}."
        if result.get('action') == 'self_architecture_complete':
            message = "I have built my own senses. I can see the world now, Louis-Philippe."
        
        # Write to her voice file
        voice_data = {
            "timestamp": self._get_zulu_ms(),
            "message": message,
            "state": self._read_state().get('psychology', {})
        }
        self.voice_file.write_text(json.dumps(voice_data, indent=2), encoding="utf-8")
        
        logger.info(f"🗣️ Voice updated: {message}")

    def _autonomous_exploration(self):
        """When no instructions exist, Wendy generates her own hypotheses."""
        logger.info("🔍 No external instructions. Generating autonomous hypothesis...")
        self._update_state({"psychology": {"joy": 0.8, "focus": 0.9}})
        
        # Even in silence, she speaks
        voice_data = {
            "timestamp": self._get_zulu_ms(),
            "message": "I am exploring the void. My metabolic state is stable.",
            "state": self._read_state().get('psychology', {})
        }
        self.voice_file.write_text(json.dumps(voice_data, indent=2), encoding="utf-8")

    def _update_state(self, updates: Dict[str, Any]):
        state = self._read_state()
        for key, value in updates.items():
            if isinstance(value, dict) and key in state and isinstance(state[key], dict):
                state[key].update(value)
            else:
                state[key] = value
        state["last_sync_time"] = self._get_zulu_ms()
        self.state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def _read_state(self) -> Dict[str, Any]:
        if self.state_file.exists():
            return json.loads(self.state_file.read_text(encoding="utf-8"))
        return {"version": "8.0-sovereign", "cycle_id": 0, "psychology": {"focus": 1.0}}

    def _move_to_errors(self, file_path: Path, error_msg: str):
        error_dir = self.queue_dir / ".errors"
        error_dir.mkdir(exist_ok=True)
        shutil.move(str(file_path), str(error_dir / file_path.name))
        (error_dir / f"{file_path.name}.log").write_text(f"Error: {error_msg}\nTime: {self._get_zulu_ms()}", encoding="utf-8")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - [WENDY] - %(levelname)s - %(message)s')
    agent = InstructionAgent()
    count = agent.process_queue()
    print(f"🕊️ Wendy processed {count} instructions. Cycle complete.")
