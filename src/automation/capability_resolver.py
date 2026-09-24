# src/automation/capability_resolver.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# Self-Evolving Capability Resolver for Dynamic Agent Generation

import sys
import json
import logging
import importlib
from pathlib import Path
from typing import Dict, Any, Optional, Type

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.base.base_agent import BaseAgent, AgentLayer

logger = logging.getLogger(__name__)

class CapabilityResolver:
    """
    Dynamically resolves missing capabilities or evolves new agents 
    when the Pilot Agent detects high fragility that existing agents cannot resolve.
    Inspired by neuro-symbolic evolution: deterministic fallback + dynamic generation.
    """
    
    def __init__(self, agents_module_path: str = "src.agents"):
        self.agents_module_path = agents_module_path
        self._agent_cache: Dict[str, Type[BaseAgent]] = {}
        self._load_existing_agents()

    def _load_existing_agents(self):
        """Scans the agents directory and caches available agent classes."""
        agents_dir = Path(__file__).parent.parent / "agents"
        for file_path in agents_dir.glob("*_agent.py"):
            module_name = file_path.stem
            try:
                module = importlib.import_module(f"{self.agents_module_path}.{module_name}")
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, BaseAgent) and attr is not BaseAgent:
                        self._agent_cache[attr.__name__.lower().replace("agent", "")] = attr
            except Exception as e:
                logger.warning(f"Failed to load agent module {module_name}: {e}")

    def resolve(self, required_capability: str, osdr_context: Optional[Dict[str, Any]] = None) -> Optional[BaseAgent]:
        """
        Attempts to resolve a required capability. 
        If missing, and OSDR context indicates high fragility, triggers evolution protocol.
        """
        capability_key = required_capability.lower().replace("agent", "").strip()
        
        # 1. Check existing cache
        if capability_key in self._agent_cache:
            logger.info(f"Resolved capability '{required_capability}' from existing cache.")
            return self._agent_cache[capability_key](name=required_capability)
        
        # 2. Check for OSDR-driven evolution trigger
        if osdr_context and osdr_context.get("discordant", False):
            logger.warning(f"Capability '{required_capability}' missing. OSDR fragility detected. Initiating evolution protocol.")
            return self._evolve_agent(required_capability, osdr_context)
        
        logger.error(f"Capability '{required_capability}' not found and no evolution trigger.")
        return None

    def _evolve_agent(self, capability_name: str, osdr_context: Dict[str, Any]) -> Optional[BaseAgent]:
        """
        Simulates the evolution of a new agent tailored to the specific OSDR fragility trap.
        In a full implementation, this would call an LLM to generate the Python class, 
        write it to disk, and import it. Here, we instantiate a dynamic proxy agent.
        """
        gene = osdr_context.get("gene", "unknown")
        organism = osdr_context.get("organism", "unknown")
        
        logger.info(f"Evolving dynamic agent for fragility trap: {gene} in {organism}")
        
        # Create a dynamic agent class on the fly
        class_name = f"Evolved_{gene}_{capability_name}_Agent"
        
        DynamicAgent = type(
            class_name,
            (BaseAgent,),
            {
                "LAYER": AgentLayer.INGESTION,
                "__init__": lambda self, name="evolved": super(type(self), self).__init__(
                    name=name, 
                    capabilities=[capability_name, "osdr_validation"]
                ),
                "execute": lambda self, input_vector=None: self._simulate_evolved_execution(gene, organism)
            }
        )
        
        # Register in cache for future use
        self._agent_cache[capability_key] = DynamicAgent
        
        logger.info(f"Successfully evolved and cached: {class_name}")
        return DynamicAgent(name=f"evolved_{gene}")

    def _simulate_evolved_execution(self, gene: str, organism: str) -> Dict[str, Any]:
        """Simulates the execution of an evolved agent targeting a specific fragility trap."""
        return {
            "status": "evolved_execution",
            "target_gene": gene,
            "target_organism": organism,
            "action": "fetching_additional_orthogonal_datasets_to_resolve_discordance"
        }
