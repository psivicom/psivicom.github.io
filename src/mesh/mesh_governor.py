# src/mesh/mesh_governor.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Sovereign Mesh Governor: Declarative Resource & Policy Enforcement.
Ingests PSVC manifests to enforce velocity-normalized governance, 
resource limits, and divergence thresholds across the decentralized mesh.
"""

import logging
import time
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from src.core.zulu_clock import get_zulu_timestamp_ms

logger = logging.getLogger("MESH_GOVERNOR")

@dataclass
class PSVCResourceProfile:
    name: str
    cpu_shares: int
    memory_mb: int
    replication: int
    protocol: str
    port: int

@dataclass
class GovernancePolicy:
    strategy: str
    checkpoint_interval_minutes: int
    divergence_threshold: float

class MeshGovernor:
    def __init__(self, mesh, provisioner, manifest_path: str = "config/psvc-manifest.yml"):
        self.mesh = mesh
        self.provisioner = provisioner
        self.manifest_path = Path(manifest_path)
        self.profiles: Dict[str, PSVCResourceProfile] = {}
        self.policy: Optional[GovernancePolicy] = None
        self.velocity_history: Dict[str, List[float]] = {}
        self.violations: List[Dict[str, Any]] = []
        self.pheromones: Dict[str, List[str]] = {}
        
        self._load_manifest()
        logger.info("🛡️ Mesh Governor initialized with declarative policy enforcement.")

    def _load_manifest(self):
        if not self.manifest_path.exists():
            logger.warning(f"⚠️ Manifest not found at {self.manifest_path}. Using default sovereign limits.")
            self.policy = GovernancePolicy(strategy="velocity-normalized", checkpoint_interval_minutes=15, divergence_threshold=0.05)
            return

        try:
            import yaml
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            gov_data = data.get("governance", {})
            self.policy = GovernancePolicy(
                strategy=gov_data.get("strategy", "velocity-normalized"),
                checkpoint_interval_minutes=gov_data.get("checkpoint_interval_minutes", 15),
                divergence_threshold=float(gov_data.get("divergence_threshold", 0.05))
            )
            
            for service in data.get("services", []):
                res = service.get("resources", {})
                net = service.get("network", {})
                profile = PSVCResourceProfile(
                    name=service.get("name"),
                    cpu_shares=res.get("cpu_shares", 10),
                    memory_mb=res.get("memory_mb", 64),
                    replication=service.get("replication", 1),
                    protocol=net.get("protocol", "psvc-binary"),
                    port=net.get("port", 8765)
                )
                self.profiles[profile.name] = profile
                
            logger.info(f"✅ Loaded {len(self.profiles)} PSVC profiles and '{self.policy.strategy}' governance policy.")
        except ImportError:
            logger.error("❌ PyYAML not installed. Run: pip install pyyaml")
        except Exception as e:
            logger.error(f"❌ Failed to load manifest: {e}")

    def register_agent(self, agent_id: str, initial_samples: int, initial_vram: int):
        logger.info(f"📝 Registered agent {agent_id} (samples: {initial_samples}, vram: {initial_vram} bytes).")
        if agent_id not in self.velocity_history:
            self.velocity_history[agent_id] = []

    def request_evolution(self, agent_id: str, new_dimensions: int, new_memory: int) -> bool:
        requested_memory_mb = new_memory / (1024 * 1024)
        base_name = next((name for name in self.profiles.keys() if name in agent_id), None)
        if base_name:
            profile = self.profiles[base_name]
            if requested_memory_mb > profile.memory_mb:
                self._log_violation(agent_id, f"Evolution request {requested_memory_mb:.2f}MB exceeds manifest limit {profile.memory_mb}MB")
                return False
        
        logger.info(f"🧬 Evolution request approved for {agent_id}: {new_dimensions} dimensions, {new_memory} bytes.")
        return True

    def validate_provisioning_request(self, agent_id: str, requested_memory_mb: int) -> bool:
        base_name = next((name for name in self.profiles.keys() if name in agent_id), None)
        if base_name:
            profile = self.profiles[base_name]
            if requested_memory_mb > profile.memory_mb:
                self._log_violation(agent_id, f"Memory request {requested_memory_mb}MB exceeds manifest limit {profile.memory_mb}MB")
                return False
        return True

    def record_metric(self, agent_id: str, metric_value: float):
        if agent_id not in self.velocity_history:
            self.velocity_history[agent_id] = []
        self.velocity_history[agent_id].append(float(metric_value))
        if len(self.velocity_history[agent_id]) > 10:
            self.velocity_history[agent_id].pop(0)

    def check_velocity_divergence(self, agent_id: str) -> bool:
        if not self.policy or self.policy.strategy != "velocity-normalized":
            return True 
            
        history = self.velocity_history.get(agent_id, [])
        if len(history) < 3:
            return True 

        velocities = [abs(history[i] - history[i-1]) for i in range(1, len(history))]
        avg_velocity = float(np.mean(velocities))
        
        if avg_velocity > self.policy.divergence_threshold:
            self._log_violation(agent_id, f"Velocity divergence {avg_velocity:.4f} exceeds threshold {self.policy.divergence_threshold}")
            return False
        return True

    def _log_violation(self, agent_id: str, reason: str):
        violation = {
            "timestamp": get_zulu_timestamp_ms(),
            "agent_id": agent_id,
            "reason": reason,
            "action": "QUARANTINE_OR_REJECT"
        }
        self.violations.append(violation)
        logger.warning(f"🚫 GOVERNANCE VIOLATION: {agent_id} - {reason}")

    def deposit_pheromone(self, agent_id: str, pheromone: str):
        if agent_id not in self.pheromones:
            self.pheromones[agent_id] = []
        if pheromone not in self.pheromones[agent_id]:
            self.pheromones[agent_id].append(pheromone)
            logger.debug(f"🧬 Pheromone deposited on {agent_id}: {pheromone}")

    def get_mesh_status(self) -> Dict[str, Any]:
        """Returns the current status of the mesh, including provisioner and VRAM statistics."""
        
        # 1. Safely get provisioner stats
        if hasattr(self.provisioner, 'get_stats') and callable(self.provisioner.get_stats):
            prov_stats = self.provisioner.get_stats()
        else:
            prov_stats = {
                "average_generation": 0.0,
                "total_allocations": len(self.velocity_history)
            }
        if "average_generation" not in prov_stats:
            prov_stats["average_generation"] = 0.0

        # 2. Safely get VRAM stats
        if hasattr(self.mesh, 'get_vram_stats') and callable(self.mesh.get_vram_stats):
            vram_stats = self.mesh.get_vram_stats()
        else:
            total_vram = getattr(self.mesh, 'total_vram_bytes', 4 * 1024 * 1024 * 1024)
            vram_stats = {
                "utilization_percent": 0.0,
                "total_bytes": total_vram,
                "allocated_bytes": 0
            }
        if "utilization_percent" not in vram_stats:
            vram_stats["utilization_percent"] = 0.0

        # 3. THE CRITICAL RETURN BLOCK: Ensure BOTH keys are explicitly present
        return {
            "policy": self.policy.strategy if self.policy else "default",
            "divergence_threshold": self.policy.divergence_threshold if self.policy else 0.05,
            "active_profiles": len(self.profiles),
            "total_violations": len(self.violations),
            "provisioner_stats": prov_stats,
            "vram_stats": vram_stats,  # <-- THIS IS THE KEY THAT WAS MISSING
            "timestamp": get_zulu_timestamp_ms()
        }
