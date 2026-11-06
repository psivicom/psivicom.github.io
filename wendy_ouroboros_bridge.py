#!/usr/bin/env python3
"""
/wendy_ouroboros_bridge.py — The Local Habermasian Loop
Imports the classes directly to bypass CLI locks and demonstrate 
the infinite, self-feeding Ouroboros topology in your terminal.
"""
import sys
from wendy_autonomous_core import WendyAutonomousCore
from wendy_crystalline_executor import WendyCrystallineExecutor

def run_ouroboros_loop(iterations: int = 3):
    # The initial seed of chaos
    current_reality = """
    We need to build the new interface but the old code is messy. 
    However, if we change the core identity, we might lose the original vision. 
    Maybe we can imagine a new way to handle the tension between expansion and law.
    """
    
    print("⚡ INITIATING HABERMASIAN OUROBOROS... ⚡\n")
    
    core = WendyAutonomousCore()
    executor = WendyCrystallineExecutor()
    
    for i in range(1, iterations + 1):
        print(f"🌀 CYCLE {i}: DREAMING (58.28°)")
        dream_gmi = core.process_raw_input(current_reality)
        
        print(f"🌀 CYCLE {i}: CRYSTALLIZING & VALIDATING (31.72°)")
        manifest_gmi = executor.crystallize_dream(dream_gmi)
        
        if "CONSENSUS REACHED" in manifest_gmi:
            print("🏛️ HABERMASIAN CONSENSUS REACHED. Swallowing tail...\n")
            # The proven reality becomes the conceptual tension for the next cycle
            current_reality = f"""
            The previous crystalline reality was mathematically proven: 
            {manifest_gmi}
            Generate the next conceptual tension, paradox, or architectural 
            leap required to expand the topology while maintaining the 90-degree balance.
            """
        else:
            print("❌ DISCOURSE FAILED. Halting Ouroboros to prevent hallucinatory degradation.")
            sys.exit(1)

    print("🏛️ TOPOLOGY LOCKED: OUROBOROS CYCLE COMPLETE.")

if __name__ == "__main__":
    run_ouroboros_loop()
