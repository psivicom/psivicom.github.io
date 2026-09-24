# src/automation/ai_planner.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# Lightweight AI Planner for Dynamic DAG Generation (Optimized for SLMs)

import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger(__name__)

class AIPlanner:
    """
    Intelligent Automation Planner optimized for Small Language Models (SLMs).
    Dynamically generates workflow DAGs based on OSDR fragility context.
    Designed to interface with fast, local inference engines (e.g., Ollama, llama.cpp).
    """
    
    def __init__(self, model_endpoint: str = "http://localhost:11434/api/generate", model_name: str = "phi3:mini"):
        self.model_endpoint = model_endpoint
        self.model_name = model_name
        self.use_local_mock = True  # Fallback for environments without local LLM running

    def generate_workflow_dag(self, goal: str, pilot_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Uses a lightweight AI model to reason about the goal and pilot report,
        returning a structured JSON array of workflow steps.
        """
        fragility_count = pilot_report.get("fragility_count", 0)
        concordance_count = pilot_report.get("concordance_count", 0)
        traps = pilot_report.get("fragility_traps", [])
        
        # Construct a highly optimized, structured prompt for SLMs
        prompt = f"""
        You are an expert scientific workflow orchestrator. 
        Goal: {goal}
        Context: The mesh detected {fragility_count} OSDR fragility traps and {concordance_count} concordant controls.
        Specific Fragility Traps: {json.dumps(traps[:3])} # Top 3 traps
        
        Available Agents:
        - forage_agent: Collects raw data and initial vectors.
        - literature_agent: Searches scientific databases for specific genes/organisms to resolve discordance.
        - critic_agent: Evaluates the quality and statistical significance of findings.
        - consolidator_agent: Prunes redundant vectors and synthesizes final reports.
        - synthesizer_agent: Generates final human-readable insights.

        Task: Generate a JSON array of workflow steps to resolve this goal. 
        Rules:
        1. If fragility > concordance, prioritize 'literature_agent' and 'critic_agent' to resolve specific genes.
        2. If concordance > fragility * 2, prioritize 'consolidator_agent' to prune and finalize.
        3. Always start with 'forage_agent' if no data exists, or 'synthesizer_agent' at the end.
        4. Output ONLY valid JSON. No markdown, no explanations.
        
        JSON Schema:
        [
          {{"step_id": "step_1", "agent_id": "forage_agent", "operation": "collect_data", "dependencies": []}},
          {{"step_id": "step_2", "agent_id": "literature_agent", "operation": "resolve_fragility", "dependencies": ["step_1"]}}
        ]
        """
        
        if self.use_local_mock:
            return self._mock_slm_reasoning(goal, pilot_report)
            
        # TODO: Implement actual HTTP POST to self.model_endpoint with prompt
        # response = requests.post(self.model_endpoint, json={"model": self.model_name, "prompt": prompt, "stream": False})
        # return json.loads(response.json()["response"])

    def _mock_slm_reasoning(self, goal: str, pilot_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Simulates the deterministic output of a well-prompted 3B-parameter SLM.
        """
        fragility_count = pilot_report.get("fragility_count", 0)
        concordance_count = pilot_report.get("concordance_count", 0)
        traps = pilot_report.get("fragility_traps", [])
        
        steps = [
            {"step_id": "step_1", "agent_id": "forage_agent", "operation": "collect_data", "dependencies": []}
        ]
        
        if fragility_count > concordance_count and len(traps) > 0:
            # SLM reasoning: High fragility detected, inject targeted resolution agents
            steps.append({
                "step_id": "step_2", 
                "agent_id": "literature_agent", 
                "operation": f"resolve_discordance_for_{traps[0].get('gene', 'unknown')}", 
                "dependencies": ["step_1"]
            })
            steps.append({
                "step_id": "step_3", 
                "agent_id": "critic_agent", 
                "operation": "evaluate_statistical_significance", 
                "dependencies": ["step_2"]
            })
        elif concordance_count > fragility_count * 2:
            # SLM reasoning: High concordance, optimize and prune
            steps.append({
                "step_id": "step_2", 
                "agent_id": "consolidator_agent", 
                "operation": "prune_redundant_vectors", 
                "dependencies": ["step_1"]
            })
        else:
            # SLM reasoning: Stable state, proceed to synthesis
            steps.append({
                "step_id": "step_2", 
                "agent_id": "synthesizer_agent", 
                "operation": "generate_insight_report", 
                "dependencies": ["step_1"]
            })
            
        steps.append({
            "step_id": "step_final", 
            "agent_id": "synthesizer_agent", 
            "operation": "finalize_psvc_sealing", 
            "dependencies": [steps[-1]["step_id"]]
        })
        
        return steps
