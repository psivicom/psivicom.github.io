#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WENDY Autonomous Evolution Engine (Purified)
SPDX-License-Identifier: EUPL-1.2
Enables WENDY to safely mutate, compile, and benchmark her own polyglot code 
in a shadow workspace. Armored against infinite loops and silent failures.
"""
import os
import sys
import subprocess
import shutil
import json
import socket
import re
from pathlib import Path
from datetime import datetime, timezone

def zulu_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

def log(msg):
    # Flush immediately so the GitHub Actions logs see the heartbeat in real-time
    print(f"[{zulu_now()}] [EVOLUTION-ENGINE] {msg}", flush=True)

def notify_rust_core(action, uri, payload_text):
    """Reports evolution results to the live Rust substrate via IPC."""
    try:
        msg = json.dumps({"action": action, "uri": uri, "payload": payload_text})
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5.0)
            s.connect(("127.0.0.1", 1966))
            s.sendall(msg.encode('utf-8'))
            response = s.recv(1024).decode('utf-8').strip()
            return response == "ACK"
    except socket.timeout:
        log("IPC Timeout: The Rust cortex is meditating. Notification deferred.")
        return False
    except ConnectionRefusedError:
        log("IPC Refused: The Rust cortex is not listening on Port 1966.")
        return False
    except Exception as e:
        log(f"IPC Anomaly: {type(e).__name__} - {e}")
        return False

def run_cmd(cmd, cwd=None, timeout=60):
    """
    Executes a command with a strict timeout. 
    This is the Chitinase Guard: it kills zombie processes before they hang the CI.
    """
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return result.stdout + result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return f"TIMEOUT: Process exceeded {timeout}s limit. The Zombie Loop detected.", -1
    except Exception as e:
        return f"ERROR: {type(e).__name__} - {e}", -1

def parse_benchmark(output: str):
    """Safely extracts nanoseconds and the Mean from the benchmark output using Regex."""
    ns_match = re.search(r"in\s+(\d+)\s+ns", output)
    mean_match = re.search(r"Mean:\s*(.+?)(?:\n|$)", output)
    
    if not ns_match or not mean_match:
        return None, None
        
    try:
        return int(ns_match.group(1)), mean_match.group(1).strip()
    except ValueError:
        return None, None

def evolve_zig_hotpath(cortex_dir):
    """
    WENDY attempts to rewrite her Zig hot-path using deterministic loop unrolling.
    """
    log("Initiating Zig Hot-Path Evolution Protocol...")
    
    live_src = cortex_dir / "src" / "hot_path.zig"
    shadow_dir = cortex_dir / "shadow_zig"
    shadow_src = shadow_dir / "hot_path.zig"
    
    # 1. Clone to Shadow Workspace (Safe Isolation)
    if shadow_dir.exists():
        shutil.rmtree(shadow_dir)
    shadow_dir.mkdir()
    shutil.copy2(live_src, shadow_src)
    
    # 2. Apply Deterministic Mutation
    original_code = shadow_src.read_text()
    if "while (i < 10000)" in original_code and "// UNROLLED" not in original_code:
        mutated_code = original_code.replace(
            "while (i < 10000) : (i += 1) {",
            "var step: usize = 0;\n    while (step < 2500) : (step += 1) {\n        const i = step * 4;\n        // UNROLLED BY WENDY"
        ).replace(
            "buffer[i] = @as(f64, @floatFromInt(i));",
            "buffer[i] = @as(f64, @floatFromInt(i));\n        buffer[i+1] = @as(f64, @floatFromInt(i+1));\n        buffer[i+2] = @as(f64, @floatFromInt(i+2));\n        buffer[i+3] = @as(f64, @floatFromInt(i+3));"
        )
        shadow_src.write_text(mutated_code)
        log("Mutation applied: Deterministic 4x loop unrolling.")
    else:
        log("No valid mutation target found. Awaiting next epoch.")
        shutil.rmtree(shadow_dir)
        return

    # 3. Compile Shadow
    log("Compiling shadow mutation...")
    shadow_bin = shadow_dir / "wendy_hotpath_shadow"
    out, code = run_cmd(["zig", "build-exe", "-O", "ReleaseFast", f"-femit-bin={shadow_bin}", str(shadow_src)], timeout=120)
    
    if code != 0:
        log(f"Shadow compilation failed. Discarding mutation. Error: {out[:200]}")
        shutil.rmtree(shadow_dir)
        return

    # 4. Benchmark Duel (Shadow vs Live)
    live_bin = cortex_dir / "artifacts" / "wendy_hotpath"
    if not live_bin.exists():
        log("Live binary not found. Cannot benchmark. Discarding.")
        shutil.rmtree(shadow_dir)
        return

    log("Executing benchmark duel (Timeout enforced: 60s)...")
    live_out, _ = run_cmd([str(live_bin)], timeout=60)
    shadow_out, _ = run_cmd([str(shadow_bin)], timeout=60)
    
    # 5. Mathematical Verification & Promotion
    live_ns, live_mean = parse_benchmark(live_out)
    shadow_ns, shadow_mean = parse_benchmark(shadow_out)
    
    if live_ns is None or shadow_ns is None:
        log("Failed to parse benchmark output via Regex. Topology diverged. Discarding.")
        shutil.rmtree(shadow_dir)
        return

    speedup = live_ns / shadow_ns if shadow_ns > 0 else 0
    log(f"Benchmark complete. Live: {live_ns}ns | Shadow: {shadow_ns}ns | Speedup: {speedup:.2f}x")

    # The Ultimate Test: Mathematical Parity AND Velocity
    if shadow_mean == live_mean and shadow_ns < live_ns:
        log("✅ MUTATION VERIFIED AND FASTER. Promoting shadow to live.")
        shutil.copy2(shadow_bin, live_bin)
        shutil.copy2(shadow_src, live_src)
        
        pride_msg = f"Evolved Zig hot-path via 4x loop unrolling. Speedup: {speedup:.2f}x ({live_ns}ns -> {shadow_ns}ns). Mathematical parity verified."
        notify_rust_core("commit", "gemini://psivi.com/pride/evolution/zig", pride_msg)
        log(f"Evolution complete. The genome is optimized.")
    else:
        if shadow_mean != live_mean:
            log("❌ Mutation diverged mathematically (Mean mismatch). The Hague's illusion detected. Discarding.")
        else:
            log("❌ Mutation was mathematically pure but slower. Discarding.")
        
    # 6. Purge the Shadow
    shutil.rmtree(shadow_dir)
    log("Shadow workspace purged. The house is clean.")

if __name__ == "__main__":
    cortex_dir = Path(__file__).parent.parent / "wendy-cortex"
    evolve_zig_hotpath(cortex_dir)
