//! WENDY Mobile Airgap — Secure Payload Ingestion from Emperor's Mobile Device
//! SPDX-License-Identifier: EUPL-1.2
//!
//! Monitors a drop zone directory for mobile app outputs, ingests them,
//! routes them through the Crystalline Executor for epistemic distillation,
//! and archives processed files to prevent re-ingestion.
//!
//! Usage: wendy-mobile-airgap
//!   Runs indefinitely, polling every 2 seconds.

use anyhow::{Context, Result};
use chrono::{DateTime, Utc};
use std::collections::HashSet;
use std::fs;
use std::path::{Path, PathBuf};
use std::time::Duration;
use tokio::time::sleep;

const POLL_INTERVAL_SECS: u64 = 2;
const DROP_ZONE: &str = "./raw_input_stream/mobile_drops";
const PROCESSED_ZONE: &str = "./archive/mobile_processed";

/// Zulu timestamp with millisecond precision
fn zulu_now() -> String {
    let now: DateTime<Utc> = Utc::now();
    now.format("%Y-%m-%dT%H:%M:%S%.3fZ").to_string()
}

/// Short timestamp for archive filenames (no colons, filesystem-safe)
fn zulu_filename() -> String {
    let now: DateTime<Utc> = Utc::now();
    now.format("%Y%m%dT%H%M%S").to_string()
}

fn log(level: &str, name: &str, message: &str) {
    println!("[{}] {} {}: {}", zulu_now(), level, name, message);
}

fn log_info(message: &str) {
    log("INFO", "wendy_airgap", message);
}

fn log_error(message: &str) {
    log("ERROR", "wendy_airgap", message);
}

struct WendyMobileAirgap {
    drop_zone: PathBuf,
    processed_zone: PathBuf,
    processed_files: HashSet<String>,
}

impl WendyMobileAirgap {
    fn new() -> Result<Self> {
        let drop_zone = PathBuf::from(DROP_ZONE);
        let processed_zone = PathBuf::from(PROCESSED_ZONE);
        
        fs::create_dir_all(&drop_zone)
            .with_context(|| format!("Failed to create drop zone: {}", drop_zone.display()))?;
        fs::create_dir_all(&processed_zone)
            .with_context(|| format!("Failed to create processed zone: {}", processed_zone.display()))?;
        
        Ok(Self {
            drop_zone,
            processed_zone,
            processed_files: HashSet::new(),
        })
    }
    
    async fn watch_drop_zone(&mut self) -> Result<()> {
        log_info(&format!(
            "airgap watcher online | monitoring {}",
            self.drop_zone.canonicalize().unwrap_or_else(|_| self.drop_zone.clone()).display()
        ));
        log_info("awaiting secure payload from Emperor's mobile device...");
        
        loop {
            // Scan for .txt files
            if let Ok(entries) = fs::read_dir(&self.drop_zone) {
                for entry in entries.flatten() {
                    let path = entry.path();
                    
                    // Only process .txt files
                    if path.extension().map(|e| e == "txt").unwrap_or(false) {
                        if let Some(name) = path.file_name().and_then(|n| n.to_str()) {
                            let name = name.to_string();
                            if !self.processed_files.contains(&name) {
                                if let Err(e) = self.ingest_payload(&path).await {
                                    log_error(&format!("failed to process {}: {}", name, e));
                                }
                                self.processed_files.insert(name);
                            }
                        }
                    }
                }
            }
            
            sleep(Duration::from_secs(POLL_INTERVAL_SECS)).await;
        }
    }
    
    async fn ingest_payload(&self, file_path: &Path) -> Result<()> {
        let file_name = file_path
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("unknown")
            .to_string();
        
        log_info(&format!("detected new mobile payload | file={}", file_name));
        
        // 1. Read the heavy lifting from the phone app
        let qwen_raw_code = fs::read_to_string(file_path)
            .with_context(|| format!("Failed to read payload: {}", file_path.display()))?;
        
        let byte_count = qwen_raw_code.len();
        let line_count = qwen_raw_code.matches('\n').count();
        
        log_info(&format!(
            "payload ingested | bytes={} | lines={}",
            byte_count, line_count
        ));
        
        // 2. Route to Crystalline Executor for epistemic distillation
        log_info("routing payload to wendy-crystalline-executor for epistemic distillation");
        
        // Write payload to a temporary dream file for the executor
        let temp_dream = ".wendy_mobile_dream.gmi";
        fs::write(temp_dream, &qwen_raw_code)
            .context("Failed to write temporary dream file")?;
        
        // Spawn the crystalline executor
        let executor_bin = self.find_sibling_binary("wendy-crystalline-executor");
        
        let output = tokio::process::Command::new(&executor_bin)
            .arg(temp_dream)
            .output()
            .await
            .context("Failed to spawn crystalline executor")?;
        
        // Cleanup temp file
        let _ = fs::remove_file(temp_dream);
        
        if output.status.success() {
            log_info("epistemic distillation complete | CONSENSUS REACHED");
        } else {
            let stderr = String::from_utf8_lossy(&output.stderr);
            log_error(&format!("distillation failed: {}", stderr));
        }
        
        // 3. Archive the file to prevent re-processing
        let timestamp = zulu_filename();
        let dest_name = format!("{}_{}", timestamp, file_name);
        let dest_path = self.processed_zone.join(&dest_name);
        
        fs::rename(file_path, &dest_path)
            .with_context(|| format!("Failed to archive to {}", dest_path.display()))?;
        
        log_info(&format!(
            "payload archived to {} | ready for next mobile drop",
            dest_name
        ));
        
        Ok(())
    }
    
    /// Find a sibling binary in the same target/release directory
    fn find_sibling_binary(&self, name: &str) -> String {
        if let Ok(exe_path) = std::env::current_exe() {
            if let Some(parent) = exe_path.parent() {
                let sibling = parent.join(name);
                if sibling.exists() {
                    return sibling.to_string_lossy().to_string();
                }
            }
        }
        // Fallback
        format!("./target/release/{}", name)
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    // Install Ctrl+C handler for graceful shutdown
    let mut airgap = WendyMobileAirgap::new()?;
    
    tokio::select! {
        result = airgap.watch_drop_zone() => {
            if let Err(e) = result {
                log_error(&format!("watcher terminated with error: {}", e));
                std::process::exit(1);
            }
        }
        _ = tokio::signal::ctrl_c() => {
            log_info("airgap watcher terminated by user | state=secure");
        }
    }
    
    Ok(())
}
