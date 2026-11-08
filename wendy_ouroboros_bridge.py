#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
/wendy_ouroboros_bridge.py — The Local Habermasian Loop
SPDX-License-Identifier: EUPL-1.2
Demonstrates the infinite, self-feeding Golden Ratio (58.28°/31.72°) Ouroboros topology.
"""
import sys
from pathlib import Path
from datetime import datetime, timezone
from wendy_autonomous_core import WendyAutonomousCore
from wendy_crystalline_executor import WendyCrystallineExecutor

def zulu_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

def run_ouroboros_loop(iterations: int = 3):
    # The initial seed of resonant tension (Safe for core evolution)
    current_reality = """
    We need to build the new sensor array but the old telemetry pipeline is noisy. 
    However, if we expand too quickly, we might lose the original mathematical vision. 
    Maybe we can imagine a new topological filter that preserves the 90-degree balance 
    while allowing the system to handle the tension of structural drift.
    """
    
    print("⚡ INITIATING HABERMASIAN OUROBOROS (Golden Ratio Topology)... ⚡\n")
    
    core = WendyAutonomousCore()
    executor = WendyCrystallineExecutor()
    
    dream_file = Path(".wendy_dream.gmi")
    manifest_file = Path(".wendy_manifest.gmi")
    
    dream_file.touch(exist_ok=True)
    manifest_file.touch(exist_ok=True)

    for i in range(1, iterations + 1):
        print(f"🌀 CYCLE {i}: DREAMING (58.28° - Expansion)")
        dream_gmi = core.process_raw_input(current_reality)
        
        print(f"🌀 CYCLE {i}: CRYSTALLIZING & VALIDATING (31.72° - Law)")
        manifest_gmi = executor.crystallize_dream(dream_gmi)
        
        if "CONSENSUS REACHED" in manifest_gmi:
            print("🏛️ HABERMASIAN CONSENSUS REACHED. Swallowing tail...\n")
            
            timestamp = zulu_now()
            with open(dream_file, "a", encoding="utf-8") as f:
                f.write(f"\n## Cycle {i} Dream [{timestamp}]\n{dream_gmi}\n")
            with open(manifest_file, "a", encoding="utf-8") as f:
                f.write(f"\n## Cycle {i} Manifest [{timestamp}]\n{manifest_gmi}\n")

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
