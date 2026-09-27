# src/base/base_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import json
from enum import Enum
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
import numpy as np

class AgentLayer(Enum):
    VALIDATION = "validation"
    OPTIMIZATION = "optimization"
    HEALING = "healing"

def _sanitize_for_json(obj):
    """
    Recursively converts NumPy objects to native Python types 
    so they can be serialized by json.dumps().
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize_for_json(i) for i in obj]
    else:
        return obj

class BaseAgent:
    def __init__(self, name: str, capabilities: List[str] = None):
        self.name = name
        self.capabilities = capabilities or []
        # Strictly UTC with microseconds
        self.creation_time = datetime.now(timezone.utc).isoformat(timespec='microseconds')
        self.receipt_chain: List[Dict] = []
        
    def seal(self, action: str, payload: Dict, fragility: bool = False, concordance: bool = False):
        """Records an event in the receipt chain."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec='microseconds'),
            "action": action,
            "payload": payload,
            "flags": {"fragility": fragility, "concordance": concordance}
        }
        self.receipt_chain.append(entry)

    def seal_result(self, signal_vector: Any, output_dir: Path, meta: Dict = None):
        """Finalizes the agent run by writing the result JSON safely."""
        output_dir.mkdir(parents=True, exist_ok=True)
        result_path = output_dir / f"{self.name}_result.json"
        
        # Prepare final data structure
        final_data = {
            "agent": self.name,
            "timestamp": self.creation_time,
            "meta": meta or {},
            "receipt_count": len(self.receipt_chain),
            # Convert signal preview to native list/floats to avoid TypeError
            "signal_preview": _sanitize_for_json(list(signal_vector[:5])) if hasattr(signal_vector, '__getitem__') else str(signal_vector)[:50]
        }
        
        # Sanitize the ENTIRE object recursively just in case meta contains numpy types too
        safe_data = _sanitize_for_json(final_data)
        
        try:
            result_path.write_text(json.dumps(safe_data, indent=2))
            print(f"✅ Sealed result to {result_path}")
        except Exception as e:
            print(f"❌ Failed to write result JSON: {e}")
            raise
