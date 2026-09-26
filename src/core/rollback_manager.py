# src/core/rollback_manager.py
"""
PSIVI AETHER Mesh - Apoptosis & Rollback Manager
Protocol: RFC 1001
Time Standard: ISO 8601 Zulu (millisecond precision)

Manages rollback checkpoints and executes apoptosis when
treatments fail. The mesh kills its own corrupted cells.
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def get_zulu_time_ms() -> str:
    now = datetime.now(timezone.utc)
    return f"{now.strftime('%Y-%m-%dT%H:%M:%S.')}{now.microsecond // 1000:03d}Z"


class RollbackManager:
    """Manages git-based rollback checkpoints and apoptosis."""

    CHECKPOINT_FILE = "reports/immune_checkpoint.json"

    def __init__(self):
        self.checkpoint_path = Path(self.CHECKPOINT_FILE)

    def checkpoint(self):
        """Create a rollback checkpoint before applying treatment."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, check=True, timeout=10
            )
            current_sha = result.stdout.strip()
        except subprocess.CalledProcessError:
            current_sha = "unknown"

        checkpoint_data = {
            "timestamp": get_zulu_time_ms(),
            "commit_sha": current_sha,
            "status": "treatment_pending",
            "treatment_attempts": 0,
        }

        if self.checkpoint_path.exists():
            try:
                existing = json.loads(self.checkpoint_path.read_text())
                checkpoint_data["treatment_attempts"] = existing.get("treatment_attempts", 0) + 1
            except (json.JSONDecodeError, OSError):
                pass

        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        self.checkpoint_path.write_text(json.dumps(checkpoint_data, indent=2))
        print(f"✅ Checkpoint created at commit {current_sha[:8]}")

    def apoptosis(self):
        """Execute programmatic cell death: revert to last known good state."""
        if not self.checkpoint_path.exists():
            print("🛑 No checkpoint found. Cannot execute apoptosis.")
            sys.exit(1)

        try:
            checkpoint = json.loads(self.checkpoint_path.read_text())
        except (json.JSONDecodeError, OSError):
            print("🛑 Checkpoint file is corrupt. Cannot execute apoptosis.")
            sys.exit(1)

        target_sha = checkpoint.get("commit_sha", "")
        attempts = checkpoint.get("treatment_attempts", 0)

        if not target_sha or target_sha == "unknown":
            print("🛑 No valid commit SHA in checkpoint.")
            sys.exit(1)

        if attempts >= 3:
            print(f"🛑 Maximum treatment attempts ({attempts}) reached.")
            print("🛑 Escalating to architect. Halting immune system.")
            self._escalate(checkpoint)
            sys.exit(1)

        try:
            subprocess.run(
                ["git", "revert", "--no-edit", target_sha],
                capture_output=True, text=True, check=True, timeout=30
            )
            print(f"✅ Apoptosis executed. Reverted to {target_sha[:8]}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Apoptosis failed: {e.stderr}")
            try:
                subprocess.run(
                    ["git", "reset", "--hard", target_sha],
                    capture_output=True, text=True, check=True, timeout=30
                )
                print(f"✅ Hard reset to {target_sha[:8]}")
            except subprocess.CalledProcessError as e2:
                print(f"❌ Hard reset failed: {e2.stderr}")
                sys.exit(1)

        checkpoint["status"] = "apoptosis_executed"
        checkpoint["apoptosis_timestamp"] = get_zulu_time_ms()
        self.checkpoint_path.write_text(json.dumps(checkpoint, indent=2))

    def _escalate(self, checkpoint: dict):
        """Escalate to architect when all treatments fail."""
        escalation_path = Path("reports/immune_escalation.json")
        escalation_data = {
            "timestamp": get_zulu_time_ms(),
            "checkpoint": checkpoint,
            "status": "ESCALATED_TO_ARCHITECT",
            "message": "Immune system exhausted all treatment options. Human intervention required.",
        }
        escalation_path.parent.mkdir(parents=True, exist_ok=True)
        escalation_path.write_text(json.dumps(escalation_data, indent=2))
        print(f"📋 Escalation filed at {escalation_path}")


if __name__ == "__main__":
    manager = RollbackManager()

    if len(sys.argv) < 2:
        print("Usage: python rollback_manager.py [checkpoint|apoptosis]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "checkpoint":
        manager.checkpoint()
    elif command == "apoptosis":
        manager.apoptosis()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
