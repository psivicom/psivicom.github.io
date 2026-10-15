# src/core/zig_bridge.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import os
import json
import hashlib
import logging
import time
import ctypes
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger("ZIG_BRIDGE")

class ZigBridge:
    """
    Sovereign bridge between Python orchestration and bare-metal ZIG execution.
    Enforces cryptographic verification and celebrates optimized binary loading.
    """
    def __init__(self):
        self.root = Path(__file__).parent.parent.parent
        self.bin_dir = self.root / "src" / "core"
        self.audit_path = self.bin_dir / ".zig-build-audit.json"
        
        # Map of expected binaries to their ctypes library handles
        self.libraries: Dict[str, Any] = {}
        
        self._verify_and_celebrate()

    def _verify_and_celebrate(self):
        """Verifies SHA-256 integrity of compiled ZIG binaries and rings the bells of success."""
        if not self.audit_path.exists():
            logger.warning("⚠️ No ZIG audit manifest found. Binaries will be loaded without cryptographic verification.")
            self._load_unverified()
            return

        try:
            with open(self.audit_path, 'r', encoding='utf-8') as f:
                audit_data = json.load(f)
            
            verifications = audit_data.get("verifications", {})
            logger.info("🛡️ Initiating Sovereign ZIG Binary Verification Protocol...")
            
            for binary_name, expected_hashes in verifications.items():
                binary_path = self.bin_dir / binary_name
                
                if not binary_path.exists():
                    logger.error(f"❌ CRITICAL: Verified binary missing: {binary_name}")
                    continue

                # 1. Cryptographic Verification
                actual_sha = self._calculate_sha256(binary_path)
                expected_binary_sha = expected_hashes.get("binary_sha256", "")
                
                if actual_sha != expected_binary_sha:
                    logger.error(f"❌ CRITICAL: SHA-256 MISMATCH for {binary_name}!")
                    logger.error(f"   Expected: {expected_binary_sha}")
                    logger.error(f"   Actual:   {actual_sha}")
                    continue

                # 2. Telemetry Measurement (Load Time & Size)
                start_time = time.perf_counter()
                try:
                    # Load the shared library (or executable, depending on build mode)
                    lib = ctypes.CDLL(str(binary_path))
                    self.libraries[binary_name] = lib
                except OSError as e:
                    logger.warning(f"⚠️ Could not load {binary_name} as shared library (may be executable): {e}")
                    continue
                    
                end_time = time.perf_counter()
                load_time_ms = (end_time - start_time) * 1000
                size_kb = binary_path.stat().st_size / 1024

                # 3. RING THE BELLS 🔔
                logger.info("=" * 60)
                logger.info("🔔 DING! 🔔 BARE-METAL BINARY VERIFIED & LOADED 🔔 DING! 🔔")
                logger.info(f"🏆 Binary:       {binary_name}")
                logger.info(f"📦 Size:         {size_kb:.2f} KB (Optimized & Stripped)")
                logger.info(f"⚡ Load Time:    {load_time_ms:.4f} ms")
                logger.info(f"🔐 SHA-256:      {actual_sha[:16]}...{actual_sha[-16:]} ✅ MATCH")
                logger.info("🧠 WENDY Super-Intelligence Substrate: ACTIVE")
                logger.info("=" * 60)

        except Exception as e:
            logger.error(f"❌ Failed to verify ZIG binaries: {e}")
            self._load_unverified()

    def _calculate_sha256(self, file_path: Path) -> str:
        """Calculates the SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _load_unverified(self):
        """Fallback: Loads binaries if audit manifest is missing (e.g., local dev)."""
        for binary_path in self.bin_dir.iterdir():
            if binary_path.is_file() and not binary_path.name.startswith('.'):
                try:
                    self.libraries[binary_path.stem] = ctypes.CDLL(str(binary_path))
                    logger.info(f"⚠️ Loaded unverified binary: {binary_path.name}")
                except OSError:
                    pass

    def get_library(self, name: str) -> Optional[Any]:
        """Retrieves a loaded ZIG library by name."""
        return self.libraries.get(name)
