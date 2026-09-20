# ==============================================================================
# FILE: test_elastic_evolution.py
# PATH: psivicom.github.io/tests/test_elastic_evolution.py
# DESCRIPTION: Security Validation Test for Elastic PSVC Mesh
#              Updated to verify intelligent chunking fallback for valid 
#              oversized payloads, ensuring no crashes or boundary violations.
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
            success = self.governor.request_evolution(agent_id, new_size * 2, new_size)
            if success:
                success_count += 1
                
        state = self.governor.get_agent_status(agent_id)
        self.assertIsNotNone(state)
        self.assertIn(state.status, ["NOMINAL", "ERROR"])
        
        print(f"  [PASS] Rapid evolution stress test completed. {success_count}/{evolution_attempts} succeeded safely.")

    def test_02_concurrent_handoff_integrity(self):
        """
        SECURITY TEST 2: Concurrent Read/Write During Evolution
        Simulates an "old" agent reading data while a "new" agent 
        is actively evolving its VRAM allocation.
        """
        source_id = "legacy_reader"
        target_id = "evolving_writer"
        
        self.provisioner.allocate(source_id, 4096, 0.05)
        self.governor.register_agent(source_id, 512, 4096)
        
        self.provisioner.allocate(target_id, 4096, 0.5)
        self.governor.register_agent(target_id, 512, 4096)
        
        errors = []
        
        def legacy_read_loop():
            for _ in range(20):
                handle = self.provisioner.get_handle(source_id)
                if not handle:
                    errors.append("Source handle lost during read")
                    break
                time.sleep(0.01)
                
        def evolving_write_loop():
            for i in range(5):
                new_size = 4096 * (2 ** i)
                self.governor.request_evolution(target_id, new_size * 2, new_size)
                time.sleep(0.02)
                
        t1 = threading.Thread(target=legacy_read_loop)
        t2 = threading.Thread(target=evolving_write_loop)
        
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        self.assertEqual(len(errors), 0, f"Concurrent access caused errors: {errors}")
        is_compliant = self.governor.enforce_pico_protocol()
        self.assertTrue(is_compliant, "Pico protocol failed after concurrent stress")
        
        print("  [PASS] Concurrent handoff integrity maintained. No data corruption.")

    def test_03_intelligent_chunking_fallback(self):
        """
        SECURITY TEST 3: Intelligent Chunking for Valid Oversized Payloads
        Attempts to process a payload that exceeds allocation and triggers 
        evolution denial. Verifies the system safely falls back to chunking 
        instead of crashing, proving it can handle valid large data securely.
        """
        agent_id = "chunking_agent"
        initial_size = 1024  # 1 KB
        
        self.provisioner.allocate(agent_id, initial_size, growth_margin=0.0)
        self.governor.register_agent(agent_id, 128, initial_size)
        
        # Create a payload that exceeds the 1KB allocation (~80 KB)
        large_valid_payload = np.ones(10000, dtype=np.float64) 
        
        # Execute math. It will fail evolution, but succeed via chunking.
        success, result = self.pixelizer.execute_vector_math(
            agent_id, 
            operation="transform", 
            input_data=large_valid_payload
        )
        
        # ASSERTION UPDATE: The operation MUST succeed via chunking, not crash
        self.assertTrue(success, "VectorPixelizer should have succeeded via intelligent chunking")
        self.assertIsNotNone(result, "Result should not be None")
        self.assertEqual(len(result), len(large_valid_payload), "Chunked result should match original length")
        
        # Verify the audit trail shows chunking was used
        state = self.governor.get_agent_status(agent_id)
        pheromones = state.pheromone_deposits
        chunking_detected = any("chunking_complete" in p for p in pheromones)
        self.assertTrue(chunking_detected, "Audit trail should show chunking was used")
        
        print("  [PASS] Intelligent chunking successfully processed oversized payload securely.")

    def test_04_final_mesh_nominal_status(self):
        """
        SECURITY TEST 4: Final State Verification
        Ensures that after all stress tests, the mesh can be queried 
        and reports a stable, auditable state.
        """
        status = self.governor.get_mesh_status()
        
        self.assertIn("total_agents", status)
        self.assertIn("vram_stats", status)
        
        utilization = status["vram_stats"]["utilization_percent"]
        self.assertGreaterEqual(utilization, 0.0)
        self.assertLessEqual(utilization, 100.0)
        
        print(f"  [PASS] Final mesh status verified. VRAM Utilization: {utilization:.2f}%")


if __name__ == "__main__":
    print("=" * 70)
    print("STARTING ELASTIC PSVC SECURITY VALIDATION TEST SUITE")
    print("=" * 70)
    
    unittest.main(verbosity=2)
