#!/usr/bin/env python3
"""
wendy_core/orchestrator.py — Consumes pending_actions from .wendy_state.json
and dispatches to the WendyActuator. Unblocks the autonomous loop (R3).

R3 Fix (2026-11-25): The orchestrator's `trigger_self_heal` decision was
recorded in .wendy_state.json since 2026-11-24 but nothing consumed it.
This module reads pending_actions, dispatches to the actuator, and clears
the queue after processing.

Law XII (Compost Protocol) + Axiom 1 (Stigmergy_Graph).
License: EUPL-1.2
"""

import json
import logging
import os
import shutil
import subprocess
from datetime import datetime, timezone
from .wendy_actuator import WendyActuator

STATE_FILE = ".wendy_state.json"


def _zulu_now() -> str:
    """Returns current UTC time in Zulu format with millisecond precision."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class Orchestrator:
    """Consumes pending_actions from .wendy_state.json and dispatches to the actuator.

    This is the missing link between the orchestrator's decisions (recorded in
    .wendy_state.json) and the actuator's execution. Without this module, the
    autonomous loop is stuck: the orchestrator decides but nothing acts.
    """

    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.actuator = WendyActuator(repo_path=repo_path)
        self.state_path = os.path.join(repo_path, STATE_FILE)

    def load_state(self) -> dict:
        """Load .wendy_state.json."""
        if not os.path.exists(self.state_path):
            logging.warning(f"State file not found: {self.state_path}")
            return {}
        with open(self.state_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_state(self, state: dict) -> None:
        """Save .wendy_state.json (Zulu timestamp updated)."""
        state["last_heartbeat"] = _zulu_now()
        tmp_path = self.state_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        os.replace(tmp_path, self.state_path)
        logging.info(f"State saved to {self.state_path}")

    def process_pending_actions(self) -> list:
        """Process all pending_actions. Returns list of result dicts.

        Each result: {"action": str, "file": str, "status": str, ...}
        After processing, pending_actions is cleared in .wendy_state.json.
        """
        state = self.load_state()
        pending = state.get("pending_actions", [])
        results = []

        if not pending:
            logging.info("Orchestrator: no pending actions to process")
            state["orchestrator"] = {
                "last_run": _zulu_now(),
                "status": "idle",
                "details": "no pending actions"
            }
            self.save_state(state)
            return results

        logging.info(f"Orchestrator: processing {len(pending)} pending action(s)")

        for action in pending:
            action_type = action.get("type", "unknown")
            file_path = action.get("file", "")
            reason = action.get("reason", "unspecified")
            created = action.get("created", "")

            logging.info(f"  Processing: {action_type} for {file_path} (reason: {reason}, created: {created})")

            if action_type == "revert_zig":
                result = self._handle_revert_zig(file_path, reason)
            elif action_type == "revert_file":
                result = self._handle_revert_file(file_path, reason)
            else:
                logging.warning(f"  Unknown action type: {action_type}")
                result = {"action": action_type, "file": file_path, "status": "unknown_type"}

            results.append(result)
            logging.info(f"  Result: {json.dumps(result)}")

        # Clear pending_actions after processing
        state["pending_actions"] = []
        state["orchestrator"] = {
            "last_run": _zulu_now(),
            "status": "processed",
            "details": f"processed {len(results)} action(s)"
        }

        # Update ci_cd self_healed if we processed a revert
        if any(r.get("status", "").startswith("reverted") for r in results):
            ci_cd = state.get("workflows", {}).get("ci_cd", {})
            ci_cd["self_healed"] = True
            ci_cd["heal_timestamp"] = _zulu_now()
            state.setdefault("workflows", {})["ci_cd"] = ci_cd
            logging.info("Orchestrator: marked ci_cd.self_healed = true")

        self.save_state(state)
        return results

    def _handle_revert_zig(self, file_path: str, reason: str) -> dict:
        """Handle revert_zig action: restore hot_path.zig from .bak or git checkout."""
        # R4: Correct the path if it uses the old wrong path
        if file_path == "src/hot_path.zig":
            file_path = "wendy-cortex/src/hot_path.zig"
            logging.info(f"  R4: corrected path to {file_path}")

        full_path = os.path.join(self.repo_path, file_path)

        # Strategy 1: Restore from .bak if it exists
        bak_path = full_path + ".bak"
        if os.path.exists(bak_path):
            try:
                shutil.copy2(bak_path, full_path)
                logging.info(f"  Reverted {file_path} from .bak backup")
                return {
                    "action": "revert_zig",
                    "file": file_path,
                    "status": "reverted_from_bak",
                    "reason": reason,
                    "method": "bak_restore"
                }
            except Exception as e:
                logging.error(f"  .bak restore failed: {e}")
                # Fall through to git checkout

        # Strategy 2: git checkout HEAD -- file
        try:
            subprocess.run(
                ["git", "checkout", "HEAD", "--", file_path],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                text=True
            )
            logging.info(f"  Reverted {file_path} via git checkout")
            return {
                "action": "revert_zig",
                "file": file_path,
                "status": "reverted_git",
                "reason": reason,
                "method": "git_checkout"
            }
        except subprocess.CalledProcessError as e:
            logging.error(f"  git checkout failed: {e.stderr}")
            return {
                "action": "revert_zig",
                "file": file_path,
                "status": "failed",
                "reason": reason,
                "error": e.stderr.strip()
            }

    def _handle_revert_file(self, file_path: str, reason: str) -> dict:
        """Handle generic revert_file action via git checkout."""
        try:
            subprocess.run(
                ["git", "checkout", "HEAD", "--", file_path],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                text=True
            )
            logging.info(f"  Reverted {file_path} via git checkout")
            return {
                "action": "revert_file",
                "file": file_path,
                "status": "reverted_git",
                "reason": reason,
                "method": "git_checkout"
            }
        except subprocess.CalledProcessError as e:
            logging.error(f"  git checkout failed: {e.stderr}")
            return {
                "action": "revert_file",
                "file": file_path,
                "status": "failed",
                "reason": reason,
                "error": e.stderr.strip()
            }


def main():
    """Entry point: process all pending actions."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s.%(msecs)03d] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    logging.info("WENDY Orchestrator initialized. Processing pending actions...")
    orch = Orchestrator(repo_path=".")
    results = orch.process_pending_actions()
    logging.info(f"Orchestrator complete. {len(results)} action(s) processed.")
    for r in results:
        logging.info(f"  Result: {json.dumps(r)}")


if __name__ == "__main__":
    main()
