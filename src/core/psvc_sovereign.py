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
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, Union

import nacl.signing
import nacl.encoding
import nacl.secret
import nacl.pwhash
from nacl.exceptions import CryptoError

logger = logging.getLogger("SOVEREIGN_KEYS")

# SURGICAL FIX: Add SovereignKeyPair class to resolve ImportError in mesh_node, robotic_bridge, and governor_agent
class SovereignKeyPair:
    """Represents a cryptographically secure Ed25519 key pair for sovereign mesh operations."""
    def __init__(self, public_key: bytes, private_key: bytes):
        self.public_key = public_key
        self.private_key = private_key

    def to_dict(self) -> dict:
        return {
            "public_key": self.public_key.hex(),
            # Private key is intentionally omitted from dict serialization for security
        }

class SovereignPSVC:
    """Manages sovereign identity and cryptographic integrity of PSVC containers."""
    # Class-level cache for the ephemeral/loaded instance
    _instance: Optional['SovereignPSVC'] = None

    def __init__(self, key_file: Path = Path("data/wendy_private.key.enc")):
        self.key_file = key_file
        self.verify_key: Optional[nacl.signing.VerifyKey] = None
        self.signing_key: Optional[nacl.signing.SigningKey] = None
        self._load_or_generate()

    @classmethod
    def get_instance(cls) -> 'SovereignPSVC':
        """Singleton accessor for the sovereign identity."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_or_generate(self):
        if self.key_file.exists():
            self._decrypt_from_disk()
        else:
            if os.environ.get("WENDY_PRIVATE_KEY_SEED"):
                self._load_from_env()
            else:
                logger.warning("⚠️ No encrypted key found. Generating ephemeral key for this session only.")
                self._generate_ephemeral()

    def _decrypt_from_disk(self):
        try:
            env_passphrase = os.environ.get("WENDY_PASSPHRASE")
            if env_passphrase:
                passphrase = env_passphrase
            else:
                passphrase = getpass.getpass(f"🔐 Enter passphrase to unlock {self.key_file.name}: ")
            
            raw_data = self.key_file.read_bytes()
            salt_len = nacl.pwhash.argon2id.SALTBYTES
            salt = raw_data[:salt_len]
            encrypted_payload = raw_data[salt_len:]
            
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
        seed_hex = os.environ["WENDY_PRIVATE_KEY_SEED"]
        self.signing_key = nacl.signing.SigningKey(bytes.fromhex(seed_hex))
        self.verify_key = self.signing_key.verify_key
        logger.info("✅ Loaded ephemeral sovereign identity from environment.")

    def _generate_ephemeral(self):
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

    # =========================================================================
    # STATIC/CLASS METHODS EXPECTED BY VOLUNTEER_WORKER.PY
    # =========================================================================

    @staticmethod
    def verify_container(container: Union[Dict[str, Any], str, bytes]) -> bool:
        """Verifies the Ed25519 signature of a PSVC container (Expected by volunteer_worker)."""
        try:
            if isinstance(container, str):
                data = json.loads(container)
            elif isinstance(container, bytes):
                data = json.loads(container.decode('utf-8'))
            else:
                data = container

            payload = data.get("payload", {})
            signature_hex = data.get("signature", "")
            public_key_hex = data.get("public_key", "")

            if not signature_hex or not public_key_hex:
                logger.warning("⚠️ Container missing signature or public key.")
                return False

            # Reconstruct the message that was signed
            payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            message = f"psvc:{payload_str}".encode('utf-8')
            signature_bytes = bytes.fromhex(signature_hex)

            # Verify using the public key from the container
            verify_key = nacl.signing.VerifyKey(bytes.fromhex(public_key_hex))
            verify_key.verify(message, signature_bytes)
            
            logger.debug("✅ PSVC container signature cryptographically verified.")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to verify PSVC container: {e}")
            return False

    @staticmethod
    def extract_data(container: Union[Dict[str, Any], str, bytes]) -> Dict[str, Any]:
        """Extracts the verified payload from a PSVC container."""
        try:
            if isinstance(container, str):
                return json.loads(container).get("payload", {})
            elif isinstance(container, bytes):
                return json.loads(container.decode('utf-8')).get("payload", {})
            else:
                return container.get("payload", {})
        except Exception as e:
            logger.error(f"❌ Failed to extract data from container: {e}")
            return {}

    def create_container(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> bytes:
        """Creates a signed PSVC container using the loaded sovereign identity."""
        payload_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        message = f"psvc:{payload_str}".encode('utf-8')
        signature_hex = self.sign(message).hex()
        
        container = {
            "version": "1.0.0",
            "type": "psvc",
            "metadata": metadata or {},
            "payload": data,
            "signature": signature_hex,
            "public_key": self.get_public_key_hex()
        }
        
        return json.dumps(container, indent=2).encode('utf-8')
