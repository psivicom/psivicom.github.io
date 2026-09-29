# src/base/base_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

from enum import Enum
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class AgentLayer(Enum):
    PERCEPTION = "perception"
    FORAGE = "forage"
    LITERATURE = "literature"
    SATELLITE = "satellite"
    CRITIC = "critic"
    INTELLIGENCE = "intelligence"
    SYNTHESIS = "synthesis"
    REPORTING = "reporting"
    GOVERNANCE = "governance"
    VALIDATION = "validation"
    ORCHESTRATION = "orchestration"
    OPTIMIZATION = "optimization"

class BaseAgent(ABC):
    LAYER: AgentLayer = AgentLayer.PERCEPTION

    def __init__(self, name: str, capabilities: Optional[List[str]] = None):
        self.name = name
        self.capabilities = capabilities or []
        self.state: Dict[str, Any] = {}

    @abstractmethod
    def _run_logic(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def execute(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            result = self._run_logic(*args, **kwargs)
            return {
                "status": "success", 
                "agent": self.name, 
                "layer": self.LAYER.value, 
                "result": result
            }
        except Exception as e:
            return {
                "status": "error", 
                "agent": self.name, 
                "error": str(e)
            }
