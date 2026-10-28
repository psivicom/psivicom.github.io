"""
WENDY v1.8 Convene Flow Orchestrator
Collapses multi-turn LLM drift into a single, locally pre-validated schema execution.
Integrates Zig bare-metal intent scoring for shadow fallback.
Integrates adversarial adjudicator to prevent GLM bias.
"""

import ctypes
import json
import os
import time
import hashlib
from typing import Any, Dict, Optional
import requests

# Import the adversarial adjudicator
from wendy_adjudicator import WendyAdjudicator, SystemState

# Load the compiled Zig local router
ZIG_LIB_PATH = os.path.join(os.path.dirname(__file__), "libwendy_local_router.so")
if not os.path.exists(ZIG_LIB_PATH):
    raise FileNotFoundError(f"WENDY Zig router not found at {ZIG_LIB_PATH}")

wendy_router = ctypes.CDLL(ZIG_LIB_PATH)

class IntentScore(ctypes.Structure):
    _fields_ = [
        ("confidence", ctypes.c_float),
        ("is_local_routable", ctypes.c_uint8),
        ("padding", ctypes.c_uint8 * 3),
    ]

# Strict JSON Schema for GLM output to prevent convene loop drift
CONVENE_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["read_sensor", "update_memory", "respond", "execute_tool", "process_acoustic", "analyze_hive"]},
        "payload": {"type": "object"},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
    },
    "required": ["action", "payload", "confidence"],
    "additionalProperties": False
}

class WendyConvene:
    def __init__(self, lane_endpoint: str, shadow_cache: Dict[str, Any]):
        self.lane_endpoint = lane_endpoint
        self.shadow_cache = shadow_cache
        self.adjudicator = WendyAdjudicator()
        self._setup_zig_bindings()

    def _setup_zig_bindings(self):
        wendy_router.wendy_score_intent.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_size_t]
        wendy_router.wendy_score_intent.restype = IntentScore

    def _get_local_embedding(self, query: str) -> list:
        """
        Placeholder for actual MiniLM local embedding generation.
        In production, this calls a local ONNX runtime session.
        Returns a 384-dimensional vector.
        """
        # Mock embedding for demonstration
        return [0.1] * 384 

    def _evaluate_shadow_fallback(self, query: str) -> Optional[Dict[str, Any]]:
        """Solves MiniLM-vs-shadow cost: bypass cloud if local confidence is high."""
        embedding = self._get_local_embedding(query)
        
        # Prepare C array
        FloatArray = ctypes.c_float * len(embedding)
        c_embedding = FloatArray(*embedding)
        
        # Call Zig bare-metal scorer
        score = wendy_router.wendy_score_intent(c_embedding, len(embedding))
        
        if score.is_local_routable == 1:
            print(f"[WENDY CONVENE] Shadow fallback triggered (confidence: {score.confidence:.2f})")
            # Return cached shadow response
            return self.shadow_cache.get("default_hive_status", {
                "action": "respond", 
                "payload": {"text": "Hive nominal."}, 
                "confidence": score.confidence
            })
        
        return None

    def _get_current_system_state(self) -> SystemState:
        """
        Retrieves current system state from Zig/Go layers.
        In production, this queries the actual bare-metal and sandbox state.
        """
        # Mock state for demonstration
        return SystemState(
            zig_checksum_valid=True,
            go_sandbox_exit_code=0,
            go_sandbox_stdout_hash=hashlib.sha256(b"mock_stdout").hexdigest(),
            sensor_data_present=True
        )

    def execute_convene(self, query: str) -> Dict[str, Any]:
        """Solves convene flow length: single-pass, schema-validated execution."""
        start_time = time.time()
        
        # 1. Attempt local shadow fallback
        shadow_result = self._evaluate_shadow_fallback(query)
        if shadow_result is not None:
            return shadow_result

        # 2. Fallback to cloud GLM (exactly ONE call)
        print("[WENDY CONVENE] Routing to cloud GLM via lane_endpoint")
        
        payload = {
            "model": "glm-4-flash",
            "messages": [{"role": "user", "content": query}],
            "response_format": {"type": "json_schema", "json_schema": CONVENE_SCHEMA},
            "temperature": 0.1
        }
        
        headers = {
            "Authorization": f"Bearer {os.environ.get('WENDY_API_KEY', '')}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.lane_endpoint, json=payload, headers=headers, timeout=5.0)
            response.raise_for_status()
            result = response.json()
            
            # 3. Parse GLM output
            content = result["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            
            # 4. ADVERSARIAL CHECK: Force validation against actual system state
            current_state = self._get_current_system_state()
            adjudication = self.adjudicator.evaluate_ruling(parsed, current_state)
            
            if adjudication["status"] == "REJECTED":
                print(f"[WENDY ADJUDICATOR] Blocked biased ruling: {adjudication['reason']}")
                return {
                    "action": "respond", 
                    "payload": {"text": "System state mismatch. Operation aborted for safety."}, 
                    "confidence": 0.0
                }
                
            print(f"[WENDY CONVENE] Single-pass execution validated in {time.time() - start_time:.2f}s")
            return adjudication["ruling"]
            
        except Exception as e:
            print(f"[WENDY CONVENE] Critical failure: {e}")
            return {
                "action": "respond", 
                "payload": {"text": "Convene flow failed. Node entering safe mode."}, 
                "confidence": 0.0
            }


if __name__ == "__main__":
    # Example initialization
    node = WendyConvene(
        lane_endpoint="https://api.open.bigmodel.cn/v1/chat/completions",
        shadow_cache={
            "default_hive_status": {
                "action": "respond", 
                "payload": {"text": "Acoustic nominal, varroa low."}, 
                "confidence": 0.92
            }
        }
    )
    
    result = node.execute_convene("What is the current varroa stress index?")
    print(json.dumps(result, indent=2))
