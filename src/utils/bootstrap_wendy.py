# src/utils/bootstrap_wendy.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Genesis Bootstrap Script: The Seed of the Mesh.
Idempotently initializes a new volunteer node with sovereign identity,
baseline metabolic state, and mesh configuration. 
Private keys are generated locally and NEVER transmitted.
"""

import json
import logging
import os
import sys
from pathlib import Path

from src.core.zulu_clock import get_zulu_timestamp_ms

# Attempt to import pynacl for sovereign key generation
try:
    import nacl.signing
    import nacl.encoding
    NACL_AVAILABLE = True
except ImportError:
    NACL_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("GENESIS_BOOTSTRAP")

class WendyBootstrap:
    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir).resolve()
        self.data_dir = self.root / "data"
        self.config_dir = self.root / "config"
        self.src_dir = self.root / "src"
        
        self.key_path = self.data_dir / "wendy_private.key"
        self.metabolism_path = self.src_dir / "wendy_metabolism.json"
        self.peer_registry_path = self.data_dir / "peer_registry.json"

    def run(self):
        """Executes the full idempotent bootstrap sequence."""
        logger.info("🌱 Initiating Wendy Genesis Bootstrap...")
        logger.info(f"📂 Root directory: {self.root}")
        
        # 1. Ensure directories exist
        for d in [self.data_dir, self.config_dir, self.src_dir]:
            d.mkdir(parents=True, exist_ok=True)
            
        # 2. Generate Sovereign Identity (Idempotent)
        self._initialize_sovereign_identity()
        
        # 3. Seed Metabolic State (Idempotent)
        self._seed_metabolic_state()
        
        # 4. Initialize Peer Registry (Idempotent)
        self._initialize_peer_registry()
        
        # 5. Final Instructions
        self._print_launch_instructions()
        
        logger.info("✅ Genesis Bootstrap complete. Node is ready to join the mesh.")

    def _initialize_sovereign_identity(self):
        """Generates Ed25519 key pair if it does not already exist."""
        if self.key_path.exists():
            logger.info("🔑 Sovereign identity already exists. Skipping generation.")
            # Enforce strict permissions on existing key
            try:
                os.chmod(self.key_path, 0o600)
            except Exception:
                pass
            return

        if not NACL_AVAILABLE:
            logger.error("❌ PyNaCl is required for sovereign key generation.")
            logger.error("   Please run: pip install pynacl")
            sys.exit(1)

        logger.info("🔑 Generating new sovereign Ed25519 identity...")
        signing_key = nacl.signing.SigningKey.generate()
        
        # Save private key locally (NEVER uploaded)
        self.key_path.write_text(
            signing_key.encode(encoder=nacl.encoding.HexEncoder).decode(), 
            encoding='utf-8'
        )
        
        # Enforce strict Unix permissions (read/write for owner only)
        try:
            os.chmod(self.key_path, 0o600)
        except Exception:
            logger.warning("⚠️ Could not set 0o600 permissions on key file (Windows environment?).")
            
        logger.info("✅ Sovereign identity generated and secured locally.")

    def _seed_metabolic_state(self):
        """Creates the baseline wendy_metabolism.json if it does not exist."""
        if self.metabolism_path.exists():
            logger.info("🧠 Metabolic state already exists. Skipping seed.")
            return

        logger.info("🧠 Seeding baseline metabolic state...")
        genesis_state = {
            "version": "8.0-sovereign",
            "updated_at": get_zulu_timestamp_ms(),
            "phase": "IDLE",
            "intensity": 0.5,
            "action": "BOOTSTRAP_COMPLETE",
            "reason": "Genesis initialization",
            "should_act": False,
            "total_cycles_completed": 0,
            "period_minutes": 10
        }
        
        self.metabolism_path.write_text(json.dumps(genesis_state, indent=2), encoding='utf-8')
        logger.info("✅ Metabolic state seeded.")

    def _initialize_peer_registry(self):
        """Creates an empty peer registry for the gossip protocol."""
        if self.peer_registry_path.exists():
            logger.info("🤝 Peer registry already exists. Skipping.")
            return

        logger.info("🤝 Initializing empty peer registry for gossip protocol...")
        registry = {
            "updated_at": get_zulu_timestamp_ms(),
            "known_peers": [
                # Add default bootstrap nodes here if desired
                # "http://goldstream-primary.psivi.com:8080/api/mesh"
            ]
        }
        
        self.peer_registry_path.write_text(json.dumps(registry, indent=2), encoding='utf-8')
        logger.info("✅ Peer registry initialized.")

    def _print_launch_instructions(self):
        """Outputs the final commands to start the mesh node."""
        print("\n" + "="*70)
        print("🌟 WENDY GENESIS COMPLETE 🌟")
        print("="*70)
        print("Your node has been securely initialized with a sovereign identity.")
        print(f"Your private key is safe at: {self.key_path.relative_to(self.root)} (Permissions: 0o600)")
        print("\nTo launch the mesh node daemon, run:")
        print("  python src/mesh/mesh_node.py")
        print("\nTo verify your node is broadcasting, check the logs for:")
        print("  'Mesh Node initialized. Sovereign systems online.'")
        print("="*70 + "\n")


if __name__ == "__main__":
    bootstrap = WendyBootstrap()
    bootstrap.run()
