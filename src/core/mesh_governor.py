"""
Mesh Governor for Evolutionary State Tracking and Security Enforcement
Monitors agent evolution and enforces pico protocol compliance
NIST SP 800-218 Compliant | FAIR Open Science | EUPL-1.2 Licensed
"""

import logging
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AgentState:
    """Tracks the evolutionary state of an agent"""
    agent_id: str
    current_generation: int
    last_evolution_time: float
    vector_dimensions: int
    memory_footprint: int
    status: str  # "NOMINAL", "EVOLVING", "ERROR"
    pheromone_deposits: List[str]


class MeshGovernor:
    """
    Enforces pico protocol and tracks agent evolution
    Ensures FAIR compliance and security boundaries
    """
    
    def __init__(self, vram_mesh, provisioner, state_file: str = "mesh_state.json"):
        self.vram_mesh = vram_mesh
        self.provisioner = provisioner
        self.state_file = Path(state_file)
        self.agent_states: Dict[str, AgentState] = {}
        self.evolution_thresholds = {
            "max_generations_per_hour": 10,
            "max_memory_growth_percent": 50,
            "min_time_between_evolutions": 60  # seconds
        }
        
        # Load existing state if available
        self._load_state()
        
        logger.info("Mesh Governor initialized")
    
    def register_agent(self, agent_id: str, initial_dimensions: int, 
                      initial_memory: int) -> AgentState:
        """
        Register a new agent with the governor
        
        Args:
            agent_id: Unique agent identifier
            initial_dimensions: Initial vector dimensions
            initial_memory: Initial memory footprint in bytes
            
        Returns:
            AgentState object
        """
        state = AgentState(
            agent_id=agent_id,
            current_generation=1,
            last_evolution_time=time.time(),
            vector_dimensions=initial_dimensions,
            memory_footprint=initial_memory,
            status="NOMINAL",
            pheromone_deposits=[]
        )
        
        self.agent_states[agent_id] = state
        self._save_state()
        
        logger.info(f"Registered agent {agent_id} (generation 1)")
        return state
    
    def request_evolution(self, agent_id: str, new_dimensions: int, 
                         new_memory: int) -> bool:
        """
        Request evolution for an agent (with security checks)
        
        Args:
            agent_id: Agent identifier
            new_dimensions: New vector dimensions
            new_memory: New memory requirement
            
        Returns:
            True if evolution is allowed and executed
        """
        if agent_id not in self.agent_states:
            logger.error(f"Agent {agent_id} not registered")
            return False
        
        state = self.agent_states[agent_id]
        
        # SECURITY CHECK 1: Rate limiting
        time_since_last = time.time() - state.last_evolution_time
        if time_since_last < self.evolution_thresholds["min_time_between_evolutions"]:
            logger.warning(f"Agent {agent_id} evolving too frequently")
            return False
        
        # SECURITY CHECK 2: Memory growth limits
        growth_percent = ((new_memory - state.memory_footprint) / 
                         state.memory_footprint) * 100
        if growth_percent > self.evolution_thresholds["max_memory_growth_percent"]:
            logger.warning(f"Agent {agent_id} requesting excessive memory growth: {growth_percent}%")
            return False
        
        # Mark as evolving
        state.status = "EVOLVING"
        self._save_state()
        
        try:
            # Execute evolution via provisioner
            success = self.provisioner.evolve(agent_id, new_memory)
            
            if success:
                # Update state
                state.current_generation += 1
                state.vector_dimensions = new_dimensions
                state.memory_footprint = new_memory
                state.last_evolution_time = time.time()
                state.status = "NOMINAL"
                
                logger.info(f"Agent {agent_id} evolved to generation {state.current_generation}")
            else:
                state.status = "ERROR"
                logger.error(f"Evolution failed for agent {agent_id}")
            
            self._save_state()
            return success
            
        except Exception as e:
            state.status = "ERROR"
            self._save_state()
            logger.error(f"Evolution error for agent {agent_id}: {e}")
            return False
    
    def deposit_pheromone(self, agent_id: str, pheromone: str) -> bool:
        """
        Record a pheromone deposit from an agent
        
        Args:
            agent_id: Agent identifier
            pheromone: Pheromone identifier/message
            
        Returns:
            True if recorded successfully
        """
        if agent_id not in self.agent_states:
            return False
        
        state = self.agent_states[agent_id]
        state.pheromone_deposits.append(f"{time.time()}:{pheromone}")
        
        # Keep only last 100 pheromones
        if len(state.pheromone_deposits) > 100:
            state.pheromone_deposits = state.pheromone_deposits[-100:]
        
        self._save_state()
        return True
    
    def get_agent_status(self, agent_id: str) -> Optional[AgentState]:
        """Get current status of an agent"""
        return self.agent_states.get(agent_id)
    
    def scan_for_violations(self) -> List[Dict]:
        """
        Scan mesh for security violations and protocol breaches
        
        Returns:
            List of violation reports
        """
        violations = []
        
        for agent_id, state in self.agent_states.items():
            # Check for stale agents
            if time.time() - state.last_evolution_time > 3600:  # 1 hour
                violations.append({
                    "agent_id": agent_id,
                    "type": "STALE_AGENT",
                    "severity": "WARNING",
                    "message": "Agent has not evolved in over 1 hour"
                })
            
            # Check for error states
            if state.status == "ERROR":
                violations.append({
                    "agent_id": agent_id,
                    "type": "ERROR_STATE",
                    "severity": "CRITICAL",
                    "message": "Agent is in error state"
                })
            
            # Check VRAM allocation consistency
            handle = self.provisioner.get_handle(agent_id)
            if handle and handle.size_bytes != state.memory_footprint:
                violations.append({
                    "agent_id": agent_id,
                    "type": "MEMORY_MISMATCH",
                    "severity": "WARNING",
                    "message": f"Governor state ({state.memory_footprint}) != Provisioner state ({handle.size_bytes})"
                })
        
        return violations
    
    def enforce_pico_protocol(self) -> bool:
        """
        Enforce pico protocol compliance across the mesh
        
        Returns:
            True if all checks pass
        """
        violations = self.scan_for_violations()
        
        critical_violations = [v for v in violations if v["severity"] == "CRITICAL"]
        
        if critical_violations:
            logger.error(f"Pico protocol violation detected: {len(critical_violations)} critical issues")
            for v in critical_violations:
                logger.error(f"  - {v['agent_id']}: {v['message']}")
            return False
        
        logger.info("Pico protocol enforcement: PASSED")
        return True
    
    def _load_state(self):
        """Load agent state from disk"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    for agent_id, state_data in data.get("agents", {}).items():
                        self.agent_states[agent_id] = AgentState(**state_data)
                logger.info(f"Loaded state for {len(self.agent_states)} agents")
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
    
    def _save_state(self):
        """Save agent state to disk"""
        try:
            data = {
                "timestamp": time.time(),
                "agents": {
                    agent_id: asdict(state) 
                    for agent_id, state in self.agent_states.items()
                }
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def get_mesh_status(self) -> Dict:
        """Get overall mesh status"""
        return {
            "total_agents": len(self.agent_states),
            "nominal_agents": sum(1 for s in self.agent_states.values() if s.status == "NOMINAL"),
            "evolving_agents": sum(1 for s in self.agent_states.values() if s.status == "EVOLVING"),
            "error_agents": sum(1 for s in self.agent_states.values() if s.status == "ERROR"),
            "vram_stats": self.vram_mesh.get_stats(),
            "provisioner_stats": self.provisioner.get_evolution_stats()
        }
