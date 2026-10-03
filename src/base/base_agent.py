# src/base/base_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Base Agent: The foundational class for all PSIVI AETHER Mesh agents.
Defines common properties, logging, and layer classification.
"""

import json
import logging
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional

logger = logging.getLogger("WENDY_AGENT")

class AgentLayer(Enum):
    """Defines the operational layers of the mesh."""
    INGESTION = "ingestion"
    ORCHESTRATION = "orchestration"
    VALIDATION = "validation"
    COGNITION = "cognition"
    SYNTHESIS = "synthesis"

class BaseAgent:
    def __init__(self, name: str, capabilities: list):
        self.name = name
        self.agent_id = name
        self.capabilities = capabilities
        self.creation_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        self.state: Dict[str, Any] = {"seals": []}
        logger.info(f"🤖 Agent {name} initialized with capabilities: {capabilities}")

    def execute(self, instruction: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main entry point for agent execution."""
        logger.info(f"⚙️ Agent {self.name} executing...")
        return {"status": "success", "agent": self.name}

    def seal(self, action: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Records a sealed action in the agent's state for auditability."""
        seal_record = {
            "action": action,
            "data": data or {},
            "timestamp": self.creation_time
        }
        self.state["seals"].append(seal_record)
        logger.debug(f"🔒 Sealed action: {action}")

    def seal_result(self, data: np.ndarray, output_dir: Path, meta: Optional[Dict[str, Any]] = None):
        """Seals the agent's result into a JSON report for the mesh."""
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = self.creation_time
        
        report = {
            "timestamp": timestamp,
            "agent": self.name,
            "layer": self.__class__.LAYER.value if hasattr(self.__class__, 'LAYER') else "unknown",
            "meta": meta or {},
            "data_summary": {
                "shape": data.shape if isinstance(data, np.ndarray) else len(data),
                "mean": float(np.mean(data)) if isinstance(data, np.ndarray) else 0.0
            }
        }
        
        filename = f"{self.name}_result_{int(datetime.now(timezone.utc).timestamp())}.json"
        (output_dir / filename).write_text(json.dumps(report, indent=2))
        logger.info(f"✅ Result sealed: {filename}")
