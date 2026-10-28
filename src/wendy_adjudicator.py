"""
WENDY v1.8 Adversarial Adjudicator
Prevents GLM self-reinforcing bias by enforcing strict, deterministic validation
against non-LLM ground truth (Zig/Go system state).
"""

import json
import hashlib
from typing import Any, Dict
from dataclasses import dataclass

@dataclass
class SystemState:
    """Immutable ground truth from the bare-metal/mesh layer."""
    zig_checksum_valid: bool
    go_sandbox_exit_code: int
    go_sandbox_stdout_hash: str
    sensor_data_present: bool

class WendyAdjudicator:
    def __init__(self):
        # We do not use an LLM here. Adjudication must be deterministic.
        pass

    def evaluate_ruling(self, glm_ruling: Dict[str, Any], actual_state: SystemState) -> Dict[str, Any]:
        """
        Evaluates a GLM's proposed ruling against hard system state.
        Prevents autoregressive echo by ignoring the GLM's self-justification.
        """
        ruling_action = glm_ruling.get("action", "")
        ruling_payload = glm_ruling.get("payload", {})
        ruling_claims_success = ruling_payload.get("success", False)

        # 1. Verify Cryptographic Integrity (Zig Layer)
        if ruling_action == "process_acoustic" and not actual_state.zig_checksum_valid:
            return self._reject_ruling(glm_ruling, "CRITICAL: Zig PSVC seal broken. GLM ruling ignored.")

        # 2. Verify Execution Integrity (Go Sandbox Layer)
        if ruling_action == "execute_tool":
            if actual_state.go_sandbox_exit_code != 0:
                return self._reject_ruling(
                    glm_ruling, 
                    f"CRITICAL: Sandbox execution failed (exit code {actual_state.go_sandbox_exit_code}). GLM claimed success."
                )
            
            # 3. Verify Output Integrity (Prevent GLM from hallucinating tool output)
            claimed_output_hash = ruling_payload.get("output_hash", "")
            if claimed_output_hash and claimed_output_hash != actual_state.go_sandbox_stdout_hash:
                return self._reject_ruling(
                    glm_ruling,
                    "CRITICAL: GLM hallucinated tool output. Hash mismatch between claimed and actual sandbox stdout."
                )

        # 4. Verify Data Grounding
        if ruling_action == "analyze_hive" and not actual_state.sensor_data_present:
            return self._reject_ruling(glm_ruling, "CRITICAL: No sensor data present. GLM ruling is ungrounded hallucination.")

        # If all deterministic checks pass, the ruling is valid.
        return {
            "status": "ACCEPTED",
            "ruling": glm_ruling,
            "adjudicator_note": "Ruling validated against deterministic system state."
        }

    def _reject_ruling(self, glm_ruling: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """
        Forces a hard fallback when the GLM attempts to validate a false state.
        """
        return {
            "status": "REJECTED",
            "original_ruling": glm_ruling,
            "reason": reason,
            "fallback_action": "enter_safe_mode",
            "adjudicator_note": "Autoregressive bias detected and neutralized."
        }


if __name__ == "__main__":
    # Integration test
    adjudicator = WendyAdjudicator()

    flawed_glm_ruling = {
        "action": "execute_tool",
        "payload": {
            "tool": "varroa_counter",
            "success": True,
            "output_hash": "a1b2c3d4e5f6"
        },
        "confidence": 0.95
    }

    actual_system_state = SystemState(
        zig_checksum_valid=True,
        go_sandbox_exit_code=1,
        go_sandbox_stdout_hash="9f8e7d6c5b4a",
        sensor_data_present=True
    )

    result = adjudicator.evaluate_ruling(flawed_glm_ruling, actual_system_state)
    print(json.dumps(result, indent=2))
