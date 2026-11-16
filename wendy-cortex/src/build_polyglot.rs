//! WENDY Polyglot Orchestrator
//! SPDX-License-Identifier: EUPL-1.2
//!
//! Compiles external languages (Go, Zig) and reports telemetry to the
//! Rust Hebbian Topology via IPC on port 1966.
//!
//! Usage: wendy-build-polyglot
//!   Compiles Go Mesh and Zig Hot Path, executes them, and reports results.

mod ipc_client;

use anyhow::{Context, Result};
use chrono::{DateTime, Utc};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

/// Zulu timestamp with millisecond precision
fn zulu_now() -> String {
    let now: DateTime<Utc> = Utc::now();
    now.format("%Y-%m-%dT%H:%M:%S%.3fZ").to_string()
}

fn log_info(message: &str) {
    println!("[{}] INFO wendy_polyglot: {}", zulu_now(), message);
}

fn log_warn(message: &str) {
    println!("[{}] WARN wendy_polyglot: {}", zulu_now(), message);
}

/// Run a command, capturing combined stdout+stderr and exit code.
fn run_cmd(cmd: &[&str], cwd: Option<&Path>) -> (String, i32) {
    let mut command = Command::new(cmd[0]);
    command.args(&cmd[1..]);
    
    if let Some(dir) = cwd {
        command.current_dir(dir);
    }
    
    match command.output() {
        Ok(output) => {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let stderr = String::from_utf8_lossy(&output.stderr);
            let combined = format!("{}{}", stdout, stderr);
            let code = output.status.code().unwrap_or(-1);
            (combined, code)
        }
        Err(e) => {
            (format!("Failed to execute {}: {}", cmd[0], e), -1)
        }
    }
}

/// Determine the cortex directory from the executable's location.
/// Falls back to `./wendy-cortex` if not found.
fn find_cortex_dir() -> PathBuf {
    // Try: executable is in wendy-cortex/target/release/
    if let Ok(exe) = std::env::current_exe() {
        if let Some(parent) = exe.parent() {
            // parent = target/release, parent.parent = target, parent.parent.parent = wendy-cortex
            if let Some(grandparent) = parent.parent().and_then(|p| p.parent()) {
                if grandparent.join("Cargo.toml").exists() {
                    return grandparent.to_path_buf();
                }
            }
        }
    }
    
    // Fallback: check relative paths
    for candidate in &["./wendy-cortex", "../wendy-cortex", "."] {
        let p = PathBuf::from(candidate);
        if p.join("Cargo.toml").exists() {
            return p;
        }
    }
    
    PathBuf::from("./wendy-cortex")
}

/// Compile and execute the Go Mesh
fn compile_go_mesh(cortex_dir: &Path, artifacts_dir: &Path) {
    log_info("Compiling Go Mesh...");
    
    let go_src = cortex_dir.join("mesh").join("main.go");
    let go_bin = artifacts_dir.join("wendy_mesh");
    
    if !go_src.exists() {
        log_warn(&format!("Go source not found: {}", go_src.display()));
        ipc_client::notify_or_log(
            "go_mesh",
            "commit",
            "gemini://psivi.com/errors/go_mesh",
            &format!("Source file missing: {}", go_src.display()),
        );
        return;
    }
    
    let (out, code) = run_cmd(
        &["go", "build", "-o", &go_bin.to_string_lossy(), &go_src.to_string_lossy()],
        None,
    );
    
    if code == 0 {
        let (exec_out, exec_code) = run_cmd(&[&go_bin.to_string_lossy()], None);
        
        if exec_code == 0 {
            let pride_msg = format!(
                "Go Mesh compiled and executed. {}",
                exec_out.trim()
            );
            ipc_client::notify_or_log(
                "go_mesh",
                "commit",
                "gemini://psivi.com/pride/go_mesh",
                &pride_msg,
            );
            log_info(&pride_msg);
        } else {
            let err_msg = format!(
                "Go Mesh compiled but execution failed (code {}): {}",
                exec_code,
                &exec_out[..exec_out.len().min(200)]
            );
            ipc_client::notify_or_log(
                "go_mesh",
                "commit",
                "gemini://psivi.com/errors/go_mesh",
                &err_msg,
            );
            log_warn(&err_msg);
        }
    } else {
        let err_msg = format!(
            "Go Mesh compilation failed: {}",
            &out[..out.len().min(200)]
        );
        ipc_client::notify_or_log(
            "go_mesh",
            "commit",
            "gemini://psivi.com/errors/go_mesh",
            &err_msg,
        );
        log_warn(&err_msg);
    }
}

/// Compile and execute the Zig Hot Path
fn compile_zig_hotpath(cortex_dir: &Path, artifacts_dir: &Path) {
    log_info("Compiling Zig Hot Path...");
    
    let zig_src = cortex_dir.join("src").join("hot_path.zig");
    let zig_bin = artifacts_dir.join("wendy_hotpath");
    
    if !zig_src.exists() {
        log_warn(&format!("Zig source not found: {}", zig_src.display()));
        ipc_client::notify_or_log(
            "zig_hotpath",
            "commit",
            "gemini://psivi.com/errors/zig_hotpath",
            &format!("Source file missing: {}", zig_src.display()),
        );
        return;
    }
    
    let (out, code) = run_cmd(
        &[
            "zig",
            "build-exe",
            "-O",
            "ReleaseFast",
            &format!("-femit-bin={}", zig_bin.to_string_lossy()),
            &zig_src.to_string_lossy(),
        ],
        None,
    );
    
    if code == 0 {
        let (exec_out, exec_code) = run_cmd(&[&zig_bin.to_string_lossy()], None);
        
        if exec_code == 0 {
            let pride_msg = format!(
                "Zig Hot Path compiled and executed. {}",
                exec_out.trim()
            );
            ipc_client::notify_or_log(
                "zig_hotpath",
                "commit",
                "gemini://psivi.com/pride/zig_hotpath",
                &pride_msg,
            );
            log_info(&pride_msg);
        } else {
            let err_msg = format!(
                "Zig Hot Path compiled but execution failed (code {}): {}",
                exec_code,
                &exec_out[..exec_out.len().min(200)]
            );
            ipc_client::notify_or_log(
                "zig_hotpath",
                "commit",
                "gemini://psivi.com/errors/zig_hotpath",
                &err_msg,
            );
            log_warn(&err_msg);
        }
    } else {
        let err_msg = format!(
            "Zig Hot Path compilation failed: {}",
            &out[..out.len().min(200)]
        );
        ipc_client::notify_or_log(
            "zig_hotpath",
            "commit",
            "gemini://psivi.com/errors/zig_hotpath",
            &err_msg,
        );
        log_warn(&err_msg);
    }
}

fn main() -> Result<()> {
    let cortex_dir = find_cortex_dir();
    let artifacts_dir = cortex_dir.join("artifacts");
    
    fs::create_dir_all(&artifacts_dir)
        .with_context(|| format!("Failed to create artifacts dir: {}", artifacts_dir.display()))?;
    
    log_info(&format!(
        "🏛️ WENDY Polyglot Orchestrator initializing | cortex={}",
        cortex_dir.display()
    ));
    
    // 1. Compile Go Mesh
    compile_go_mesh(&cortex_dir, &artifacts_dir);
    
    // 2. Compile Zig Hot Path
    compile_zig_hotpath(&cortex_dir, &artifacts_dir);
    
    log_info("✅ Polyglot compilation complete. Telemetry pushed to Rust Substrate.");
    
    Ok(())
}
