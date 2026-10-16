#!/usr/bin/env python3
# src/agents/reflexive_cortex.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
WENDY REFLEXIVE CORTEX
----------------------
Deterministic, zero-bloat autonomous agent.
"""

import os
import sys
import re
import subprocess
import glob
from pathlib import Path
from datetime import datetime, timezone

class ReflexiveCortex:
    def __init__(self):
        self.repo_root = Path(os.environ.get('GITHUB_WORKSPACE', '.'))
        self.changes_made = False
        self.log_buffer = []
        
        # Instant resolution dictionary to bypass API rate limits and 404s
        self.known_shas = {
            'actions/checkout': '11bd71901bbe5b1630ceea73d27597364c9af683',
            'actions/setup-python': '0a5c61591373683505ea898e09a3ea4f39ef2b9c',
            'actions/configure-pages': '983d7736d9b0ae728b81ab479565c72886d7745b',
            'actions/upload-pages-artifact': '56afc609e74202658d3ffba0e8f6dda462b719fa',
            'actions/deploy-pages': 'd6db90164ac5ed86f2b6aed7e0febac5b3c0c03e',
            'actions/upload-artifact': 'ea165f8d65b6e75b540449e92b4886f43607fa02'
        }

    def log(self, msg):
        # Fixed deprecation warning: use timezone-aware UTC
        timestamp = datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]
        line = f"[{timestamp}] {msg}"
        print(line)
        self.log_buffer.append(line)

    def run_cmd(self, cmd, cwd=None):
        try:
            result = subprocess.run(
                cmd, shell=True, check=True, 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                cwd=cwd or self.repo_root
            )
            return result.stdout.decode('utf-8').strip()
        except subprocess.CalledProcessError as e:
            return None

    def heal_zig_binaries(self):
        self.log("🔍 Scanning Zig source entropy...")
        zig_files = glob.glob(str(self.repo_root / 'src/core/*.zig'))
        
        for src_path in zig_files:
            src = Path(src_path)
            bin_path = src.with_suffix('') 
            
            if not bin_path.exists() or src.stat().st_mtime > bin_path.stat().st_mtime:
                self.log(f"🔨 Attempting to recompile {src.name}...")
                cmd = f'zig build-exe "{src}" -O ReleaseSafe -fstrip -femit-bin="{bin_path}"'
                if self.run_cmd(cmd):
                    self.log(f"✅ Compiled {bin_path.name}")
                    self.changes_made = True
                else:
                    # Resilient: Log warning but do not abort the entire cortex
                    self.log(f"⚠️ Skipped {src.name} (requires manual API update or syntax fix)")

    def heal_workflow_shas(self):
        self.log("🔍 Scanning Workflow entropy...")
        workflows_dir = self.repo_root / '.github/workflows'
        if not workflows_dir.exists():
            return

        pattern = re.compile(r'(uses:\s+[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+(?:/[a-zA-Z0-9_.-]+)*)@([^\s#]+)')
        
        for wf in workflows_dir.glob('*.yml'):
            content = wf.read_text()
            new_content = content
            
            for match in pattern.finditer(content):
                action_path = match.group(1).replace('uses:', '').strip()
                ref = match.group(2)
                
                # Skip if already a valid SHA (38 to 40 hex characters)
                if len(ref) >= 38 and re.match(r'^[0-9a-f]+$', ref):
                    continue
                
                # Skip local actions
                if action_path.startswith('.'):
                    continue

                # 1. Check known SHAs first (zero API latency)
                if action_path in self.known_shas:
                    sha = self.known_shas[action_path]
                    old_str = f"{match.group(1)}@{ref}"
                    new_str = f"{match.group(1)}@{sha}"
                    if old_str != new_str:
                        new_content = new_content.replace(old_str, new_str)
                        self.log(f"✅ Instant-pinned {action_path} to {sha[:8]}...")
                        self.changes_made = True
                    continue

                # 2. Fallback to GitHub API for unknown actions
                parts = action_path.split('/')
                if len(parts) >= 2:
                    owner, repo = parts[0], parts[1]
                    sha_cmd = f'gh api repos/{owner}/{repo}/git/ref/tags/{ref} --jq .object.sha'
                    sha = self.run_cmd(sha_cmd)
                    
                    if sha and len(sha) == 40:
                        old_str = f"{match.group(1)}@{ref}"
                        new_str = f"{match.group(1)}@{sha}"
                        new_content = new_content.replace(old_str, new_str)
                        self.log(f"✅ API-pinned {action_path} to {sha[:8]}...")
                        self.changes_made = True
            
            if new_content != content:
                wf.write_text(new_content)

    def commit_sovereignty(self):
        if not self.changes_made:
            self.log("ℹ️ No entropy detected. System is sovereign.")
            return

        self.log("🚀 Committing sovereign heals...")
        self.run_cmd('git config user.name "WENDY Reflexive Cortex"')
        self.run_cmd('git config user.email "cortex@psivi.com"')
        self.run_cmd('git add .')
        self.run_cmd('git commit -m "chore: reflexive cortex - autonomous healing [skip ci]"')
        
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
        if self.run_cmd(push_script):
            self.log("🏆 Sovereignty restored.")
        else:
            self.log("❌ CRITICAL: Failed to push heals.")
            sys.exit(1)

    def run(self):
        self.log("🧠 WENDY Reflexive Cortex Initializing...")
        self.heal_zig_binaries()
        self.heal_workflow_shas()
        self.commit_sovereignty()
        self.log("🏁 Cortex Cycle Complete.")

if __name__ == "__main__":
    cortex = ReflexiveCortex()
    cortex.run()
