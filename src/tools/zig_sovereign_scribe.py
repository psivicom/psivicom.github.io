# src/tools/zig_sovereign_scribe.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import shutil
from pathlib import Path
import logging
import subprocess
import sys

logger = logging.getLogger("ZIG_SOVEREIGN_SCRIBE")

def sync_zig_architecture():
    root = Path(__file__).parent.parent.parent
    core_dir = root / "src" / "core"
    uncommented_dir = root / "docs" / "ZIG_UNCOMMENTED_SOURCE"
    commented_dir = root / "docs" / "ZIG_COMMENTED_SOURCE"
    
    uncommented_dir.mkdir(parents=True, exist_ok=True)
    commented_dir.mkdir(parents=True, exist_ok=True)
    
    if not core_dir.exists():
        logger.info("ℹ️ src/core not found. ZIG Scribe dormant.")
        return

    zig_files = list(core_dir.glob("*.zig"))
    logger.info(f"📜 ZIG Sovereign Scribe initializing. Syncing {len(zig_files)} files...")
    
    synced_count = 0
    for zig_file in zig_files:
        name = zig_file.stem
        
        dest_uncommented = uncommented_dir / f"{name}.zig"
        shutil.copy2(zig_file, dest_uncommented)
        
        dest_commented = commented_dir / f"{name}.md"
        code_content = zig_file.read_text(encoding='utf-8')
        
        # SAFE STRING CONCATENATION: Prevents Markdown parser conflicts
        md_content = (
            f"# {name.replace('_', ' ').title()} - WENDY Bare-Metal ZIG Module\n\n"
            f"> **SOVEREIGN PROTOCOL ENFORCED**: This file is the pristine, human-readable master source.\n"
            f"> **Auto-Synced**: Any modifications to `src/core/{name}.zig` are automatically reflected here.\n\n"
            f"## Source Code\n\n"
            f"```zig\n{code_content}\n```\n"
        )
        
        dest_commented.write_text(md_content, encoding='utf-8')
        logger.info(f"✅ Synced {name} -> docs/")
        synced_count += 1

    logger.info(f"🏁 ZIG Sovereign Scribe complete. {synced_count} files synchronized.")
    
    try:
        subprocess.check_call(["git", "config", "user.name", "PSIVI ZIG Scribe"])
        subprocess.check_call(["git", "config", "user.email", "zig-scribe@psivi.com"])
        subprocess.check_call(["git", "add", "docs/ZIG_UNCOMMENTED_SOURCE/", "docs/ZIG_COMMENTED_SOURCE/"])
        
        result = subprocess.run(["git", "diff", "--staged", "--quiet"], capture_output=True)
        if result.returncode != 0:
            subprocess.check_call(["git", "commit", "-m", "docs: autonomous ZIG scribe synchronized documentation [skip ci]"])
            
            for i in range(1, 4):
                try:
                    subprocess.check_call(["git", "pull", "--rebase", "origin", "main"])
                    subprocess.check_call(["git", "push", "origin", "main"])
                    logger.info("✅ ZIG documentation committed and pushed.")
                    break
                except subprocess.CalledProcessError:
                    logger.warning(f"⚠️ Push failed. Retrying in 2s... ({i}/3)")
                    import time
                    time.sleep(2)
        else:
            logger.info("ℹ️ ZIG documentation already up to date.")
    except Exception as e:
        logger.warning(f"⚠️ Git commit failed (may be in detached HEAD): {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    sync_zig_architecture()
