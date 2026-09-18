"""
AETHER VANGUARD - PSVC Provisioner
License: EUPL 1.2
Purpose: Reads PSIVI RFC .psvc manifests and provisions secure edge containers.
"""
import yaml
import subprocess
import logging
from pathlib import Path

class PSVCProvisioner:
    def __init__(self, manifest_path: str = "config/aether-vanguard.psvc"):
        self.manifest_path = Path(manifest_path)
        self.config = self._load_manifest()
        
    def _load_manifest(self) -> dict:
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"PSVC Manifest not found at {self.manifest_path}")
        with open(self.manifest_path, 'r') as f:
            return yaml.safe_load(f)

    def spawn_pico_node(self, node_id: str, target_vram_mb: int):
        """
        Dynamically adjusts the .psvc manifest for the specific volunteer's 
        hardware and spawns the container using the local psvc runtime.
        """
        logging.info(f"Provisioning PSVC node {node_id} with {target_vram_mb}MB VRAM limit...")
        
        # 1. Inject dynamic VRAM Dim constraints into the spec
        self.config['spec']['resources']['vram_limit_mb'] = target_vram_mb
        self.config['metadata']['name'] = f"aether-pico-{node_id}"
        
        # 2. Write the temporary, node-specific manifest
        temp_manifest = Path(f"/tmp/{node_id}.psvc")
        with open(temp_manifest, 'w') as f:
            yaml.dump(self.config, f)
            
        # 3. Execute the local PSVC runtime (Assuming CLI command 'psvc up')
        # This keeps the orchestration strictly within your RFC-defined ecosystem
        try:
            subprocess.run(
                ["psvc", "up", "-f", str(temp_manifest)], 
                check=True, 
                capture_output=True,
                text=True
            )
            logging.info(f"Successfully deployed {node_id} via PSVC runtime.")
        except FileNotFoundError:
            logging.warning("Local 'psvc' binary not found in PATH. Falling back to Docker simulation.")
            # Fallback for CI/CD testing environments where the actual psvc binary isn't installed
            self._fallback_docker_spawn(node_id)

    def _fallback_docker_spawn(self, node_id: str):
        """Safety fallback for GitHub Actions testing."""
        subprocess.run([
            "docker", "run", "-d", 
            "--name", f"aether-pico-{node_id}",
            "--memory", f"{self.config['spec']['resources']['vram_limit_mb']}m",
            "aether-vanguard:latest",
            "python", "-m", "src.nodes.pico_worker"
        ])
