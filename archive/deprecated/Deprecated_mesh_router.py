import yaml
import os
import json
import datetime

class MeshRouter:
    def __init__(self, config_path="agent_config.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.agents = self.config["agents"]
        self.memory_folder = self.config["memory"]["folder"]

    def who_handles(self, task):
        """Route a task to the right agent based on keywords"""
        routing = {
            "weather": "forage",
            "temperature": "forage",
            "bloom": "forage",
            "elevation": "lidar",
            "terrain": "lidar",
            "canopy": "lidar",
            "audit": "intelligence",
            "license": "intelligence",
            "synthesize": "synthesizer",
            "report": "synthesizer",
            "insight": "synthesizer",
            "heartbeat": "vanguard",
            "security": "vanguard",
        }
        task_lower = task.lower()
        for keyword, agent in routing.items():
            if keyword in task_lower:
                return agent
        return self.config["routing"]["fallback"]

    def mesh_status(self):
        """Read the entire mesh and return a status summary"""
        memories = []
        if os.path.exists(self.memory_folder):
            for file in os.listdir(self.memory_folder):
                if file.endswith("_memory.json"):
                    with open(os.path.join(self.memory_folder, file)) as f:
                        memories.append(json.load(f))

        active_agents = set(m.get("agent", "unknown") for m in memories)
        declared_agents = set(self.agents.keys())
        missing = declared_agents - active_agents

        return {
            "declared_agents": list(declared_agents),
            "active_agents": list(active_agents),
            "silent_agents": list(missing),
            "total_memories": len(memories),
            "mesh_health": "NOMINAL" if not missing else "DEGRADED",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def print_status(self):
        status = self.mesh_status()
        print(f"=== {self.config['mesh']['name']} STATUS ===")
        print(f"Health: {status['mesh_health']}")
        print(f"Declared: {', '.join(status['declared_agents'])}")
        print(f"Active:   {', '.join(status['active_agents'])}")
        print(f"Silent:   {', '.join(status['silent_agents']) or 'None'}")
        print(f"Memories: {status['total_memories']}")

if __name__ == "__main__":
    router = MeshRouter()
    router.print_status()
