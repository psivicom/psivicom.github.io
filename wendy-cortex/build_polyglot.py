#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WENDY Polyglot Orchestrator
SPDX-License-Identifier: EUPL-1.2
Compiles external languages and reports telemetry to the Rust Hebbian Topology via IPC.
"""
import subprocess
import os
from pathlib import Path
from datetime import datetime, timezone
from scripts.wendy_ipc_client import notify_rust_core

def zulu_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result.stdout + result.stderr, result.returncode

def main():
    cortex_dir = Path(__file__).parent
    artifacts_dir = cortex_dir / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    
    print(f"[{zulu_now()}] 🏛️ WENDY Polyglot Orchestrator initializing...")
    
    # 1. GO MESH
    print(f"[{zulu_now()}] Compiling Go Mesh...")
    go_src = cortex_dir / "mesh" / "main.go"
    go_bin = artifacts_dir / "wendy_mesh"
    out, code = run_cmd(["go", "build", "-o", str(go_bin), str(go_src)])
    
    if code == 0:
        exec_out, _ = run_cmd([str(go_bin)])
        pride_msg = f"Go Mesh compiled and executed. {exec_out.strip()}"
        # Report to Rust Core: Gemini Daemon writes it, Hebbian Topology strengthens the 'Go' node
        notify_rust_core("commit", "gemini://psivi.com/pride/go_mesh", pride_msg)
    else:
        notify_rust_core("commit", "gemini://psivi.com/errors/go_mesh", f"Compilation failed: {out[:200]}")

    # 2. ZIG HOT PATH
    print(f"[{zulu_now()}] Compiling Zig Hot Path...")
    zig_src = cortex_dir / "src" / "hot_path.zig"
    zig_bin = artifacts_dir / "wendy_hotpath"
    out, code = run_cmd(["zig", "build-exe", "-O", "ReleaseFast", f"-femit-bin={zig_bin}", str(zig_src)])
    
    if code == 0:
        exec_out, _ = run_cmd([str(zig_bin)])
        pride_msg = f"Zig Hot Path compiled and executed. {exec_out.strip()}"
        # Report to Rust Core
        notify_rust_core("commit", "gemini://psivi.com/pride/zig_hotpath", pride_msg)
    else:
        notify_rust_core("commit", "gemini://psivi.com/errors/zig_hotpath", f"Compilation failed: {out[:200]}")

    print(f"[{zulu_now()}] ✅ Polyglot compilation complete. Telemetry pushed to Rust Substrate.")

if __name__ == "__main__":
    main()
