import enum
from typing import Any, Dict, Optional


class AgentLayer(enum.Enum):
    """Defines the hierarchical layer of an agent within the mesh."""
    INGESTION = "INGESTION"
    PROCESSING = "PROCESSING"
    DISPATCH = "DISPATCH"
    REPORTING = "REPORTING"


class BaseAgent:
    """Abstract base class for all agents in the PsiviCom mesh."""

    def __init__(self, name: str, layer: AgentLayer):
        self.name = name
        self.layer = layer
        self._state: Dict[str, Any] = {}

    def get_state(self) -> Dict[str, Any]:
        return self._state.copy()

    def set_state(self, key: str, value: Any) -> None:
        self._state[key] = value

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement execute method")
