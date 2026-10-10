# src/utils/bootstrap_wendy.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Genesis Bootstrap Script: The Seed of the Mesh (Encrypted at Rest).
Generates an Ed25519 identity and encrypts it at rest using Argon2id.
The plaintext private key NEVER touches the disk.
"""

import json
import logging
import os
import sys
import getpass
from pathlib import Path

from src.core.zulu_clock import get_zulu_timestamp_ms

try:
    import nacl.signing
    import nacl.encoding
    import nacl.secret
    import nacl.pwhash
    import nacl.utils
    NACL_AVAILABLE = True
except ImportError:
    NACL_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("GENESIS_BOOTSTRAP")

class WendyBootstrap:
    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir).resolve()
        self.data_dir = self.root / "data"
        self.key_path = self.data_dir / "wendy_private.key.enc" # Encrypted extension

    def run(self):
        logger.info("🌱 Initiating Wendy Genesis Bootstrap (Sovereign Encrypted Mode)...")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        if self.key_path.exists():
            logger.info("🔑 Encrypted sovereign identity already exists. Skipping generation.")
            return

        if not NACL_AVAILABLE:
            logger.error("❌ PyNaCl is required. Run: pip install pynacl")
            sys.exit(1)

        logger.info("🔑 Generating new sovereign Ed25519 identity...")
        signing_key = nacl.signing.SigningKey.generate()
        raw_key_bytes = signing_key.encode()

        # Prompt user for a passphrase to encrypt the key at rest
        print("\n" + "="*60)
        print("🔐 SOVEREIGN PASSPHRASE SETUP")
        print("="*60)
        print("Your private key will be encrypted on disk using Argon2id.")
        print("You will need this passphrase every time the mesh node starts.")
        print("If you lose it, the key is unrecoverable.\n")
        
        passphrase = getpass.getpass("Enter a strong sovereign passphrase: ")
        if not passphrase:
            logger.error("❌ Passphrase cannot be empty.")
            sys.exit(1)
            
        confirm = getpass.getpass("Confirm passphrase: ")
        if passphrase != confirm:
            logger.error("❌ Passphrases do not match.")
            sys.exit(1)

        # Encrypt the key using Argon2id KDF and SecretBox
        logger.info("🔒 Deriving encryption key via Argon2id and encrypting...")
        salt = nacl.utils.random(nacl.pwhash.argon2id.SALTBYTES)
        opslimit = nacl.pwhash.argon2id.OPSLIMIT_INTERACTIVE
        memlimit = nacl.pwhash.argon2id.MEMLIMIT_INTERACTIVE
        
        derived_key = nacl.pwhash.argon2id.kdf(
            nacl.secret.SecretBox.KEY_SIZE, 
            passphrase.encode('utf-8'), 
            salt, 
            opslimit, 
            memlimit
        )
        
        box = nacl.secret.SecretBox(derived_key)
        encrypted_payload = box.encrypt(raw_key_bytes)

        # Save salt + encrypted payload to disk (Plaintext key is wiped from RAM immediately)
        self.key_path.write_bytes(salt + encrypted_payload)
        
        # Enforce strict Unix permissions
        try:
            os.chmod(self.key_path, 0o600)
        except Exception:
            pass
            
        logger.info("✅ Sovereign identity generated, encrypted at rest, and secured.")
        logger.info(f"📂 Encrypted key saved to: {self.key_path.relative_to(self.root)}")
        print("="*60 + "\n")

if __name__ == "__main__":
    bootstrap = WendyBootstrap()
    bootstrap.run()
