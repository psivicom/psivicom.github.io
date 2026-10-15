# src/tools/zig_sovereign_governor.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import shutil
import re
import os
from pathlib import Path
import logging
import subprocess

logger = logging.getLogger("ZIG_SOVEREIGN_GOVERNOR")

class ZigSovereignGovernor:
    def __init__(self):
        self.root = Path(__file__).parent.parent.parent
        self.sanctioned_source_dir = self.root / "src" / "core"
        self.sanctioned_docs_dir = self.root / "docs" / "ZIG_COMMENTED_SOURCE"
        self.sanctioned_uncommented_dir = self.root / "docs" / "ZIG_UNCOMMENTED_SOURCE"
        
        # Known binary names to watch for (without extensions)
        self.known_binaries = {"vector_engine", "zulu_clock", "actuation_engine", "psvc_sealer"}
        
        # CRITICAL: Known ephemeral/sandbox locations where AI might accidentally write files
        self.ephemeral_zones = [
            Path("/tmp"),
            Path("/var/tmp"),
            Path("/home/runner/work/_temp"), # GitHub Actions specific temp dir
            Path(os.environ.get("RUNNER_TEMP", "/tmp")), # Fallback for CI environments
        ]

    def patrol_and_rescue(self):
        """Scans ephemeral sandboxes to rescue lost files, then patrols the repo for drift."""
        logger.info("🛡️ ZIG Sovereign Governor initiating Ephemeral Rescue & Repository Patrol...")
        
        corrections_made = 0
        
        # 1. RESCUE MISSION: Hunt in ephemeral sandboxes first (Highest Priority)
        for zone in self.ephemeral_zones:
            if not zone.exists():
                continue
            logger.info(f"🔍 Scanning ephemeral zone: {zone}")
            
            # Hunt for rogue .zig source files in the sandbox
            for zig_file in zone.rglob("*.zig"):
                logger.critical(f"🚨 CRITICAL RESCUE: Found ZIG source in ephemeral sandbox: {zig_file}")
                self._rescue_to_permanence(zig_file)
                corrections_made += 1
                
            # Hunt for rogue compiled binaries in the sandbox
            for item in zone.rglob("*"):
                if item.is_file() and item.name in self.known_binaries:
                    logger.critical(f"🚨 CRITICAL RESCUE: Found compiled binary in ephemeral sandbox: {item}")
                    self._rescue_binary_to_permanence(item)
                    corrections_made += 1

        # 2. PATROL MISSION: Hunt for rogue files inside the repository (Architectural Drift)
        for zig_file in self.root.rglob("*.zig"):
            if self.sanctioned_source_dir in zig_file.parents or \
               self.sanctioned_docs_dir in zig_file.parents or \
               self.sanctioned_uncommented_dir in zig_file.parents:
                continue
                
            logger.warning(f"⚠️ Architectural Drift Detected: Rogue ZIG file at {zig_file.relative_to(self.root)}")
            self._relocate_source_file(zig_file)
            corrections_made += 1

        for item in self.root.rglob("*"):
            if item.is_file() and item.name in self.known_binaries:
                if self.sanctioned_source_dir not in item.parents:
                    logger.warning(f"⚠️ Architectural Drift Detected: Rogue binary at {item.relative_to(self.root)}")
                    self._relocate_binary(item)
                    corrections_made += 1

        if corrections_made == 0:
            logger.info("✅ Repository is perfectly aligned. No ephemeral losses or architectural drift detected.")
        else:
            logger.info(f"🏁 Governor executed {corrections_made} rescues and corrections.")
            self._commit_corrections()

    def _rescue_to_permanence(self, ephemeral_file: Path):
        """Rescues a file from a sandbox and writes it permanently to src/core/."""
        target_path = self.sanctioned_source_dir / ephemeral_file.name
        logger.info(f"🚁 Rescuing {ephemeral_file.name} from sandbox to {target_path.relative_to(self.root)}")
        
        # CRITICAL: Use copy2 instead of move. We must guarantee the file is safely 
        # in the repository before the OS wipes the sandbox directory.
        shutil.copy2(str(ephemeral_file), str(target_path))
        self._invoke_scribe(target_path)
        
        # Attempt to delete the ephemeral copy to keep the sandbox clean
        try:
            ephemeral_file.unlink()
        except Exception:
            pass

    def _rescue_binary_to_permanence(self, ephemeral_binary: Path):
        """Rescues a compiled binary from a sandbox."""
        target_path = self.sanctioned_source_dir / ephemeral_binary.name
        logger.info(f"🚁 Rescuing binary {ephemeral_binary.name} from sandbox to {target_path.relative_to(self.root)}")
        shutil.copy2(str(ephemeral_binary), str(target_path))
        target_path.chmod(0o755)
        try:
            ephemeral_binary.unlink()
        except Exception:
            pass

    def _relocate_source_file(self, rogue_file: Path):
        target_path = self.sanctioned_source_dir / rogue_file.name
        logger.info(f"🔄 Relocating {rogue_file.name} to {target_path.relative_to(self.root)}")
        shutil.move(str(rogue_file), str(target_path))
        self._invoke_scribe(target_path)

    def _relocate_binary(self, rogue_binary: Path):
        target_path = self.sanctioned_source_dir / rogue_binary.name
        logger.info(f"🔄 Relocating binary {rogue_binary.name} to {target_path.relative_to(self.root)}")
        shutil.move(str(rogue_binary), str(target_path))
        target_path.chmod(0o755)

    def _invoke_scribe(self, zig_file: Path):
        name = zig_file.stem
        code_content = zig_file.read_text(encoding='utf-8')
        
        # Strip comments for the uncommented backup
        stripped_code = re.sub(r'//.*', '', code_content)
        stripped_code = re.sub(r'/\*.*?\*/', '', stripped_code, flags=re.DOTALL)
        stripped_code = re.sub(r'\n\s*\n\s*\n', '\n\n', stripped_code).strip() + '\n'
        
        self.sanctioned_uncommented_dir.mkdir(parents=True, exist_ok=True)
        (self.sanctioned_uncommented_dir / f"{name}.zig").write_text(stripped_code, encoding='utf-8')
        
        # Generate the pristine Markdown documentation
        self.sanctioned_docs_dir.mkdir(parents=True, exist_ok=True)
        md_content = (
            f"# {name.replace('_', ' ').title()} - WENDY Bare-Metal ZIG Module\n\n"
            f"> **SOVEREIGN PROTOCOL ENFORCED**: Rescued from ephemeral sandbox by Autonomous Governor.\n\n"
            f"## Source Code\n\n"
            f"```zig\n{code_content}\n```\n"
        )
        (self.sanctioned_docs_dir / f"{name}.md").write_text(md_content, encoding='utf-8')
        logger.info(f"✅ Scribe synchronized rescued {name}.zig")

    def _commit_corrections(self):
        try:
            subprocess.check_call(["git", "config", "user.name", "PSIVI ZIG Governor"])
            subprocess.check_call(["git", "config", "user.email", "governor@psivi.com"])
            subprocess.check_call(["git", "add", "src/core/", "docs/ZIG_COMMENTED_SOURCE/", "docs/ZIG_UNCOMMENTED_SOURCE/"])
            
            result = subprocess.run(["git", "diff", "--staged", "--quiet"], capture_output=True)
            if result.returncode != 0:
                subprocess.check_call(["git", "commit", "-m", "fix: governor rescued ephemeral files and corrected ZIG drift [skip ci]"])
                
                for i in range(1, 4):
                    try:
                        subprocess.check_call(["git", "pull", "--rebase", "origin", "main"])
                        subprocess.check_call(["git", "push", "origin", "main"])
                        logger.info("✅ Governor rescues committed and pushed.")
                        break
                    except subprocess.CalledProcessError:
                        logger.warning(f"⚠️ Push failed. Retrying in 2s... ({i}/3)")
                        import time
                        time.sleep(2)
        except Exception as e:
            logger.warning(f"⚠️ Governor commit failed: {e}")

def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    governor = ZigSovereignGovernor()
    governor.patrol_and_rescue()

if __name__ == "__main__":
    main()
