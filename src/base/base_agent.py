# src/base/base_agent.py
import json
from enum import Enum
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

class AgentLayer(Enum):
    VALIDATION = "validation"
    OPTIMIZATION = "optimization"
    HEALING = "healing"

class BaseAgent:
    def __init__(self, name: str, capabilities: List[str] = None):
        self.name = name
        self.capabilities = capabilities or []
        self.creation_time = datetime.now().isoformat()
        self.receipt_chain: List[Dict] = []
        
    def seal(self, action: str, payload: Dict, fragility: bool = False, concordance: bool = False):
        """Records an event in the receipt chain."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "payload": payload,
            "flags": {"fragility": fragility, "concordance": concordance}
        }
        self.receipt_chain.append(entry)

    def seal_result(self, signal_vector: Any, output_dir: Path, meta: Dict = None):
        """Finalizes the agent run by writing the result JSON."""
        output_dir.mkdir(parents=True, exist_ok=True)
        result_path = output_dir / f"{self.name}_result.json"
        
        final_data = {
            "agent": self.name,
            "timestamp": self.creation_time,
            "meta": meta or {},
            "receipt_count": len(self.receipt_chain),
            "signal_preview": list(signal_vector[:5]) if hasattr(signal_vector, '__getitem__') else str(signal_vector)[:50]
        }
        
        result_path.write_text(json.dumps(final_data, indent=2))
        print(f"✅ Sealed result to {result_path}")
