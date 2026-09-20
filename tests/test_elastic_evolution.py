# ==============================================================================
# FILE: test_elastic_evolution.py
# PATH: psivicom.github.io/tests/test_elastic_evolution.py
# DESCRIPTION: Security Validation Test for Elastic PSVC Mesh
#              Complete file ready to paste. Includes agent imports from src/agents/.
# LICENSE: EUPL-1.2 | COMPLIANCE: NIST SP 800-218, FAIR Open Science
# ==============================================================================

import unittest
import sys
import os
import time
import threading
import numpy as np

# Ensure the root directory is in the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vram_mesh import VRAMMesh
from src.orchestrator.psvc_provisioner import ElasticPSVCProvisioner
from mesh_governor import MeshGovernor
from src.core.vector_pixelizer import VectorPixelizer

# Import agents from their new location in src/agents/
from src.agents.satellite_agent import SatelliteAgent
from src.agents.forage_agent import ForageAgent


class TestElasticEvolutionSecurity(unittest.TestCase):
    """
    Security and stress tests for the Elastic PSVC Architecture.
    Verifies that the mesh remains NOMINAL under extreme conditions.
    """
    
    def setUp(self):
        """Initialize a controlled, small VRAM environment for fast testing."""
        self.vram_size = 32 * 1024 * 1024  # 32 MB
        self.vram_mesh = VRAMMesh(total_vram_bytes=self.vram_size)
        self.provisioner = ElasticPSVCProvisioner(self.vram_mesh, growth_margin_default=0.2)
        self.governor = MeshGovernor(self.vram_mesh, self.provisioner, state_file="test_mesh_state.json")
        self.pixelizer = VectorPixelizer(self.vram_mesh, self.provisioner, self.governor)
        
        print(f"\n[SETUP] Initialized test mesh with {self.vram_size / (1024*1024):.2f} MB VRAM")

    def tearDown(self):
        """Clean up and verify no memory leaks or lingering error states."""
        for agent_id in list(self.governor.agent_states.keys()):
            self.provisioner.release(agent_id)
            
        if os.path.exists("test_mesh_state.json"):
            os.remove("test_mesh_state.json")
            
        print("[TEARDOWN] Test environment cleaned up securely.")

    def test_01_rapid_evolution_stress(self):
        """
        SECURITY TEST 1: Rapid Evolution
        Forces an agent to request multiple rapid size increases.
        Verifies that the Governor's rate-limiting handles it without corruption.
        """
        agent_id = "stress_test_agent"
        initial_size = 1024 * 10  # 10 KB
        
        self.provisioner.allocate(agent_id, initial_size, growth_margin=0.1)
        self.governor.register_agent(agent_id, initial_size, initial_size)
        
        evolution_attempts = 5
        success_count = 0
        
        for i in range(evolution_attempts):
            new_size = initial_size * (2 ** (i + 1))
            success = self.governor.request_evolution(agent_id, new_size * 2
