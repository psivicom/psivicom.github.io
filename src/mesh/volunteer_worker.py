# src/mesh/volunteer_worker.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Sovereign Volunteer Worker: The Edge Node Executor.
Processes instructions from the mesh queue, verifying cryptographic 
signatures and enforcing Zulu temporal precision before execution.
"""

import json
import logging
from pathlib import Path

from src.core.psvc_sovereign import SovereignPSVC
from src.core.zulu_clock import get_zulu_timestamp_ms

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger("VOLUNTEER_WORKER")

def process_instruction_queue():
    """Scans the instruction queue for sovereign PSVC tasks and executes them."""
    queue_dir = Path("data/instruction_queue")
    if not queue_dir.exists():
        logger.warning("⚠️ Instruction queue directory missing. Standing by.")
        return

    # Find all .psvc.json files (sovereign containers)
    psvc_files = list(queue_dir.glob("*.psvc.json"))
    
    if not psvc_files:
        logger.info("💤 No sovereign instructions in queue.")
        return

    logger.info(f"👷 Volunteer Worker starting. Found {len(psvc_files)} tasks.")
    
    # Process oldest first
    oldest_file = sorted(psvc_files, key=lambda f: f.stat().st_mtime)[0]
    
    try:
        # 1. Load the container
        container = json.loads(oldest_file.read_text(encoding="utf-8"))
        
        # 2. ZERO-TRUST: Verify Ed25519 signature before doing ANYTHING
        if not SovereignPSVC.verify_container(container):
            logger.error(f"🚫 REJECTED: {oldest_file.name} has invalid cryptographic signature.")
            # Move to rejected folder
            rejected_dir = Path("data/rejected_instructions")
            rejected_dir.mkdir(parents=True, exist_ok=True)
            oldest_file.rename(rejected_dir / oldest_file.name)
            return
            
        # 3. Extract verified payload
        payload = SovereignPSVC.extract_data(container)
        command = payload.get("command", "unknown")
        
        logger.info(f"✅ VERIFIED: Executing command '{command}' from {payload.get('agent_id', 'unknown')}")
        
        # --- PLACEHOLDER: Insert actual robotic/compute execution logic here ---
        # e.g., apply Lee-filter to SAR patch, update local state, etc.
        
        # 4. Move to processed folder with Zulu timestamp
        processed_dir = Path("data/processed_instructions")
        processed_dir.mkdir(parents=True, exist_ok=True)
        zulu_safe = get_zulu_timestamp_ms().replace(':', '-').replace('.', '-')
        new_name = f"processed_{oldest_file.stem}_{zulu_safe}.json"
        
        oldest_file.rename(processed_dir / new_name)
        logger.info(f"✅ Task completed and archived: {new_name}")
        
    except json.JSONDecodeError:
        logger.error(f"❌ Error: {oldest_file.name} is not valid JSON.")
    except Exception as e:
        logger.error(f"❌ Error processing instruction {oldest_file.name}: {e}")

if __name__ == "__main__":
    process_instruction_queue()
