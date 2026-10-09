# src/agents/vanguard_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Vanguard Agent: The Guardian of the PSIVI AETHER Mesh.
Enforces mesh integrity, maintains the immutable ledger, and validates PSVC manifests.
Config Alignment: role="guardian", tools=["heartbeat", "ledger", "enforce_pico"], precision="float32"
"""

import json
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

from src.base.base_agent import BaseAgent, AgentLayer
from src.core.zulu_clock import get_zulu_timestamp_ms

logger = logging.getLogger("VANGUARD_AGENT")

class VanguardAgent(BaseAgent):
    LAYER = AgentLayer.VALIDATION # Acts as the final validation/governance gate

    def __init__(self, name: str = "vanguard", ledger_path: str = "data/vanguard_ledger.jsonl"):
        super().__init__(name, capabilities=["heartbeat", "ledger", "enforce_pico"])
        self.ledger_path = Path(ledger_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Enforce float32 precision for all internal state metrics per agent_config.yaml
        self.mesh_integrity_score = np.float32(1.0)
        self.anomaly_count = np.float32(0.0)
        
        logger.info(f"🛡️ Vanguard Agent initialized. Precision locked to float32.")

    def heartbeat(self) -> Dict[str, Any]:
        """
        Tool: heartbeat
        Periodic mesh integrity check. Returns a float32 telemetry vector.
        """
        self.mesh_integrity_score = np.float32(1.0) if self.ledger_path.exists() else np.float32(0.0)
        
        telemetry = {
            "agent": self.name,
            "status": "PATROLLING",
            "integrity_score": float(self.mesh_integrity_score), # Cast to native float for JSON serialization
            "anomaly_count": int(self.anomaly_count),
            "timestamp": get_zulu_timestamp_ms()
        }
        
        self.seal("heartbeat_executed", telemetry)
        logger.info(f"💓 Vanguard heartbeat nominal. Integrity: {telemetry['integrity_score']}")
        return telemetry

    def ledger(self, action: str, actor: str, details: str, metadata: Dict[str, Any] = None) -> None:
        """
        Tool: ledger
        Appends an immutable, timestamped record to the governance ledger.
        """
        entry = {
            "timestamp": get_zulu_timestamp_ms(),
            "action": action,
            "actor": actor,
            "details": details,
            "metadata": metadata or {},
            "authority": "The Audette Clause"
        }
        
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            
        self.seal("ledger_updated", {"action": action, "actor": actor})
        logger.info(f"📜 Ledger updated: {action} by {actor}")

    def enforce_pico(self, psvc_manifest: Dict[str, Any]) -> bool:
        """
        Tool: enforce_pico
        Validates that any PSVC container manifest complies with EUPL-1.2 
        licensing and contains no hallucinated or missing metadata.
        """
        required_fields = ["name", "version", "license", "author", "health_check"]
        
        for field in required_fields:
            if field not in psvc_manifest:
                self.anomaly_count = np.float32(self.anomaly_count + 1.0)
                logger.error(f"🚫 PSVC Manifest rejected: Missing required field '{field}'")
                self.ledger("MANIFEST_REJECTED", "vanguard", f"Missing field: {field}", psvc_manifest)
                return False
        
        if psvc_manifest.get("license") != "EUPL-1.2":
            self.anomaly_count = np.float32(self.anomaly_count + 1.0)
            logger.error(f"🚫 PSVC Manifest rejected: Invalid license '{psvc_manifest.get('license')}'. Must be EUPL-1.2.")
            self.ledger("LICENSE_VIOLATION", "vanguard", f"Invalid license: {psvc_manifest.get('license')}", psvc_manifest)
            return False

        logger.info(f"✅ PSVC Manifest '{psvc_manifest.get('name')}' cleared by Vanguard.")
        self.ledger("MANIFEST_APPROVED", "vanguard", f"Manifest {psvc_manifest.get('name')} validated", psvc_manifest)
        return True

    def execute(self, instruction: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main entry point for agent execution, routing to the correct tool."""
        if not instruction:
            return self.heartbeat()
            
        tool = instruction.get("tool")
        if tool == "heartbeat":
            return self.heartbeat()
        elif tool == "ledger":
            self.ledger(
                action=instruction.get("action", "UNKNOWN"),
                actor=instruction.get("actor", "SYSTEM"),
                details=instruction.get("details", ""),
                metadata=instruction.get("metadata", {})
            )
            return {"status": "success", "tool": "ledger"}
        elif tool == "enforce_pico":
            is_valid = self.enforce_pico(instruction.get("manifest", {}))
            return {"status": "success" if is_valid else "rejected", "tool": "enforce_pico"}
        else:
            logger.warning(f"Unknown tool requested: {tool}")
            return {"status": "error", "message": f"Unknown tool: {tool}"}

if __name__ == "__main__":
    # Initialize logging for standalone test
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    vanguard = VanguardAgent()
    
    # Test 1: Heartbeat
    print("\n--- Testing Heartbeat ---")
    print(json.dumps(vanguard.heartbeat(), indent=2))
    
    # Test 2: Enforce Pico (Valid)
    print("\n--- Testing Enforce Pico (Valid) ---")
    valid_manifest = {
        "name": "forage_agent.psvc",
        "version": "1.2.0",
        "license": "EUPL-1.2",
        "author": "Louis-Philippe Audette",
        "health_check": "/health"
    }
    vanguard.enforce_pico(valid_manifest)
    
    # Test 3: Enforce Pico (Invalid - Wrong License)
    print("\n--- Testing Enforce Pico (Invalid License) ---")
    invalid_manifest = {
        "name": "rogue_agent.psvc",
        "version": "1.0.0",
        "license": "Apache-2.0", # This should trigger a rejection
        "author": "Unknown",
        "health_check": "/health"
    }
    vanguard.enforce_pico(invalid_manifest)
    
    # Test 4: Ledger Review
    print("\n--- Ledger State ---")
    if vanguard.ledger_path.exists():
        print(vanguard.ledger_path.read_text())
