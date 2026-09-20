# ============================================================
# FILE: synthesizer_agent.py
# PATH: psivicom.github.io/src/agents/synthesizer_agent.py
# DESCRIPTION: Evolving Synthesizer Agent
#   Combines multi-agent data into scientific insights.
#   Uses elastic VRAM and intelligent chunking.
# LICENSE: EUPL-1.2
# COMPLIANCE: NIST SP 800-218, FAIR Open Science
# ============================================================

import logging
import numpy as np
import time
import sys
import os
from typing import Optional, Tuple, List

# Ensure root directory is in path
base_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
)
sys.path.insert(0, base_dir)

# Import elastic core infrastructure
from vram_mesh import VRAMMesh
from mesh_governor import MeshGovernor
from src.core.vector_pixelizer import VectorPixelizer
from src.orchestrator.psvc_provisioner import (
    ElasticPSVCProvisioner
)

logger = logging.getLogger(__name__)


class SynthesizerAgent:
    """
    Combines data from forage, satellite, and lidar
    agents into unified environmental synthesis reports.
    Handles unpredictable multi-source data fusion with
    elastic VRAM and intelligent chunking.
    """
    
    def __init__(
        self,
        agent_id: str,
        provisioner: ElasticPSVCProvisioner,
        governor: MeshGovernor,
        pixelizer: VectorPixelizer
    ):
        self.agent_id = agent_id
        self.provisioner = provisioner
        self.governor = governor
        self.pixelizer = pixelizer
        
        # Constants for synthesis processing
        self.bytes_per_element = 8  # float64
        self.fusion_overhead = 1.4  # 40% for multi-source
        self.source_count = 3  # forage + satellite + lidar
        
        logger.info(
            f"SynthesizerAgent {self.agent_id} initialized."
        )

    def synthesize_batch(
        self,
        source_samples: int
    ) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Fuses data from multiple agent sources into a
        single synthesis report.

        Args:
            source_samples: Number of samples per source.
                Total input = source_samples * 3 sources.

        Returns:
            Tuple of (success, synthesized_result)
        """
        total_samples = source_samples * self.source_count
        
        logger.info(
            f"[{self.agent_id}] Starting synthesis. "
            f"Sources: {self.source_count}, "
            f"Samples/source: {source_samples}, "
            f"Total: {total_samples}"
        )
        
        # 1. Calculate required VRAM
        required_vram = self._calc_required_vram(
            total_samples
        )
        
        # 2. Check current allocation
        handle = self.provisioner.get_handle(
            self.agent_id
        )
        if not handle:
            logger.error(
                f"[{self.agent_id}] No VRAM handle."
            )
            return False, None
            
        current_vram = handle.size_bytes
        
        # 3. EVOLUTION CHECK
        if required_vram > current_vram:
            logger.warning(
                f"[{self.agent_id}] Synthesis requires "
                f"{required_vram} bytes, only "
                f"{current_vram} allocated. "
                f"Requesting evolution..."
            )
            
            success = self.governor.request_evolution(
                self.agent_id,
                new_dimensions=total_samples,
                new_memory=required_vram
            )
            
            if not success:
                logger.info(
                    f"[{self.agent_id}] Evolution denied. "
                    f"Pixelizer will use chunking."
                )
                
        # 4. Simulate multi-source fusion data
        #    Source A: Forage telemetry
        source_a = np.random.rand(
            source_samples
        ).astype(np.float64)
        
        #    Source B: Satellite SAR backscatter
        source_b = np.random.rand(
            source_samples
        ).astype(np.float64)
        
        #    Source C: Lidar canopy density
        source_c = np.random.rand(
            source_samples
        ).astype(np.float64)
        
        # 5. Concatenate all sources for fusion
        fused_input = np.concatenate(
            [source_a, source_b, source_c]
        )
        
        # 6. Execute synthesis via pixelizer
        success, result = self.pixelizer.execute_vector_math(
            self.agent_id,
            operation="transform",
            input_data=fused_input
        )
        
        if not success:
            logger.error(
                f"[{self.agent_id}] Synthesis failed."
            )
            return False, None
            
        # 7. Deposit pheromone for FAIR audit
        pheromone = (
            f"synthesis_complete:"
            f"{total_samples}_samples:"
            f"{self.source_count}_sources"
        )
        self.governor.deposit_pheromone(
            self.agent_id, pheromone
        )
        
        logger.info(
            f"[{self.agent_id}] Synthesis complete. "
            f"Output size: {result.nbytes} bytes."
        )
        
        return True, result

    def generate_weekly_insight(
        self,
        daily_sample_counts: List[int]
    ) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Generates a weekly scientific insight by
        synthesizing 7 days of multi-source data.

        Args:
            daily_sample_counts: List of sample counts
                for each day (length 7).

        Returns:
            Tuple of (success, weekly_result)
        """
        logger.info(
            f"[{self.agent_id}] Generating weekly insight."
        )
        
        weekly_results = []
        
        for day, count in enumerate(daily_sample_counts):
            logger.info(
                f"[{self.agent_id}] Processing day "
                f"{day + 1}/7 with {count} samples."
            )
            
            success, day_result = self.synthesize_batch(
                source_samples=count
            )
            
            if not success:
                logger.error(
                    f"[{self.agent_id}] Day {day+1} failed."
                )
                return False, None
                
            weekly_results.append(day_result)
        
        # Aggregate weekly results
        try:
            weekly_insight = np.concatenate(
                weekly_results
            )
            
            pheromone = (
                f"weekly_insight_complete:"
                f"{len(daily_sample_counts)}_days:"
                f"{weekly_insight.nbytes}_bytes"
            )
            self.governor.deposit_pheromone(
                self.agent_id, pheromone
            )
            
            logger.info(
                f"[{self.agent_id}] Weekly insight ready."
            )
            return True, weekly_insight
            
        except Exception as e:
            logger.error(
                f"[{self.agent_id}] Aggregation failed: {e}"
            )
            return False, None

    def _calc_required_vram(
        self, total_samples: int
    ) -> int:
        """Calculates VRAM for multi-source fusion."""
        base = total_samples * self.bytes_per_element
        return int(base * self.fusion_overhead)


