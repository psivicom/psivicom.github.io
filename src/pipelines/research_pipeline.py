# src/pipelines/research_pipeline.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# Research Pipeline: Coordinates multi-agent research workflows with OSDR validation

import sys
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Ensure project root is in path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# CORRECTED IMPORTS: Pointing to new modular architecture
from src.core.psvc_reference import write_file, read_file, validate_file, content_hash, PRECISION_FLOAT16
from src.core.psvc_containers import seal_container, extract_metadata
from src.mesh.vram_mesh import VRAMMesh
from src.mesh.governor import MeshGovernor
from src.mesh.provisioner import ElasticPSVCProvisioner
from src.orchestrator.chain_orchestrator import ChainOrchestrator, AgentProfile, WorkflowStep
from src.agents.forage_agent import ForageAgent
from src.agents.pilot_agent import PilotAgent
from src.agents.consolidator_agent import ConsolidatorAgent
from src.agents.literature_agent import LiteratureAgent

logger = logging.getLogger(__name__)


class ResearchPipeline:
    """
    Coordinates end-to-end research workflows using the PSIVI mesh.
    Integrates OSDR ground truth validation via Pilot Agent.
    """
    
    def __init__(self, vram_gb: float = 8.0, osdr_data_path: str = "data/osdr_ground_truth.jsonl"):
        self.vram_gb = vram_gb
        self.osdr_data_path = osdr_data_path
        self.orchestrator = None
        self.results: List[Dict] = []
        
    def initialize(self) -> bool:
        """Initialize the orchestrator and mesh infrastructure"""
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
        """
        Execute a research workflow for a given goal.
        
        Args:
            goal: Research goal/question
            agents: Optional list of agent IDs to include
        
        Returns:
            Workflow execution results
        """
        if not self.orchestrator:
            if not self.initialize():
                return {"success": False, "error": "Pipeline initialization failed"}
        
        # Define default workflow steps
        steps = [
            WorkflowStep(
                source_agent_id="orchestrator",
                target_agent_id="forage_agent",
                operation="collect_data",
                is_mutable=True
            ),
            WorkflowStep(
                source_agent_id="forage_agent",
                target_agent_id="literature_agent",
                operation="validate_context",
                is_mutable=True
            ),
            WorkflowStep(
                source_agent_id="literature_agent",
                target_agent_id="critic_agent",
                operation="evaluate_quality",
                is_mutable=False
            ),
            WorkflowStep(
                source_agent_id="critic_agent",
                target_agent_id="consolidator_agent",
                operation="synthesize_results",
                is_mutable=True
            )
        ]
        
        # Execute workflow (Pilot Agent automatically evaluates elasticity)
        success = self.orchestrator.execute_workflow(steps, goal=goal)
        
        result = {
            "success": success,
            "goal": goal,
            "timestamp": datetime.utcnow().isoformat(),
            "vram_gb": self.vram_gb,
            "osdr_data_path": self.osdr_data_path
        }
        
        self.results.append(result)
        return result
    
    def run_pilot_scan(self) -> Dict[str, Any]:
        """
        Run Pilot Agent scan to evaluate mesh epistemic health.
        
        Returns:
            Pilot scan results including fragility/concordance counts
        """
        if not self.orchestrator:
            if not self.initialize():
                return {"success": False, "error": "Pipeline initialization failed"}
        
        elasticity = self.orchestrator.evaluate_elasticity()
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "decision": elasticity.decision,
            "reason": elasticity.reason,
            "fragility_count": elasticity.fragility_count,
            "concordance_count": elasticity.concordance_count,
            "osdr_matches": len(elasticity.osdr_matches)
        }
    
    def export_results(self, output_dir: Path = None) -> List[Path]:
        """
        Export all workflow results as RFC 1001 compliant containers.
        
        Args:
            output_dir: Output directory (default: reports/pico_containers)
        
        Returns:
            List of exported file paths
        """
        if output_dir is None:
            output_dir = Path("reports/pico_containers")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = []
        
        for i, result in enumerate(self.results):
            # Create summary vector
            summary = json.dumps(result, sort_keys=True)
            summary_hash = content_hash(summary.encode())
            
            # Create vector from hash
            vector = np.zeros(4096, dtype=np.float32)
            for j, char in enumerate(summary_hash[:4096]):
                vector[j] = ord(char) / 255.0
            vector /= np.linalg.norm(vector)
            
            # Write container
            filename = f"research_result_{i}_{summary_hash[:12]}.psvc"
            filepath = output_dir / filename
            write_file(vector, filepath, precision=PRECISION_FLOAT16)
            
            # Write sidecar
            sidecar_path = filepath.with_suffix('.json')
            with open(sidecar_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            exported_files.append(filepath)
            logger.info(f"Exported result to {filename}")
        
        return exported_files
    
    def get_mesh_status(self) -> Dict[str, Any]:
        """Get current mesh status from orchestrator"""
        if not self.orchestrator:
            return {"status": "not_initialized"}
        
        return {
            "status": "nominal",
            "vram_gb": self.vram_gb,
            "results_count": len(self.results),
            "osdr_data_loaded": Path(self.osdr_data_path).exists()
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    pipeline = ResearchPipeline(vram_gb=4.0, osdr_data_path="data/osdr_ground_truth.jsonl")
    
    if not pipeline.initialize():
        print("❌ Failed to initialize Research Pipeline")
        sys.exit(1)
    
    print("✅ Research Pipeline initialized")
    
    # Run a sample workflow
    goal = "Analyze Goldstream forage window with satellite radar and literature context"
    result = pipeline.run_workflow(goal)
    
    if result["success"]:
        print(f"\n✅ Workflow completed: {goal}")
        print(f"   Timestamp: {result['timestamp']}")
    else:
        print(f"\n❌ Workflow failed: {result.get('error', 'Unknown error')}")
    
    # Run pilot scan
    pilot_result = pipeline.run_pilot_scan()
    print(f"\n🧭 Pilot Scan: {pilot_result['decision']}")
    print(f"   Fragility: {pilot_result['fragility_count']}, Concordance: {pilot_result['concordance_count']}")
    
    # Export results
    exported = pipeline.export_results()
    print(f"\n📦 Exported {len(exported)} result containers")
    
    # Show mesh status
    status = pipeline.get_mesh_status()
    print(f"\n📊 Mesh Status: {status['status']}")
