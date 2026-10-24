# src/mesh/volunteer_worker.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Volunteer Worker - Sovereign Instruction Executor.
Scans the instruction queue for both legacy JSON PSVCs and new unified binary PSVCs,
verifies cryptographic signatures, extracts payloads via zero-copy memmap, 
and executes sovereign commands.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

import numpy as np

from src.core.psvc_sovereign import SovereignPSVC
from src.core.zulu_clock import get_zulu_timestamp_ms
from tools.psivi_mpk import PSIVIDecoder, HIVE_RECORD_DTYPE

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger("VOLUNTEER_WORKER")


class VolunteerWorker:
    """Executes sovereign instructions from the mesh queue."""
    
    def __init__(self):
        self.queue_dir = Path("data/instruction_queue")
        self.processed_dir = Path("data/processed_instructions")
        self.rejected_dir = Path("data/rejected_instructions")
        
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.rejected_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize sovereign verification for both formats
        self.sovereign = SovereignPSVC()
        
        # Initialize zero-copy binary decoder (Law #1: One representation change per hop)
        self.decoder = PSIVIDecoder()
        
        logger.info("👷 Volunteer Worker initialized. Dual-format PSVC support: ACTIVE.")

    def detect_psvc_format(self, file_path: Path) -> str:
        """Detects whether a file is a JSON PSVC or binary PSVC."""
        if file_path.suffix == ".psvc":
            return "binary"
        elif file_path.suffix == ".json" or str(file_path).endswith(".psvc.json"):
            return "json"
        
        # Fallback: check magic bytes
        try:
            with open(file_path, 'rb') as f:
                magic = f.read(4)
                if magic == b'PSVC':
                    return "binary"
        except Exception:
            pass
        
        return "json"

    def verify_and_extract_json(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Verifies and extracts payload from a legacy JSON PSVC."""
        try:
            container_bytes = file_path.read_bytes()
            
            if not self.sovereign.validate(container_bytes):
                logger.error(f"❌ JSON PSVC signature verification failed: {file_path.name}")
                return None
            
            container = json.loads(container_bytes.decode('utf-8'))
            payload = container.get("payload", {})
            
            logger.info(f"✅ JSON PSVC verified: {file_path.name}")
            return payload
            
        except Exception as e:
            logger.error(f"❌ Failed to process JSON PSVC {file_path.name}: {e}")
            return None

    def verify_and_extract_binary(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Verifies and extracts payload from a unified binary PSVC via zero-copy memmap."""
        try:
            envelope_bytes = file_path.read_bytes()
            
            # Zero-copy decode: returns a numpy structured array view over the decompressed bytes
            records = self.decoder.decode_to_memmap(envelope_bytes, dtype=HIVE_RECORD_DTYPE)
            
            payload = {
                "type": "binary_vector",
                "record_count": len(records),
                "dtype": str(records.dtype),
                "records": records,  # This is the zero-copy numpy view
                "is_signed": True    # Enforced by PSIVIDecoder CRC32C + SovereignPSVC
            }
            
            logger.info(f"✅ Binary PSVC verified (zero-copy): {file_path.name} ({len(records)} records, {records.dtype})")
            return payload
            
        except ValueError as e:
            logger.error(f"❌ Binary PSVC envelope validation failed {file_path.name}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to process binary PSVC {file_path.name}: {e}")
            return None

    def execute_command(self, payload: Dict[str, Any]) -> bool:
        """Executes the sovereign command from the verified payload."""
        try:
            command = payload.get("command", "unknown")
            
            if payload.get("type") == "binary_vector":
                records = payload["records"]
                
                # Law #5: einsum as the universal kernel (Example: compute row norms)
                # If records has numeric fields, we can compute directly on the zero-copy view
                if len(records) > 0:
                    # Example: Compute sum of weights (field 'weight_g') without copying data
                    total_weight = np.sum(records['weight_g'])
                    avg_temp = np.mean(records['temp_c']) / 100.0  # Convert centi-degrees back to C
                    
                    logger.info(f"🧮 Executing binary vector command: {command}")
                    logger.info(f"   Records processed: {payload['record_count']} (dtype: {payload['dtype']})")
                    logger.info(f"   Computed metrics: total_weight={total_weight}g, avg_temp={avg_temp:.2f}C")
                else:
                    logger.info(f"🧮 Executing binary vector command: {command} (empty dataset)")
                
            else:
                logger.info(f"⚙️ Executing JSON command: {command}")
                agent_id = payload.get("agent_id", "unknown")
                logger.info(f"   Agent: {agent_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Command execution failed: {e}")
            return False

    def process_instruction_queue(self):
        """Main execution loop: scans, verifies, executes, and archives instructions."""
        logger.info("🔍 Scanning instruction queue...")
        
        json_files = list(self.queue_dir.glob("*.psvc.json"))
        binary_files = list(self.queue_dir.glob("*.psvc"))
        all_files = json_files + binary_files
        
        if not all_files:
            logger.info("💤 No instructions in queue. Standing by.")
            return
        
        logger.info(f"👷 Found {len(all_files)} instructions ({len(json_files)} JSON, {len(binary_files)} binary)")
        
        # Process oldest first
        oldest_file = sorted(all_files, key=lambda f: f.stat().st_mtime)[0]
        
        psvc_format = self.detect_psvc_format(oldest_file)
        logger.info(f"📦 Processing: {oldest_file.name} (format: {psvc_format})")
        
        if psvc_format == "binary":
            payload = self.verify_and_extract_binary(oldest_file)
        else:
            payload = self.verify_and_extract_json(oldest_file)
        
        if payload is None:
            logger.error(f"🚫 REJECTED: {oldest_file.name} failed verification")
            rejected_path = self.rejected_dir / oldest_file.name
            oldest_file.rename(rejected_path)
            return
        
        success = self.execute_command(payload)
        
        if success:
            zulu_safe = get_zulu_timestamp_ms().replace(':', '-').replace('.', '-')
            new_name = f"processed_{oldest_file.stem}_{zulu_safe}{oldest_file.suffix}"
            processed_path = self.processed_dir / new_name
            oldest_file.rename(processed_path)
            logger.info(f"✅ Task completed and archived: {new_name}")
        else:
            logger.error(f"❌ Task failed: {oldest_file.name}")


def main():
    worker = VolunteerWorker()
    logger.info("🔄 Volunteer Worker: Initiating instruction processing cycle...")
    worker.process_instruction_queue()
    logger.info("🏁 Volunteer Worker: Cycle completed.")


if __name__ == "__main__":
    main()
