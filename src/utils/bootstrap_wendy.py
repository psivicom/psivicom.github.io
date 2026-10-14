# src/utils/bootstrap_wendy.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import os
import getpass
import logging
from pathlib import Path

from src.core.psvc_sovereign import SovereignPSVC

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("WENDY_BOOTSTRAP")

class WendyBootstrap:
    def __init__(self):
        self.config_dir = Path("config")
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        logger.info("🌱 Initiating Wendy Genesis Bootstrap (Sovereign Encrypted Mode)...")
        logger.info("🔑 Generating new sovereign Ed25519 identity...")
        
        # SURGICAL FIX: Prevent GetPassWarning/EOFError in headless CI environments
        if os.environ.get("CI") == "true":
            passphrase = os.environ.get("WENDY_PASSPHRASE", "genesis_bootstrap_ci_default_passphrase_2026")
            logger.info("ℹ️ CI Environment detected. Using secure default passphrase for bootstrap.")
        else:
            try:
                passphrase = getpass.getpass("Enter a strong sovereign passphrase: ")
            except (EOFError, getpass.GetPassWarning):
                logger.warning("⚠️ Terminal does not support secure input. Falling back to default.")
                passphrase = "genesis_bootstrap_fallback_passphrase"

        if not passphrase:
            logger.error("❌ Passphrase cannot be empty.")
            return

        # Generate and seal the sovereign identity
        sovereign = SovereignPSVC({
            "identity": "WENDY_GENESIS",
            "role": "Sovereign Mesh Orchestrator",
            "location": "Goldstream, BC"
        })
        
        # Derive key from passphrase (simplified for bootstrap)
        sovereign._derive_key_from_passphrase(passphrase)
        
        key_path = self.config_dir / "wendy_sovereign_key.psvc"
        sovereign.seal_to_file(str(key_path))
        
        logger.info(f"✅ Sovereign identity sealed and stored at {key_path}")
        logger.info("🏁 Genesis Bootstrap Complete. WENDY is ready.")

if __name__ == "__main__":
    bootstrap = WendyBootstrap()
    bootstrap.run()
