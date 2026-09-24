# src/pipelines/research_pipeline.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add project root to path for absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Root level imports
from psvc_reference import write_file, read_file, validate_file, content_hash, PRECISION_FLOAT16

# src/ imports
from src.core.psvc_containers import seal_container, extract_metadata
from src.mesh.vram_mesh import VRAMMesh
from src.mesh.mesh_governor import MeshGovernor
from src.orchestrator.psvc_provisioner import ElasticPSVCProvisioner
from src.orchestrator.chain_orchestrator import ChainOrchestrator, AgentProfile, WorkflowStep
from src.agents.forage_agent import ForageAgent
from src.agents.pilot_agent import PilotAgent
from src.agents.consolidator_agent import ConsolidatorAgent
from src.agents.literature_agent import LiteratureAgent

logger = logging.getLogger(__name__)

class ResearchPipeline:
    def __init__(self, vram_gb: float = 8.0, osdr_data_path: str = "data/osdr_ground_truth.jsonl"):
        self.vram_gb = vram_gb
        self.osdr_data_path = osdr_data_path
        self.orchestrator = None
        self.results: List[Dict] = []
        
    def initialize(self) -> bool:
        try:
            self.orchestrator = ChainOrchestrator(
                total_vram_gb=self.vram_gb,
                osdr_data_path=self.osdr_data_path
            )
            logger.info("Research Pipeline initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Research Pipeline: {e}")
            return False
    
    def run_workflow(self, goal: str, agents: List[str] = None) -> Dict[str, Any]:
        if not self.orchestrator:
            if not self.initialize():
                return {"success": False, "error": "Pipeline initialization failed"}
        
        steps = [
            WorkflowStep(source_agent_id="orchestrator", target_agent_id="forage_agent", operation="collect_data", is_mutable=True),
            WorkflowStep(source_agent_id="forage_agent", target_agent_id="literature_agent", operation="validate_context", is_mutable=True),
            WorkflowStep(source_agent_id="literature_agent", target_agent_id="critic_agent", operation="evaluate_quality", is_mutable=False),
            WorkflowStep(source_agent_id="critic_agent", target_agent_id="consolidator_agent", operation="synthesize_results", is_mutable=True)
        ]
        
        success = self.orchestrator.execute_workflow(steps, goal=goal)
        result = {"success": success, "goal": goal, "timestamp": datetime.utcnow().isoformat()}
        self.results.append(result)
        return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pipeline = ResearchPipeline(vram_gb=4.0, osdr_data_path="data/osdr_ground_truth.jsonl")
    if pipeline.initialize():
        print("✅ Research Pipeline initialized")
        result = pipeline.run_workflow("Analyze Goldstream forage window")
        print(f"Result: {result}")
