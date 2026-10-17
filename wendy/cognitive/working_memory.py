import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class MemoryNode:
    key: str
    value: Any
    salience: float
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0

class WorkingMemory:
    def __init__(self, capacity: int = 1000, decay_rate: float = 0.01):
        self.capacity = capacity
        self.decay_rate = decay_rate
        self.store: Dict[str, MemoryNode] = {}

    def update(self, key: str, value: Any, salience: float = 1.0) -> None:
        current_time = time.time()
        if key in self.store:
            node = self.store[key]
            node.value = value
            node.salience = max(node.salience, salience)
            node.timestamp = current_time
            node.access_count += 1
        else:
            if len(self.store) >= self.capacity:
                self._evict_lowest_salience(current_time)
            self.store[key] = MemoryNode(key=key, value=value, salience=salience, timestamp=current_time)

    def retrieve(self, key: str) -> Optional[Any]:
        current_time = time.time()
        if key not in self.store:
            return None
        node = self.store[key]
        node.access_count += 1
        node.timestamp = current_time
        return node.value

    def _evict_lowest_salience(self, current_time: float) -> None:
        if not self.store:
            return
        lowest_key = min(
            self.store.keys(),
            key=lambda k: self.store[k].salience * (1.0 / (1.0 + self.decay_rate * (current_time - self.store[k].timestamp)))
        )
        del self.store[lowest_key]

    def dump(self) -> List[Dict[str, Any]]:
        return [
            {
                "key": node.key,
                "value": node.value,
                "salience": node.salience,
                "access_count": node.access_count
            }
            for node in self.store.values()
        ]
