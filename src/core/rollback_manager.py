# src/core/rollback_manager.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
PSIVI AETHER Mesh - Apoptosis & Rollback Manager
Protocol: RFC 1001 | Time Standard: Zulu (millisecond precision)

Manages rollback checkpoints and executes apoptosis when treatments fail. 
Combines Git-based code reversion with runtime state file restoration.
The mesh kills its own corrupted cells without crashing the host node.
"""

import json
import logging
import shutil
import subprocess
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

from src.core.zulu_clock import get_zulu_timestamp_ms

logger = logging.getLogger("ROLLBACK_MANAGER")

class RollbackManager:
    """Manages git-based and state-based rollback checkpoints and apoptosis."""

    CHECKPOINT_DIR = "data/checkpoints"
    CHECKPOINT_META = "data/checkpoints/immune_checkpoint.json"
    CRITICAL_STATE_FILES = [
        "src/wendy_metabolism.json",
        "data/mesh_weights.json",
        "data/void_metrics.json"
    ]

    def __init__(self, root_dir: str = ".", ledger_path: str = "data/vanguard_ledger.jsonl"):
        self.root = Path(root_dir)
        self.checkpoint_dir = self.root / self.CHECKPOINT_DIR
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.ledger_path = self.root / ledger_path
        self.checkpoint_meta_path = self.root / self.CHECKPOINT_META

    def checkpoint(self, reason: str = "treatment_pending") -> bool:
        """Create a comprehensive rollback checkpoint (Git SHA + State Files) before applying treatment."""
        zulu_now = get_zulu_timestamp_ms()
        
        # 1. Get Git SHA
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, check=True, timeout=10, cwd=str(self.root)
            )
            current_sha = result.stdout.strip()
        except subprocess.CalledProcessError:
            current_sha = "unknown"
            logger.warning("⚠️ Could not determine Git SHA. Proceeding with state-only checkpoint.")

        # 2. Snapshot Critical State Files
        state_hashes = {}
        chkpt_folder = self.checkpoint_dir / f"chkpt_{zulu_now.replace(':', '-').replace('.', '-')}"
        chkpt_folder.mkdir(parents=True, exist_ok=True)
        
        for rel_path in self.CRITICAL_STATE_FILES:
            src_file = self.root / rel_path
            if src_file.exists():
                dest_file = chkpt_folder / rel_path.replace('/', '_')
                shutil.copy2(src_file, dest_file)
                with open(src_file, 'rb') as f:
                    state_hashes[rel_path] = hashlib.sha256(f.read()).hexdigest()[:16]

        # 3. Update Checkpoint Metadata
        attempts = 0
        if self.checkpoint_meta_path.exists():
            try:
                existing = json.loads(self.checkpoint_meta_path.read_text(encoding='utf-8'))
                attempts = existing.get("treatment_attempts", 0) + 1
            except (json.JSONDecodeError, OSError):
                pass

        checkpoint_data = {
            "timestamp": zulu_now,
            "commit_sha": current_sha,
            "checkpoint_folder": str(chkpt_folder.name),
            "status": reason,
            "treatment_attempts": attempts,
            "state_hashes": state_hashes
        }

        self.checkpoint_meta_path.write_text(json.dumps(checkpoint_data, indent=2), encoding='utf-8')
        logger.info(f"✅ Checkpoint created at commit {current_sha[:8] if current_sha != 'unknown' else 'unknown'}. Attempts: {attempts}")
        return True

    def apoptosis(self, anomaly_type: str, context: Dict[str, Any]) -> bool:
        """
        Execute programmatic cell death: revert code and state to last known good state.
        Returns True on success, False on failure (does NOT sys.exit, allowing graceful node recovery).
        """
        if not self.checkpoint_meta_path.exists():
            logger.error("🛑 No checkpoint found. Cannot execute apoptosis.")
            self._log_to_vanguard(anomaly_type, context, success=False, reason="no_checkpoint")
            return False

        try:
            checkpoint = json.loads(self.checkpoint_meta_path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            logger.error("🛑 Checkpoint file is corrupt. Cannot execute apoptosis.")
            self._log_to_vanguard(anomaly_type, context, success=False, reason="corrupt_checkpoint")
            return False

        target_sha = checkpoint.get("commit_sha", "")
        attempts = checkpoint.get("treatment_attempts", 0)
        chkpt_folder = self.checkpoint_dir / checkpoint.get("checkpoint_folder", "")

        if attempts >= 3:
            logger.error(f"🛑 Maximum treatment attempts ({attempts}) reached. Escalating to architect.")
            self._escalate(checkpoint, anomaly_type)
            self._log_to_vanguard(anomaly_type, context, success=False, reason="max_attempts_reached")
            return False

        success = True
        
        # 1. Attempt Git Revert/Reset (Code Apoptosis)
        if target_sha and target_sha != "unknown":
            try:
                subprocess.run(
                    ["git", "reset", "--hard", target_sha],
                    capture_output=True, text=True, check=True, timeout=30, cwd=str(self.root)
                )
                logger.info(f"✅ Code apoptosis executed. Hard reset to {target_sha[:8]}")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Git apoptosis failed: {e.stderr}")
                success = False

        # 2. Restore State Files (State Apoptosis)
        if chkpt_folder.exists():
            for rel_path in self.CRITICAL_STATE_FILES:
                dest_file = chkpt_folder / rel_path.replace('/', '_')
                src_file = self.root / rel_path
                if dest_file.exists():
                    shutil.copy2(dest_file, src_file)
                    logger.info(f"🔄 State restored: {rel_path}")
        else:
            logger.warning("⚠️ Checkpoint folder missing. State files not restored.")
            success = False

        # 3. Update Metadata
        checkpoint["status"] = "apoptosis_executed" if success else "apoptosis_failed"
        checkpoint["apoptosis_timestamp"] = get_zulu_timestamp_ms()
        self.checkpoint_meta_path.write_text(json.dumps(checkpoint, indent=2), encoding='utf-8')
        
        self._log_to_vanguard(anomaly_type, context, success=success)
        return success

    def _log_to_vanguard(self, anomaly_type: str, context: Dict[str, Any], success: bool, reason: str = "executed"):
        """Records the immune response in the immutable ledger."""
        record = {
            "timestamp": get_zulu_timestamp_ms(),
            "action": "IMMUNE_APOPTOSIS",
            "actor": "rollback_manager",
            "anomaly_type": anomaly_type,
            "success": success,
            "reason": reason,
            "context": context,
            "authority": "Automated Self-Healing"
        }
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def _escalate(self, checkpoint: dict, anomaly_type: str):
        """Escalate to architect when all treatments fail."""
        escalation_path = self.root / "reports/immune_escalation.json"
        escalation_data = {
            "timestamp": get_zulu_timestamp_ms(),
            "anomaly_type": anomaly_type,
            "checkpoint": checkpoint,
            "status": "ESCALATED_TO_ARCHITECT",
            "message": "Immune system exhausted all treatment options. Human intervention required.",
        }
        escalation_path.parent.mkdir(parents=True, exist_ok=True)
        escalation_path.write_text(json.dumps(escalation_data, indent=2), encoding='utf-8')
        logger.critical(f"📋 ESCALATION FILED at {escalation_path}")


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    manager = RollbackManager()

    if len(sys.argv) < 2:
        print("Usage: python rollback_manager.py [checkpoint|apoptosis]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "checkpoint":
        manager.checkpoint()
    elif command == "apoptosis":
        # Mock context for CLI testing
        manager.apoptosis("CLI_TEST", {"test": True})
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
