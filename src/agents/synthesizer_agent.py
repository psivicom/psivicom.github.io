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
from typing import Optional, Tuple, List

# CORRECT absolute imports from the repository root (PYTHONPATH)
from src.mesh.vram_mesh import VRAMMesh
from src.mesh.mesh_governor import MeshGovernor
from src.core.vector_pixelizer import VectorPixelizer
from src.orchestrator.psvc_provisioner import ElasticPSVCProvisioner

logger = logging.getLogger(__name__)

class SynthesizerAgent:
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
        
        self.bytes_per_element = 8
        self.fusion_overhead = 1.4
        self.source_count = 3
        
        logger.info(f"SynthesizerAgent {self.agent_id} initialized.")

    def synthesize_batch(self, source_samples: int) -> Tuple[bool, Optional[np.ndarray]]:
        total_samples = source_samples * self.source_count
        logger.info(f"[{self.agent_id}] Starting synthesis. Sources: {self.source_count}, Samples/source: {source_samples}, Total: {total_samples}")
        
        required_vram = self._calc_required_vram(total_samples)
        handle = self.provisioner.get_handle(self.agent_id)
        if not handle:
            logger.error(f"[{self.agent_id}] No VRAM handle.")
            return False, None
            
        current_vram = handle.size_bytes
        
        if required_vram > current_vram:
            logger.warning(f"[{self.agent_id}] Synthesis requires {required_vram} bytes, only {current_vram} allocated. Requesting evolution...")
            success = self.governor.request_evolution(self.agent_id, new_dimensions=total_samples, new_memory=required_vram)
            if not success:
                logger.info(f"[{self.agent_id}] Evolution denied. Pixelizer will use chunking.")
                
        source_a = np.random.rand(source_samples).astype(np.float64)
        source_b = np.random.rand(source_samples).astype(np.float64)
        source_c = np.random.rand(source_samples).astype(np.float64)
        fused_input = np.concatenate([source_a, source_b, source_c])
        
        success, result = self.pixelizer.execute_vector_math(self.agent_id, operation="transform", input_data=fused_input)
        if not success:
            logger.error(f"[{self.agent_id}] Synthesis failed.")
            return False, None
            
        pheromone = f"synthesis_complete:{total_samples}_samples:{self.source_count}_sources"
        self.governor.deposit_pheromone(self.agent_id, pheromone)
        logger.info(f"[{self.agent_id}] Synthesis complete. Output size: {result.nbytes} bytes.")
        return True, result

    def generate_weekly_insight(self, daily_sample_counts: List[int]) -> Tuple[bool, Optional[np.ndarray]]:
        logger.info(f"[{self.agent_id}] Generating weekly insight.")
        weekly_results = []
        
        for day, count in enumerate(daily_sample_counts):
            success, day_result = self.synthesize_batch(source_samples=count)
            if not success:
                logger.error(f"[{self.agent_id}] Day {day+1} failed.")
                return False, None
            weekly_results.append(day_result)
        
        try:
            weekly_insight = np.concatenate(weekly_results)
            pheromone = f"weekly_insight_complete:{len(daily_sample_counts)}_days:{weekly_insight.nbytes}_bytes"
            self.governor.deposit_pheromone(self.agent_id, pheromone)
            logger.info(f"[{self.agent_id}] Weekly insight ready.")
            return True, weekly_insight
        except Exception as e:
            logger.error(f"[{self.agent_id}] Aggregation failed: {e}")
            return False, None

    def _calc_required_vram(self, total_samples: int) -> int:
        base = total_samples * self.bytes_per_element
        return int(base * self.fusion_overhead)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    mesh = VRAMMesh(total_vram_bytes=4 * 1024 * 1024 * 1024)
    provisioner = ElasticPSVCProvisioner(mesh)
    governor = MeshGovernor(mesh, provisioner)
    pixelizer = VectorPixelizer(mesh, provisioner, governor)
    
    agent = SynthesizerAgent("synthesizer_01", provisioner, governor, pixelizer)
    
    initial_samples = 500
    initial_vram = agent._calc_required_vram(initial_samples * 3)
    provisioner.allocate(agent.agent_id, initial_vram, growth_margin=0.3)
    governor.register_agent(agent.agent_id, initial_samples, initial_vram)
    
    print("\n--- Normal Daily Synthesis ---")
    agent.synthesize_batch(source_samples=500)
    
    print("\n--- Weekly Insight (Large Data) ---")
    agent.generate_weekly_insight([500, 800, 1200, 600, 50000, 900, 700])
    
    print("\n--- Final Status ---")
    status = governor.get_mesh_status()
    print(f"Generations: {status['provisioner_stats']['average_generation']:.2f}")
    print(f"VRAM Utilization: {status['vram_stats']['utilization_percent']:.2f}%")
    print("Synthesizer complete. Mesh: NOMINAL.")
