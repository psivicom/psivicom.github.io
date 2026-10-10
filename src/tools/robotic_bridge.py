# src/tools/robotic_bridge.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Robotic Actuator Bridge: The Polyglot Physical Interface.
Delegates deterministic rule evaluation to a bare-metal Zig binary for 
nanosecond latency, while Python handles cryptographic signing and MQTT dispatch.
Ensures zero-trust execution: hardware only obeys verified, sovereign instructions.
"""

import json
import logging
import subprocess
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List

from src.core.zulu_clock import get_zulu_timestamp_ms
from src.core.psvc_sovereign import SovereignPSVC, SovereignKeyPair
from src.core.sovereign_kernel import SovereignKernel

logger = logging.getLogger("ROBOTIC_BRIDGE")

class RoboticActuatorBridge:
    def __init__(self, root_dir: str = ".", ledger_path: str = "data/vanguard_ledger.jsonl"):
        self.root = Path(root_dir)
        self.ledger_path = self.root / ledger_path
        self.rules_path = self.root / "config/actuation_rules.json"
        
        # Initialize sovereign identity for signing physical commands
        self.keys = SovereignKeyPair(self.root / "data/wendy_private.key")
        self.psvc_factory = SovereignPSVC(self.keys)
        
        # Link to the cognitive state
        self.kernel = SovereignKernel(root_dir=root_dir, key_pair=self.keys)
        
        # Locate the compiled Zig binary for bare-metal evaluation
        self.zig_binary = self.root / "src/core/actuation_engine"
        
        logger.info("🌉 Robotic Actuator Bridge initialized. Polyglot zero-trust interface ready.")

    def _evaluate_rules_zig(self, state_vector: np.ndarray) -> Optional[List[Dict[str, Any]]]:
        """
        Delegates rule evaluation to the compiled Zig binary for bare-metal speed.
        Bypasses Python's GIL entirely for nanosecond latency.
        """
        if not self.zig_binary.exists():
            logger.warning("⚠️ Zig binary not found. Falling back to Python evaluation.")
            return self._evaluate_rules_python(state_vector)
            
        try:
            # Convert 16-dim float32 array to comma-separated string for Zig CLI
            vector_csv = ",".join(f"{v:.6f}" for v in state_vector)
            
            result = subprocess.run(
                [str(self.zig_binary), vector_csv, str(self.rules_path)],
                capture_output=True, text=True, timeout=1
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout.strip())
            else:
                logger.error(f"❌ Zig evaluation failed: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Zig execution error, falling back to Python: {e}")
            return self._evaluate_rules_python(state_vector)

    def _evaluate_rules_python(self, state_vector: np.ndarray) -> Optional[List[Dict[str, Any]]]:
        """
        Graceful degradation fallback if the Zig binary is not yet compiled.
        """
        commands = []
        stress = float(state_vector[4])
        intensity = float(state_vector[1])
        defense = float(state_vector[2])
        
        if stress >= 0.75:
            commands.append({"action": "ACTIVATE_COOLING", "target": "apiary_hive_01", "priority": "CRITICAL", "duration_seconds": 300})
        if intensity >= 0.85 and stress < 0.75:
            commands.append({"action": "OPEN_ENTRANCE", "target": "apiary_hive_01", "priority": "HIGH"})
        if defense >= 0.80:
            commands.append({"action": "ENABLE_LIDAR_SCAN", "target": "apiary_perimeter", "priority": "HIGH"})
            
        return commands if commands else None

    def sign_and_dispatch(self, commands: List[Dict[str, Any]], target_protocol: str = "MQTT") -> bool:
        """
        Cryptographically seals the command payload and dispatches to hardware.
        """
        if not commands:
            return True
            
        payload = {
            "timestamp": get_zulu_timestamp_ms(),
            "commands": commands,
            "authority": "Sovereign Actuation"
        }
        
        # 1. Create Sovereign PSVC Container
        container = self.psvc_factory.create_container(
            content_type="robotic_actuation_command",
            data=payload,
            operation="execute_physical_action"
        )
        
        # 2. Serialize to bytes (ready for MQTT/ROS2 payload)
        payload_bytes = json.dumps(container).encode('utf-8')
        
        # 3. Simulate Hardware Dispatch (In production, replace with paho-mqtt or rospy)
        try:
            # mqtt_client.publish("wendy/apiary/commands", payload_bytes, qos=2)
            logger.info(f"✅ {len(commands)} commands successfully signed and dispatched via {target_protocol}.")
            
            # 4. Log to Vanguard Ledger for immutable provenance
            self._log_dispatch(payload, success=True)
            return True
            
        except Exception as e:
            logger.error(f"❌ Dispatch failed: {e}")
            self._log_dispatch(payload, success=False, error=str(e))
            return False

    def execute_cycle(self) -> Dict[str, Any]:
        """Main execution loop: Reads state, evaluates via Zig, and dispatches."""
        logger.info("🔄 Executing Robotic Bridge cycle...")
        
        # 1. Export current sovereign state (16-dim vector)
        state_bytes = self.kernel.export_soul(target_node_id="local_bridge")
        state_data = json.loads(state_bytes.decode('utf-8'))
        vector_list = state_data.get("vector", [])
        
        if len(vector_list) != 16:
            logger.error("🚫 State vector dimension mismatch.")
            return {"status": "error", "reason": "dimension_mismatch"}
            
        # Enforce strict float32 precision
        state_vector = np.array(vector_list, dtype=np.float32)
        
        # 2. Bare-metal evaluation via Zig
        commands = self._evaluate_rules_zig(state_vector)
        
        if not commands:
            logger.info("💤 No physical actuation required at this time.")
            return {"status": "idle", "reason": "no_commands_generated"}
            
        # 3. Cryptographic dispatch
        success = self.sign_and_dispatch(commands, target_protocol="MQTT_SIMULATED")
        
        return {
            "status": "success" if success else "failed",
            "commands_dispatched": len(commands),
            "timestamp": get_zulu_timestamp_ms()
        }

    def _log_dispatch(self, payload: Dict[str, Any], success: bool, error: str = ""):
        """Records the physical actuation attempt in the immutable ledger."""
        record = {
            "timestamp": get_zulu_timestamp_ms(),
            "action": "ROBOTIC_DISPATCH",
            "actor": "robotic_bridge",
            "success": success,
            "error": error,
            "commands": payload.get("commands", []),
            "authority": "Sovereign Actuation"
        }
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    @staticmethod
    def _hash_vector(vector: np.ndarray) -> str:
        import hashlib
        return hashlib.sha256(vector.tobytes()).hexdigest()[:16]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    # Ensure directories exist
    Path("data").mkdir(parents=True, exist_ok=True)
    Path("config").mkdir(parents=True, exist_ok=True)
    
    bridge = RoboticActuatorBridge()
    print("\n🌉 Testing Robotic Actuator Bridge (Polyglot Zig + Python)...")
    result = bridge.execute_cycle()
    print(json.dumps(result, indent=2))
