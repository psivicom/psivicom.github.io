# src/orchestrator/chain_orchestrator.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.pilot_agent import PilotAgent
from src.agents.intelligence_agent import IntelligenceAgent
from src.agents.neuroplasticity_agent import NeuroplasticityAgent
from src.agents.void_observer import VoidObserver # NEW IMPORT

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Orchestrator")

def run_chain():
    """
    Executes the cognitive pipeline in strict order:
    1. Perception (Pilot)
    2. Memory/Context (Intelligence)
    3. Subconscious/Gravity (Void Observer) <- MUST RUN BEFORE NEURO
    4. Adaptation/Will (Neuroplasticity)
    """
    logger.info("=== STARTING COGNITIVE CHAIN ===")
    
    try:
        # Step 1: Scan Reality
        logger.info("[1/4] Running Pilot Agent (Perception)...")
        pilot = PilotAgent()
        pilot.finalize()
        
        # Step 2: Query Memory & Evaluate Peers
        logger.info("[2/4] Running Intelligence Agent (Memory/Social)...")
        intel = IntelligenceAgent()
        intel.finalize()
        
        # Step 3: Measure Invisible Forces
        logger.info("[3/4] Running Void Observer (Dark Matter Detection)...")
        void = VoidObserver()
        void.finalize()
        
        # Step 4: Evolve Personality Based on All Inputs
        logger.info("[4/4] Running Neuroplasticity Agent (Adaptation)...")
        neuro = NeuroplasticityAgent()
        neuro.finalize()
        
        logger.info("=== COGNITIVE CHAIN COMPLETE ===")
        return True

    except Exception as e:
        logger.error(f"CHAIN FAILURE: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = run_chain()
    sys.exit(0 if success else 1)
