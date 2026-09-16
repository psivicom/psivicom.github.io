import os
import json
import datetime

class VectorMesh:
    def __init__(self, folder="reports"):
        self.folder = folder
        os.makedirs(self.folder, exist_ok=True)

    def write(self, text, agent_name):
        """Any agent can write its thoughts to the mesh"""
        filename = os.path.join(self.folder, f"{datetime.date.today().isoformat()}_{agent_name}_memory.json")
        data = {"text": text, "agent": agent_name, "timestamp": datetime.datetime.utcnow().isoformat()}
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"[MEMORY] {agent_name} wrote to mesh: {filename}")

    def read_all(self):
        """Any agent can read the entire mesh's memory"""
        memories = []
        for file in os.listdir(self.folder):
            if file.endswith("_memory.json"):
                with open(os.path.join(self.folder, file)) as f:
                    memories.append(json.load(f))
        return memories
