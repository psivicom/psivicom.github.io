#!/usr/bin/env python3
# src/agents/contextual_coder.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
WENDY CONTEXTUAL CODER
----------------------
A true autonomous programming agent. 
It does not use blind regex or rigid quarantine lists. 
It scans the compiler output, reads the surrounding code context, 
applies intelligent, structurally aware migrations, and validates the result.
"""

import os
import re
import subprocess
import glob
from pathlib import Path
from datetime import datetime, timezone

class ContextualCoder:
    def __init__(self):
        self.repo_root = Path(os.environ.get('GITHUB_WORKSPACE', '.'))
        self.core_dir = self.repo_root / 'src/core'
        self.evolutions_made = 0
        
        # Context-Aware Knowledge Graph: Maps error signatures to structural transformations
        self.knowledge_graph = [
            {
                "name": "Zig 0.13.0 Ed25519 SecretKey Initialization",
                "error_signature": r"error: struct 'crypto\.25519\.ed25519\.Ed25519\.SecretKey' has no member named 'fromSeed'",
                "context_pattern": r"(\w+)\s*=\s*crypto\.25519\.ed25519\.Ed25519\.SecretKey\.fromSeed\(\s*([^)]+)\s*\)",
                "transformation": lambda match: f"{match.group(1)} = crypto.25519.ed25519.Ed25519.SecretKey.init({match.group(2)})",
                "description": "Migrates SecretKey.fromSeed(seed) to SecretKey.init(seed) while preserving variable assignment context."
            },
            {
                "name": "Zig 0.13.0 Direct SecretKey Init",
                "error_signature": r"error: struct 'crypto\.25519\.ed25519\.Ed25519\.SecretKey' has no member named 'fromSeed'",
                "context_pattern": r"\.fromSeed\(\s*([^)]+)\s*\)",
                "transformation": lambda match: f".init({match.group(1)})",
                "description": "Migrates direct method calls from .fromSeed() to .init() preserving the seed argument."
            }
        ]

    def log(self, msg):
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        print(f"[{timestamp}] 🧠 CODER: {msg}")

    def run_cmd(self, cmd, cwd=None):
        try:
            result = subprocess.run(
                cmd, shell=True, check=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=cwd or self.repo_root
            )
            return True, result.stdout.decode('utf-8').strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.decode('utf-8')

    def parse_error_location(self, error_output: str):
        """Scans compiler output to find the exact file and line of failure."""
        # Matches: /path/to/file.zig:123:45: error: ...
        match = re.search(r'([^:\s]+\.zig):(\d+):\d+:\s*error:', error_output)
        if match:
            return Path(match.group(1)), int(match.group(2))
        return None, None

    def read_context(self, file_path: Path, line_number: int, window: int = 15):
        """Scans the surroundings of the error to understand the code structure."""
        try:
            lines = file_path.read_text().split('\n')
            start = max(0, line_number - window)
            end = min(len(lines), line_number + window)
            return '\n'.join(lines[start:end]), start
        except Exception:
            return "", 0

    def heal_zig_module(self, src_path: Path):
        self.log(f"🔍 Scanning and evaluating {src_path.name}...")
        
        bin_path = src_path.with_suffix('')
        cmd = f'zig build-exe "{src_path}" -O ReleaseSafe -fstrip -femit-bin="{bin_path}"'
        success, error_output = self.run_cmd(cmd)
        
        if success:
            self.log(f"✅ {src_path.name} is already sovereign.")
            return True

        self.log(f"⚠️ Compilation failed. Analyzing surroundings for {src_path.name}...")
        
        # 1. Locate the exact error
        error_file, error_line = self.parse_error_location(error_output)
        if not error_file or not error_file.exists():
            self.log(f"❌ Could not parse error location for {src_path.name}.")
            return False

        # 2. Read the surroundings
        context, offset = self.read_context(error_file, error_line)
        self.log(f"📖 Read {len(context.split('\n'))} lines of context around line {error_line}.")

        # 3. Apply Context-Aware Transformations
        original_content = error_file.read_text()
        modified_content = original_content
        healed = False

        for rule in self.knowledge_graph:
            if re.search(rule["error_signature"], error_output, re.IGNORECASE):
                # Check if the context pattern exists in the surrounding code
                if re.search(rule["context_pattern"], context, re.IGNORECASE):
                    self.log(f"💡 Identified evolution opportunity: {rule['name']}")
                    self.log(f"🛠️ Applying contextual transformation: {rule['description']}")
                    
                    # Apply transformation globally to the file to catch all instances
                    new_content, count = re.subn(
                        rule["context_pattern"],
                        rule["transformation"],
                        original_content,
                        flags=re.IGNORECASE
                    )
                    
                    if count > 0:
                        modified_content = new_content
                        healed = True
                        self.log(f"📝 Successfully evolved {count} instance(s) in {src_path.name}")
                        break # Apply one evolution at a time, then re-validate

        if healed:
            # 4. Validate the Evolution
            self.log(f"🧪 Validating evolved code in {src_path.name}...")
            error_file.write_text(modified_content)
            success, new_error = self.run_cmd(cmd)
            
            if success:
                self.log(f"🏆 VALIDATION SUCCESS: {src_path.name} has successfully evolved.")
                self.evolutions_made += 1
                return True
            else:
                self.log(f"❌ VALIDATION FAILED: Evolution did not resolve the issue. Reverting to preserve integrity.")
                error_file.write_text(original_content)
                return False
        else:
            self.log(f"⚠️ No contextual match found for this specific error. Manual architect review required.")
            return False

    def commit_sovereignty(self):
        if self.evolutions_made == 0:
            self.log("ℹ️ No autonomous evolutions required. The codebase is stable.")
            return

        self.log(f"🚀 Committing {self.evolutions_made} autonomous evolution(s)...")
        self.run_cmd('git config user.name "WENDY Contextual Coder"')
        self.run_cmd('git config user.email "coder@psivi.com"')
        self.run_cmd('git add src/core/')
        self.run_cmd('git commit -m "chore: coder - autonomous context-aware api evolution [skip ci]"')
        
        # Constitution-compliant push
        push_script = """
        for attempt in 1 2 3; do
          if git pull --rebase origin main && git push origin main; then
            echo "✅ Push successful on attempt $attempt"
            exit 0
          fi
          echo "⚠️ Push attempt $attempt failed, retrying..."
          sleep 2
        done
        exit 1
        """
        success, _ = self.run_cmd(push_script)
        if success:
            self.log("🏆 Autonomous evolution successfully integrated into the mesh.")
        else:
            self.log("❌ CRITICAL: Failed to push evolved code.")

    def run(self):
        self.log("Initializing Contextual Coding Engine...")
        zig_files = glob.glob(str(self.core_dir / '*.zig'))
        
        for src_path in zig_files:
            self.heal_zig_module(Path(src_path))
            
        self.commit_sovereignty()
        self.log("🏁 Coder Cycle Complete. The mesh evolves.")

if __name__ == "__main__":
    coder = ContextualCoder()
    coder.run()
