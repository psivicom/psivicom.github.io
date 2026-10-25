# src/agents/instruction_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Instruction Agent - Sovereign Queue Processor.
Scans the instruction queue, validates PSVC magic headers, processes valid 
instructions, and safely quarantines corrupted or legacy files.
"""

import json
import logging
import shutil
from pathlib import Path
from typing import List, Dict, Any

from src.core.zulu_clock import get_zulu_timestamp_ms

logger = logging.getLogger("InstructionAgent")

class InstructionAgent:
    """Executes sovereign instructions from the mesh queue."""
    
    def __init__(self):
        self.queue_dir = Path("data/instruction_queue")
        self.processed_dir = Path("data/processed_instructions")
        self.rejected_dir = Path("data/rejected_instructions")
        
        # Ensure directories exist
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.rejected_dir.mkdir(parents=True, exist_ok=True)

    def process_queue(self) -> int:
        """
        Scans the instruction queue, processes valid instructions,
        and moves invalid/corrupted files to the rejected directory.
        """
        inst_count = 0
        
        # Get all .psvc and .json files
        files = list(self.queue_dir.glob("*.psvc")) + list(self.queue_dir.glob("*.json"))
        
        # Sort by modification time (oldest first)
        files.sort(key=lambda f: f.stat().st_mtime)
        
        for file_path in files:
            try:
                if self._is_valid_psvc(file_path):
                    self._process_instruction(file_path)
                    inst_count += 1
                else:
                    self._reject_instruction(file_path, "Invalid or truncated PSVC header")
            except Exception as e:
                logger.error(f"❌ Failed to process {file_path.name}: {e}")
                self._reject_instruction(file_path, str(e))
                
        return inst_count

    def _is_valid_psvc(self, file_path: Path) -> bool:
        """
        Checks if a .psvc file has the valid 'PSVC' magic header.
        JSON files are bypassed for legacy compatibility.
        """
        if file_path.suffix == ".json":
            return True 
        
        try:
            with open(file_path, 'rb') as f:
                magic = f.read(4)
                return magic == b'PSVC'
        except Exception:
            return False

    def _process_instruction(self, file_path: Path):
        """Processes a valid instruction and moves it to the processed directory."""
        logger.info(f"📥 Processing instruction: {file_path.name}")
        
        # TODO: Insert actual instruction execution logic here
        # e.g., factory.spawn_agent(payload)
        
        # Archive with Zulu timestamp
        zulu_safe = get_zulu_timestamp_ms().replace(':', '-').replace('.', '-')
        new_name = f"processed_{file_path.stem}_{zulu_safe}{file_path.suffix}"
        processed_path = self.processed_dir / new_name
        
        shutil.move(str(file_path), str(processed_path))
        logger.info(f"✅ Successfully processed and archived: {new_name}")

    def _reject_instruction(self, file_path: Path, reason: str):
        """Moves an invalid instruction to the rejected directory to prevent infinite loops."""
        logger.error(f"❌ Failed to process {file_path.name}: {reason}")
        rejected_path = self.rejected_dir / file_path.name
        
        # Handle name collisions in rejected dir
        counter = 1
        while rejected_path.exists():
            rejected_path = self.rejected_dir / f"{file_path.stem}_rej{counter}{file_path.suffix}"
            counter += 1
            
        shutil.move(str(file_path), str(rejected_path))
        logger.info(f"🚫 Moved to rejected quarantine: {rejected_path.name}")
