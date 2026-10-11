# src/mesh/mesh_governor.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Sovereign Mesh Governor: Declarative Resource & Policy Enforcement.
Ingests PSVC manifests to enforce velocity-normalized governance, 
resource limits, and divergence thresholds across the decentralized mesh.
"""

import logging
import threading
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from src.core.zulu_clock import get_zulu_timestamp_ms

logger = logging.getLogger("MESH_GOVERNOR")

@dataclass
class PSVCResourceProfile:
    name: str
    cpu_shares: int = 10
    memory_mb: int = 64
    replication: int = 1
    protocol: str = "psvc-binary"
    port: int = 8765

    def __post_init__(self):
        if self.memory_mb <= 0:
            raise ValueError(f"memory_mb must be positive for profile {self.name}")

@dataclass
class GovernancePolicy:
    strategy: str = "velocity-normalized"
    checkpoint_interval_minutes: int = 15
    divergence_threshold: float = 0.05

class MeshGovernor:
    def __init__(self, mesh, provisioner, manifest_path: str = "config/psvc-manifest.yml"):
        self.mesh = mesh
        self.provisioner = provisioner
        self.manifest_path = Path(manifest_path)
        
        self.profiles: Dict[str, PSVCResourceProfile] = {}
        self.policy: GovernancePolicy = GovernancePolicy()
        
        # Thread-safe state tracking
        self._lock = threading.Lock()
        self.velocity_history: Dict[str, List[float]] = {}
        self.violations: List[Dict[str, Any]] = []
        self.pheromones: Dict[str, List[str]] = {}
        
        self._load_manifest()
        logger.info("🛡️ Mesh Governor initialized with declarative policy enforcement.")

    def _load_manifest(self):
        if not self.manifest_path.exists():
            logger.warning(f"⚠️ Manifest not found at {self.manifest_path}. Using default sovereign limits.")
            return

        try:
            import yaml
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            gov_data = data.get("governance", {})
            if gov_data:
                self.policy = GovernancePolicy(
                    strategy=gov_data.get("strategy", self.policy.strategy),
                    checkpoint_interval_minutes=int(gov_data.get("checkpoint_interval_minutes", self.policy.checkpoint_interval_minutes)),
                    divergence_threshold=float(gov_data.get("divergence_threshold", self.policy.divergence_threshold))
                )
            
            for service in data.get("services", []):
                if not service or "name" not in service:
                    continue
                res = service.get("resources", {}) or {}
                net = service.get("network", {}) or {}
                profile = PSVCResourceProfile(
                    name=service["name"],
                    cpu_shares=int(res.get("cpu_shares", 10)),
                    memory_mb=int(res.get("memory_mb", 64)),
                    replication=int(service.get("replication", 1)),
                    protocol=net.get("protocol", "psvc-binary"),
                    port=int(net.get("port", 8765))
                )
                self.profiles[profile.name] = profile
                
            logger.info(f"✅ Loaded {len(self.profiles)} PSVC profiles and '{self.policy.strategy}' governance policy.")
        except ImportError:
            logger.error("❌ PyYAML not installed. Run: pip install pyyaml")
        except Exception as e:
            logger.error(f"❌ Failed to load manifest: {e}\n{traceback.format_exc()}")

    def _get_profile_for_agent(self, agent_id: str) -> Optional[PSVCResourceProfile]:
        """Finds the most specific (longest matching prefix) profile for an agent."""
        # Sort profile names by length descending to match the most specific profile first
        for name in sorted(self.profiles.keys(), key=len, reverse=True):
            if agent_id.startswith(name) or name in agent_id:
                return self.profiles[name]
        return None

    def register_agent(self, agent_id: str, initial_samples: int, initial_vram: int):
        with self._lock:
            if agent_id not in self.velocity_history:
                self.velocity_history[agent_id] = []
        logger.info(f"📝 Registered agent {agent_id} (samples: {initial_samples}, vram: {initial_vram} bytes).")

    def request_evolution(self, agent_id: str, new_dimensions: int, new_memory: int) -> bool:
        requested_memory_mb = new_memory / (1024 * 1024)
        profile = self._get_profile_for_agent(agent_id)
        
        if profile and requested_memory_mb > profile.memory_mb:
            self._log_violation(agent_id, f"Evolution request {requested_memory_mb:.2f}MB exceeds manifest limit {profile.memory_mb}MB")
            return False
        
        logger.info(f"🧬 Evolution request approved for {agent_id}: {new_dimensions} dimensions, {new_memory} bytes.")
        return True

    def validate_provisioning_request(self, agent_id: str, requested_memory_mb: int) -> bool:
        profile = self._get_profile_for_agent(agent_id)
        if profile and requested_memory_mb > profile.memory_mb:
            self._log_violation(agent_id, f"Memory request {requested_memory_mb}MB exceeds manifest limit {profile.memory_mb}MB")
            return False
        return True

    def record_metric(self, agent_id: str, metric_value: float):
        with self._lock:
            if agent_id not in self.velocity_history:
                self.velocity_history[agent_id] = []
            
            history = self.velocity_history[agent_id]
            history.append(float(metric_value))
            
            # Keep a rolling window of the last 10 metrics
            if len(history) > 10:
                history.pop(0)

    def check_velocity_divergence(self, agent_id: str) -> bool:
        if self.policy.strategy != "velocity-normalized":
            return True 
            
        with self._lock:
            history = self.velocity_history.get(agent_id, [])
            # Need at least 3 data points to calculate 2 velocities
            if len(history) < 3:
                return True 

            # Pure Python calculation - avoids numpy overhead for small lists
            velocities = [abs(history[i] - history[i-1]) for i in range(1, len(history))]
            avg_velocity = sum(velocities) / len(velocities)
        
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
        with self._lock:
            self.violations.append(violation)
        logger.warning(f"🚫 GOVERNANCE VIOLATION: {agent_id} - {reason}")

    def deposit_pheromone(self, agent_id: str, pheromone: str):
        with self._lock:
            if agent_id not in self.pheromones:
                self.pheromones[agent_id] = []
            if pheromone not in self.pheromones[agent_id]:
                self.pheromones[agent_id].append(pheromone)
                logger.debug(f"🧬 Pheromone deposited on {agent_id}: {pheromone}")

    def get_mesh_status(self) -> Dict[str, Any]:
        """Returns a thread-safe snapshot of the current mesh status."""
        
        # 1. Safely get provisioner stats
        prov_stats = {"average_generation": 0.0, "total_allocations": 0}
        if hasattr(self.provisioner, 'get_stats') and callable(self.provisioner.get_stats):
            try:
                raw_stats = self.provisioner.get_stats()
                if isinstance(raw_stats, dict):
                    prov_stats.update(raw_stats)
            except Exception as e:
                logger.debug(f"Failed to fetch provisioner stats: {e}")
        
        with self._lock:
            prov_stats.setdefault("total_allocations", len(self.velocity_history))
            prov_stats.setdefault("average_generation", 0.0)
            violation_count = len(self.violations)

        # 2. Safely get VRAM stats
        vram_stats = {"utilization_percent": 0.0, "total_bytes": 0, "allocated_bytes": 0}
        if hasattr(self.mesh, 'get_vram_stats') and callable(self.mesh.get_vram_stats):
            try:
                raw_vram = self.mesh.get_vram_stats()
                if isinstance(raw_vram, dict):
                    vram_stats.update(raw_vram)
            except Exception as e:
                logger.debug(f"Failed to fetch VRAM stats: {e}")
                
        vram_stats.setdefault("total_bytes", getattr(self.mesh, 'total_vram_bytes', 4 * 1024 * 1024 * 1024))
        vram_stats.setdefault("utilization_percent", 0.0)
        vram_stats.setdefault("allocated_bytes", 0)

        # 3. Return a complete, guaranteed status dictionary
        return {
            "policy": self.policy.strategy,
            "divergence_threshold": self.policy.divergence_threshold,
            "active_profiles": len(self.profiles),
            "total_violations": violation_count,
            "provisioner_stats": prov_stats,
            "vram_stats": vram_stats,
            "timestamp": get_zulu_timestamp_ms()
        }