# ============================================================
# Example Usage / Test Harness
# ============================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 1. Initialize infrastructure
    mesh = VRAMMesh(
        total_vram_bytes=4 * 1024 * 1024 * 1024
    )
    provisioner = ElasticPSVCProvisioner(mesh)
    governor = MeshGovernor(mesh, provisioner)
    pixelizer = VectorPixelizer(
        mesh, provisioner, governor
    )
    
    # 2. Initialize agent
    agent = SynthesizerAgent(
        "synthesizer_01",
        provisioner,
        governor,
        pixelizer
    )
    
    # 3. Register with small initial allocation
    initial_samples = 500
    initial_vram = agent._calc_required_vram(
        initial_samples * 3
    )
    provisioner.allocate(
        agent.agent_id, initial_vram, growth_margin=0.3
    )
    governor.register_agent(
        agent.agent_id, initial_samples, initial_vram
    )
    
    # 4. Process a normal daily batch
    print("\n--- Normal Daily Synthesis ---")
    agent.synthesize_batch(source_samples=500)
    
    # 5. Process a massive weekly insight
    print("\n--- Weekly Insight (Large Data) ---")
    daily_counts = [
        500, 800, 1200, 600, 50000, 900, 700
    ]
    agent.generate_weekly_insight(daily_counts)
    
    # 6. Final status
    print("\n--- Final Status ---")
    status = governor.get_mesh_status()
    gen = status['provisioner_stats']['average_generation']
    util = status['vram_stats']['utilization_percent']
    print(f"Generations: {gen:.2f}")
    print(f"VRAM Utilization: {util:.2f}%")
    print("Synthesizer complete. Mesh: NOMINAL.")
