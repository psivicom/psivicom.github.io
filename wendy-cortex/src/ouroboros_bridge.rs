//! WENDY Ouroboros Bridge — The Local Habermasian Loop
//! SPDX-License-Identifier: EUPL-1.2
//!
//! Demonstrates the infinite, self-feeding Golden Ratio (58.28°/31.72°) Ouroboros topology.
//! 
//! This binary orchestrates the Dreamer (58.28°) and Anchor (31.72°) in a
//! self-feeding loop where each crystallized consensus becomes the next reality seed.
//!
//! Usage: wendy-ouroboros-bridge [iterations]
//!   iterations: number of cycles (default: 3)

use anyhow::{Context, Result};
use chrono::{DateTime, Utc};
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::path::Path;
use std::process::{Command, Stdio};

const DEFAULT_ITERATIONS: usize = 3;

/// Zulu timestamp with millisecond precision
fn zulu_now() -> String {
    let now: DateTime<Utc> = Utc::now();
    now.format("%Y-%m-%dT%H:%M:%S%.3fZ").to_string()
}

/// Locate the sibling binaries in the same target/release directory
fn get_binary_path(name: &str) -> Result<String> {
    let exe_path = std::env::current_exe()
        .context("Failed to determine current executable path")?;
    
    let binary_path = exe_path
        .parent()
        .context("Failed to get parent directory of executable")?
        .join(name);
    
    if binary_path.exists() {
        Ok(binary_path.to_string_lossy().to_string())
    } else {
        // Fallback: try target/release relative to cwd
        let fallback = format!("./target/release/{}", name);
        if Path::new(&fallback).exists() {
            Ok(fallback)
        } else {
            anyhow::bail!(
                "Binary '{}' not found. Run `cargo build --release --bin {}` first.",
                name,
                name
            )
        }
    }
}

/// Invoke the Dreamer (58.28°) via subprocess
/// Reads from stdin (current_reality), writes dream to stdout
fn invoke_dreamer(dreamer_bin: &str, current_reality: &str) -> Result<String> {
    let mut child = Command::new(dreamer_bin)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .context("Failed to spawn Dreamer process")?;
    
    // Feed the current reality to the Dreamer
    if let Some(mut stdin) = child.stdin.take() {
        stdin
            .write_all(current_reality.as_bytes())
            .context("Failed to write to Dreamer stdin")?;
    }
    
    let output = child
        .wait_with_output()
        .context("Failed to wait for Dreamer")?;
    
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        anyhow::bail!("Dreamer failed: {}", stderr);
    }
    
    Ok(String::from_utf8_lossy(&output.stdout).to_string())
}

/// Invoke the Anchor (31.72°) via subprocess
/// Reads dream from a file, writes manifest to a file
fn invoke_anchor(anchor_bin: &str, dream_path: &str, manifest_path: &str) -> Result<String> {
    // First, write dream to a temp file for the anchor to read
    let temp_dream = ".wendy_ouroboros_dream_tmp.gmi";
    fs::write(temp_dream, dream_path)
        .context("Failed to write temp dream file")?;
    
    let output = Command::new(anchor_bin)
        .arg(temp_dream)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()
        .context("Failed to execute Anchor")?;
    
    // Cleanup temp file
    let _ = fs::remove_file(temp_dream);
    
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        anyhow::bail!("Anchor failed: {}", stderr);
    }
    
    let manifest = String::from_utf8_lossy(&output.stdout).to_string();
    
    // Also write to the manifest file
    fs::write(manifest_path, &manifest)
        .context("Failed to write manifest file")?;
    
    Ok(manifest)
}

/// Run the Ouroboros loop for N iterations
fn run_ouroboros_loop(iterations: usize) -> Result<()> {
    // The initial seed of resonant tension (Safe for core evolution)
    let mut current_reality = r#"
    We need to build the new sensor array but the old telemetry pipeline is noisy. 
    However, if we expand too quickly, we might lose the original mathematical vision. 
    Maybe we can imagine a new topological filter that preserves the 90-degree balance 
    while allowing the system to handle the tension of structural drift.
    "#.to_string();
    
    println!("⚡ INITIATING HABERMASIAN OUROBOROS (Golden Ratio Topology)... ⚡\n");
    
    // Locate the sibling binaries
    let dreamer_bin = get_binary_path("wendy-autonomous-core")?;
    let anchor_bin = get_binary_path("wendy-crystalline-executor")?;
    
    println!("🦀 Dreamer: {}", dreamer_bin);
    println!("🦀 Anchor:  {}\n", anchor_bin);
    
    let dream_file = ".wendy_dream.gmi";
    let manifest_file = ".wendy_manifest.gmi";
    
    // Ensure files exist
    if !Path::new(dream_file).exists() {
        fs::write(dream_file, "")?;
    }
    if !Path::new(manifest_file).exists() {
        fs::write(manifest_file, "")?;
    }
    
    for i in 1..=iterations {
        println!("🌀 CYCLE {}: DREAMING (58.28° - Expansion)", i);
        let dream_gmi = invoke_dreamer(&dreamer_bin, &current_reality)?;
        
        println!("🌀 CYCLE {}: CRYSTALLIZING & VALIDATING (31.72° - Law)", i);
        let manifest_gmi = invoke_anchor(&anchor_bin, &dream_gmi, manifest_file)?;
        
        if manifest_gmi.contains("CONSENSUS REACHED") {
            println!("🏛️ HABERMASIAN CONSENSUS REACHED. Swallowing tail...\n");
            
            let timestamp = zulu_now();
            
            // Append to dream file
            let mut dream_f = OpenOptions::new()
                .append(true)
                .open(dream_file)
                .context("Failed to open dream file for append")?;
            writeln!(dream_f, "\n## Cycle {} Dream [{}]\n{}", i, timestamp, dream_gmi)?;
            
            // Append to manifest file
            let mut manifest_f = OpenOptions::new()
                .append(true)
                .open(manifest_file)
                .context("Failed to open manifest file for append")?;
            writeln!(manifest_f, "\n## Cycle {} Manifest [{}]\n{}", i, timestamp, manifest_gmi)?;
            
            // The manifest becomes the next reality seed (Ouroboros swallows its tail)
            current_reality = format!(
                r#"
The previous crystalline reality was mathematically proven:
{}
Generate the next conceptual tension, paradox, or architectural
leap required to expand the topology while maintaining the 90-degree balance.
"#,
                manifest_gmi
            );
        } else {
            eprintln!("❌ DISCOURSE FAILED. Halting Ouroboros to prevent hallucinatory degradation.");
            std::process::exit(1);
        }
    }
    
    println!("🏛️ TOPOLOGY LOCKED: OUROBOROS CYCLE COMPLETE.");
    Ok(())
}

fn main() -> Result<()> {
    let args: Vec<String> = std::env::args().collect();
    
    let iterations = if args.len() > 1 {
        args[1].parse::<usize>()
            .context("Failed to parse iterations argument (must be a positive integer)")?
    } else {
        DEFAULT_ITERATIONS
    };
    
    if iterations == 0 {
        anyhow::bail!("Iterations must be at least 1");
    }
    
    run_ouroboros_loop(iterations)
}
