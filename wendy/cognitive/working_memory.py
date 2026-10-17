import time
import math
from typing import Dict, Any, List, Optional

class WorkingMemoryNode:
    __slots__ = ('key', 'value', 'activation', 'last_accessed', 'tags')
    def __init__(self, key: str, value: Any, activation: float, tags: List[str]):
        self.key = key
        self.value = value
        self.activation = activation
        self.last_accessed = time.time()
        self.tags = tags

class WorkingMemory:
    def __init__(self, capacity: int = 1024, decay_rate: float = 0.05):
        self.capacity = capacity
        self.decay_rate = decay_rate
        self.store: Dict[str, WorkingMemoryNode] = {}

    def decay(self) -> None:
        current_time = time.time()
        keys_to_remove = []
        for key, node in self.store.items():
            elapsed = current_time - node.last_accessed
            node.activation *= math.exp(-self.decay_rate * elapsed)
            node.last_accessed = current_time
            if node.activation < 0.01:
                keys_to_remove.append(key)
        for k in keys_to_remove:
            del self.store[k]

    def set(self, key: str, value: Any, activation: float = 1.0, tags: Optional[List[str]] = None) -> None:
        self.decay()
        if len(self.store) >= self.capacity and key not in self.store:
            min_key = min(self.store.keys(), key=lambda k: self.store[k].activation)
            del self.store[min_key]
        self.store[key] = WorkingMemoryNode(key, value, activation, tags or [])

    def get(self, key: str) -> Optional[Any]:
        self.decay()
        if key in self.store:
            node = self.store[key]
            node.activation = min(1.0, node.activation + 0.2)
            node.last_accessed = time.time()
            return node.value
        return None

    def query_by_tag(self, tag: str) -> List[Any]:
        self.decay()
        results = []
        for node in self.store.values():
            if tag in node.tags:
                results.append(node.value)
        return results
