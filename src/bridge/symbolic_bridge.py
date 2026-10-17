import subprocess
import json
import sys

class SymbolicBridge:
    def __init__(self):
        self.intent_map = {
            "observe": [0.1] * 16,
            "analyze": [0.5] * 16,
            "evolve": [0.9] * 16
        }

    def translate_intent(self, intent: str) -> list:
        """Translates human intent into a 16-dimensional vector."""
        return self.intent_map.get(intent, [0.0] * 16)

    def execute_cycle(self, intent: str):
        vector = self.translate_intent(intent)
        csv_data = ",".join(map(str, vector))
        
        print(f"🌉 Bridge: Translating '{intent}' to vector space...")
        
        # Call the Zig Vector Engine
        try:
            result = subprocess.run(
                ["./src/core/vector_engine", csv_data], 
                capture_output=True, text=True
            )
            print(result.stdout)
        except Exception as e:
            print(f"❌ Bridge Error: {e}")

if __name__ == "__main__":
    bridge = SymbolicBridge()
    target_intent = sys.argv[1] if len(sys.argv) > 1 else "observe"
    bridge.execute_cycle(target_intent)
