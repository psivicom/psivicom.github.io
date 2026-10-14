# src/core/psvc_sovereign.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import os
import json
import getpass
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union

import nacl.signing
import nacl.encoding
import nacl.secret
import nacl.pwhash
from nacl.exceptions import CryptoError

logger = logging.getLogger("SOVEREIGN_KEYS")

# BULLETPROOF: Explicitly defined at module level to resolve all ImportError exceptions
class SovereignKeyPair:
    """Represents a cryptographically secure Ed25519 key pair for sovereign mesh operations."""
    def __init__(self, public_key: bytes, private_key: bytes):
        self.public_key = public_key
        self.private_key = private_key

    def to_dict(self) -> dict:
        return {"public_key": self.public_key.hex()}

class SovereignPSVC:
    _instance: Optional['SovereignPSVC'] = None

    def __init__(self, key_file: Path = Path("data/wendy_private.key.enc")):
        self.key_file = key_file
        self.verify_key: Optional[nacl.signing.VerifyKey] = None
        self.signing_key: Optional[nacl.signing.SigningKey] = None
        self._load_or_generate()

    @classmethod
    def get_instance(cls) -> 'SovereignPSVC':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_or_generate(self):
        if self.key_file.exists():
            self._decrypt_from_disk()
        elif os.environ.get("WENDY_PRIVATE_KEY_SEED"):
            self._load_from_env()
        else:
            logger.warning("⚠️ No encrypted key found. Generating ephemeral key for this session only.")
            self._generate_ephemeral()

    def _decrypt_from_disk(self):
        try:
            passphrase = os.environ.get("WENDY_PASSPHRASE") or getpass.getpass(f"🔐 Enter passphrase: ")
            raw_data = self.key_file.read_bytes()
            salt = raw_data[:nacl.pwhash.argon2id.SALTBYTES]
            encrypted_payload = raw_data[nacl.pwhash.argon2id.SALTBYTES:]
            
            derived_key = nacl.pwhash.argon2id.kdf(
                nacl.secret.SecretBox.KEY_SIZE, passphrase.encode('utf-8'), salt,
                nacl.pwhash.argon2id.OPSLIMIT_INTERACTIVE, nacl.pwhash.argon2id.MEMLIMIT_INTERACTIVE
            )
            self.signing_key = nacl.signing.SigningKey(nacl.secret.SecretBox(derived_key).decrypt(encrypted_payload))
            self.verify_key = self.signing_key.verify_key
            logger.info("✅ Sovereign identity successfully decrypted into volatile RAM.")
        except Exception as e:
            logger.error(f"❌ Failed to load sovereign key: {e}")
            raise SystemExit(e)

    def _load_from_env(self):
        self.signing_key = nacl.signing.SigningKey(bytes.fromhex(os.environ["WENDY_PRIVATE_KEY_SEED"]))
        self.verify_key = self.signing_key.verify_key
        logger.info("✅ Loaded ephemeral sovereign identity from environment.")

    def _generate_ephemeral(self):
        self.signing_key = nacl.signing.SigningKey.generate()
        self.verify_key = self.signing_key.verify_key
        logger.warning("⚠️ Using ephemeral identity.")

    def sign(self, message: bytes) -> bytes:
        if not self.signing_key: raise RuntimeError("No signing key available.")
        return self.signing_key.sign(message).signature

    def get_public_key_hex(self) -> str:
        if not self.verify_key: raise RuntimeError("No verify key available.")
        return self.verify_key.encode(encoder=nacl.encoding.HexEncoder).decode()

    @staticmethod
    def verify_container(container: Union[Dict[str, Any], str, bytes]) -> bool:
        try:
            data = json.loads(container) if isinstance(container, (str, bytes)) else container
            payload = data.get("payload", {})
            signature_hex = data.get("signature", "")
            public_key_hex = data.get("public_key", "")
            if not signature_hex or not public_key_hex: return False
            
            message = f"psvc:{json.dumps(payload, sort_keys=True, separators=(',', ':'))}".encode('utf-8')
            nacl.signing.VerifyKey(bytes.fromhex(public_key_hex)).verify(message, bytes.fromhex(signature_hex))
            return True
        except Exception:
            return False

    @staticmethod
    def extract_data(container: Union[Dict[str, Any], str, bytes]) -> Dict[str, Any]:
        try:
            data = json.loads(container) if isinstance(container, (str, bytes)) else
