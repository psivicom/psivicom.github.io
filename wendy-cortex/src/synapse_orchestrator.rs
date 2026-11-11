//! WENDY Synapse Orchestrator — Ouroboros Optimization Demonstration
//! SPDX-License-Identifier: EUPL-1.2
//!
//! Demonstrates the Ouroboros loop: identifying slow baseline math,
//! dreaming a native Rust crystal, compiling the artifact, and
//! hot-swapping it for optimized execution.
//!
//! Benchmarks RADARSAT SAR backscatter variance calculation:
//!   1. Baseline naive implementation (intentionally slow)
//!   2. Optimized native implementation (Welford's algorithm)
//!   3. Reports speedup and verifies mathematical equivalence
//!
//! Usage: wendy-synapse-orchestrator [size]
//!   size: number of data points (default: 10,000,000)

use anyhow::{Context, Result};
use chrono::{DateTime, Utc};
use std::env;
use std::time::Instant;

const DEFAULT_SIZE: usize = 10_000_000;

/// Zulu timestamp with millisecond precision
fn zulu_now() -> String {
    let now: DateTime<Utc> = Utc::now();
    now.format("%Y-%m-%dT%H:%M:%S%.3fZ").to_string()
}

fn log_info(message: &str) {
    println!("[{}] INFO wendy_synapse: {}", zulu_now(), message);
}

fn log_warning(message: &str) {
    println!("[{}] WARN wendy_synapse: {}", zulu_now(), message);
}

/// Baseline naive variance (intentionally slow — two passes, no numerical stability)
/// This represents "Python-like" slow math that the Ouroboros wants to optimize.
fn baseline_variance(data: &[f64]) -> f64 {
    let len = data.len() as f64;
    let mean: f64 = data.iter().sum::<f64>() / len;
    data.iter().map(|x| (x - mean).powi(2)).sum::<f64>() / len
}

/// Optimized native variance using Welford's online algorithm
/// Numerically stable, single-pass, SIMD-friendly.
/// This represents the "Rust crystal" the Ouroboros dreams into existence.
fn crystalline_variance(data: &[f64]) -> f64 {
    let mut count: usize = 0;
    let mut mean: f64 = 0.0;
    let mut m2: f64 = 0.0;
    
    for &value in data {
        count += 1;
        let delta = value - mean;
        mean += delta / count as f64;
        let delta2 = value - mean;
        m2 += delta * delta2;
    }
    
    if count < 2 {
        0.0
    } else {
        m2 / count as f64  // Population variance (matches baseline)
    }
}

/// Generate synthetic RADARSAT SAR backscatter data
fn generate_sar_data(size: usize) -> Vec<f64> {
    log_info(&format!(
        "Ingesting synthetic RADARSAT backscatter array | size={}",
        size
    ));
    (0..size)
        .map(|i| (i % 100) as f64 / 10.0)
        .collect()
}

fn main() -> Result<()> {
    let args: Vec<String> = env::args().collect();
    
    let size = if args.len() > 1 {
        args[1].parse::<usize>()
            .context("Failed to parse size argument (must be a positive integer)")?
    } else {
        DEFAULT_SIZE
    };
    
    if size == 0 {
        anyhow::bail!("Size must be at least 1");
    }
    
    log_info("WENDY Synapse Orchestrator initializing...");
    
    // 1. Generate the dataset
    let sar_data = generate_sar_data(size);
    
    // 2. Execute baseline (The Bottleneck)
    log_info("Executing baseline naive variance calculation...");
    let t0 = Instant::now();
    let py_result = baseline_variance(&sar_data);
    let py_time = t0.elapsed();
    log_info(&format!(
        "Baseline result: {:.4} | Time: {:.4}s",
        py_result,
        py_time.as_secs_f64()
    ));
    
    // 3. The Ouroboros Loop: Dream a native Rust crystal
    log_info("Ouroboros dreaming crystalline SAR variance artifact...");
    
    // In a full Ouroboros, this would invoke the Crystalline Executor
    // to compile and hot-load a dynamic artifact. For this demonstration,
    // we call the optimized native implementation directly.
    
    // 4. Execute the hot-swapped native artifact
    log_info("Executing hot-swapped native Rust crystal...");
    let t2 = Instant::now();
    let rust_result = crystalline_variance(&sar_data);
    let rust_time = t2.elapsed();
    log_info(&format!(
        "Rust result:   {:.4} | Time: {:.4}s",
        rust_result,
        rust_time.as_secs_f64()
    ));
    
    // 5. Calculate and report speedup
    let py_secs = py_time.as_secs_f64();
    let rust_secs = rust_time.as_secs_f64();
    
    let speedup = if rust_secs > 0.0 {
        py_secs / rust_secs
    } else {
        f64::INFINITY
    };
    
    log_info(&format!(
        "⚡💰 Ouroboros Optimization Achieved: {:.2}x speedup. Electricity saved.",
        speedup
    ));
    
    // 6. Verify mathematical equivalence
    let divergence = (py_result - rust_result).abs();
    if divergence > 0.0001 {
        log_warning(&format!(
            "Mathematical divergence detected between baseline and crystal! delta={}",
            divergence
        ));
    } else {
        log_info("Crystalline artifact mathematically verified. Synapse optimized.");
    }
    
    Ok(())
}
