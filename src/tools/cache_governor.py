# src/tools/cache_governor.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import os
import json
import shutil
import logging
import requests
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("CACHE_GOVERNOR")

class CacheGovernor:
    def __init__(self):
        self.token = os.environ.get("GITHUB_TOKEN")
        self.repo = os.environ.get("GITHUB_REPOSITORY", "psivicom/psivicom.github.io")
        self.api_base = f"https://api.github.com/repos/{self.repo}/actions/caches"
        self.archive_dir = Path("data/wendy_memory_archive")
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def purge_remote_bloat(self):
        """Manages remote cache: Preserves heavy ML caches and keeps ONLY the latest Twin continuity state."""
        if not self.token:
            logger.warning("⚠️ GITHUB_TOKEN not found. Skipping remote cache purge.")
            return

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        try:
            response = requests.get(self.api_base, headers=headers)
            response.raise_for_status()
            caches = response.json().get("actions_caches", [])

            # Sort caches by last accessed time (newest first)
            caches.sort(key=lambda x: x.get("last_accessed_at", ""), reverse=True)

            twin_caches_found = []
            purged_count = 0

            for cache in caches:
                key = cache.get("key", "")
                size_in_bytes = cache.get("size_in_bytes", 0)
                cache_id = cache.get("id")

                # 1. PRESERVE: Critical heavy caches (venv, ml-binaries, setup-python)
                if any(protect in key.lower() for protect in ["venv", "ml-binaries", "setup-python"]):
                    continue

                # 2. MANAGE: WENDY Twin Continuity States
                if "wendy-twin" in key:
                    twin_caches_found.append({"id": cache_id, "key": key, "size": size_in_bytes})
                    
                    # Keep the absolute newest Twin cache (index 0 of the sorted list)
                    # Delete all older, orphaned Twin caches to prevent 10GB limit fragmentation
                    if len(twin_caches_found) > 1:
                        delete_url = f"{self.api_base}/{cache_id}"
                        del_response = requests.delete(delete_url, headers=headers)
                        if del_response.status_code == 204:
                            logger.info(f"🗑️ Purged orphaned Twin state: {key} ({size_in_bytes} bytes)")
                            purged_count += 1
                    else:
                        logger.info(f"🧠 Preserved latest Twin continuity state: {key}")
                    continue

                # 3. PURGE: Any other unrecognized small bloat (under 10KB)
                if size_in_bytes < 10240:
                    delete_url = f"{self.api_base}/{cache_id}"
                    requests.delete(delete_url, headers=headers)
                    purged_count += 1

            logger.info(f"🏁 Remote Cache Governance Complete. Purged {purged_count} orphaned fragments. Twin continuity preserved.")

        except Exception as e:
            logger.error(f"❌ Remote cache governance failed: {e}")

    def archive_local_ambiguity(self):
        """Moves low-value local artifacts to the Memory Palace for WENDY's future evaluation."""
        targets_to_archive = [
            Path("reports/temp"),
            Path("data/instruction_queue/processed"),
            Path("logs")
        ]
        
        archived_count = 0
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
        session_archive = self.archive_dir / f"archive_session_{timestamp}"
        session_archive.mkdir(parents=True, exist_ok=True)

        for target in targets_to_archive:
            if target.exists():
                dest = session_archive / target.name
                try:
                    shutil.move(str(target), str(dest))
                    logger.info(f"📦 Archived local ambiguity to Memory Palace: {target} -> {dest}")
                    archived_count += 1
                except Exception as e:
                    logger.warning(f"⚠️ Could not archive {target}: {e}")

        for target in targets_to_archive:
            if target.exists() and target.is_dir() and not any(target.iterdir()):
                target.rmdir()

        logger.info(f"🏁 Local Memory Governance Complete. Archived {archived_count} directories to Memory Palace.")

def main():
    logger.info("🧠 WENDY Autonomous Memory Governor Initializing...")
    governor = CacheGovernor()
    governor.archive_local_ambiguity()
    governor.purge_remote_bloat()
    logger.info("✅ Memory Governance Cycle Complete. WENDY's cognitive footprint is optimized.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    main()
