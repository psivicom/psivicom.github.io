# src/core/psvc_sovereign.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Sovereign PSVC Factory (Encrypted at Rest).
Loads the Ed25519 private key from an Argon2id-encrypted file into volatile RAM.
Supports environment variables for automated CI/CD (GitHub Actions).
"""

import os
import json
import getpass
import logging
from pathlib import Path
from typing import Optional

import nacl.signing
import nacl.encoding
import nacl.secret
import nacl.pwhash
from nacl.exceptions import CryptoError

logger = logging.getLogger("SOVEREIGN_KEYS")

class SovereignKeyPair:
    def __init__(self, key_file: Path = Path("data/wendy_private.key.enc")):
        self.key_file = key_file
        self.verify_key: Optional[nacl.signing.VerifyKey] = None
        self.signing_key: Optional[nacl.signing.SigningKey] = None
        
        self._load_or_generate()

    def _load_or_generate(self):
        if self.key_file.exists():
            self._decrypt_from_disk()
        else:
            # Fallback for legacy unencrypted keys or CI/CD ephemeral generation
            if os.environ.get("WENDY_PRIVATE_KEY_SEED"):
                self._load_from_env()
            else:
                logger.warning("⚠️ No encrypted key found. Generating ephemeral key for this session only.")
                self._generate_ephemeral()

    def _decrypt_from_disk(self):
        """Decrypts the key from disk into volatile RAM using a passphrase."""
        try:
            # 1. Check for CI/CD environment variable first
            env_passphrase = os.environ.get("WENDY_PASSPHRASE")
            if env_passphrase:
                passphrase = env_passphrase
            else:
                # 2. Prompt human volunteer
                passphrase = getpass.getpass(f"🔐 Enter passphrase to unlock {self.key_file.name}: ")

            # Read salt and encrypted payload
            raw_data = self.key_file.read_bytes()
            salt_len = nacl.pwhash.argon2id.SALTBYTES
            salt = raw_data[:salt_len]
            encrypted_payload = raw_data[salt_len:]

            # Derive key and decrypt
            derived_key = nacl.pwhash.argon2id.kdf(
                nacl.secret.SecretBox.KEY_SIZE, 
                passphrase.encode('utf-8'), 
                salt, 
                nacl.pwhash.argon2id.OPSLIMIT_INTERACTIVE, 
                nacl.pwhash.argon2id.MEMLIMIT_INTERACTIVE
            )
            
            box = nacl.secret.SecretBox(derived_key)
            raw_key_bytes = box.decrypt(encrypted_payload)
            
            self.signing_key = nacl.signing.SigningKey(raw_key_bytes)
            self.verify_key = self.signing_key.verify_key
            logger.info("✅ Sovereign identity successfully decrypted into volatile RAM.")
            
        except CryptoError:
            logger.error("❌ FATAL: Invalid passphrase or corrupted key file.")
            raise SystemExit("Mesh cannot start without valid sovereign identity.")
        except Exception as e:
            logger.error(f"❌ Failed to load sovereign key: {e}")
            raise SystemExit(e)

    def _load_from_env(self):
        """Loads key from GitHub Actions secret (Ephemeral CI/CD mode)."""
        seed_hex = os.environ["WENDY_PRIVATE_KEY_SEED"]
        self.signing_key = nacl.signing.SigningKey(bytes.fromhex(seed_hex))
        self.verify_key = self.signing_key.verify_key
        logger.info("✅ Loaded ephemeral sovereign identity from environment.")

    def _generate_ephemeral(self):
        """Generates a temporary key that will die when the process ends."""
        self.signing_key = nacl.signing.SigningKey.generate()
        self.verify_key = self.signing_key.verify_key
        logger.warning("⚠️ Using ephemeral identity. This node will not be recognized on restart.")

    def sign(self, message: bytes) -> bytes:
        if not self.signing_key:
            raise RuntimeError("No signing key available in RAM.")
        return self.signing_key.sign(message).signature

    def get_public_key_hex(self) -> str:
        if not self.verify_key:
            raise RuntimeError("No verify key available.")
        return self.verify_key.encode(encoder=nacl.encoding.HexEncoder).decode()
