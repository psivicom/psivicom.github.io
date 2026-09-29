# src/base/base_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Base Agent: The foundational class for all PSIVI AETHER Mesh agents.
Defines common properties, logging, and layer classification.
"""

import logging
from enum import Enum
from typing import Dict, Any, Optional

logger = logging.getLogger("WENDY_AGENT")

class AgentLayer(Enum):
    """Defines the operational layers of the mesh."""
    INGESTION = "ingestion"
    ORCHESTRATION = "orchestration"
    VALIDATION = "validation"
    COGNITION = "cognition"

class BaseAgent:
    def __init__(self, name: str, capabilities: list):
        self.name = name
        self.capabilities = capabilities
        self.state: Dict[str, Any] = {}
        logger.info(f"🤖 Agent {name} initialized with capabilities: {capabilities}")

    def execute(self, instruction: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main entry point for agent execution."""
        logger.info(f"⚙️ Agent {self.name} executing...")
        return {"status": "success", "agent": self.name}
