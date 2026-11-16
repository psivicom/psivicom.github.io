//! WENDY Rust Bridge — IPC Client for Rust Substrate Communication
//! SPDX-License-Identifier: EUPL-1.2
//!
//! Demonstrates how crystallized mathematical artifacts are transmitted
//! to the running wendy-cortex daemon via the TCP IPC bridge on port 1966.
//!
//! Usage: wendy-rust-bridge [uri] [symbolic_math]
//!   If no arguments provided, runs a self-test with a Lock-Free CAS axiom.

use anyhow::{Context, Result};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::env;
use std::io::{Read, Write};
use std::net::TcpStream;
use std::time::Duration;

const DEFAULT_HOST: &str = "127.0.0.1";
const DEFAULT_PORT: u16 = 1966;
const TIMEOUT_SECS: u64 = 5;

/// Zulu timestamp with millisecond precision
fn zulu_now() -> String {
    let now: DateTime<Utc> = Utc::now();
    now.format("%Y-%m-%dT%H:%M:%S%.3fZ").to_string()
}

fn log(level: &str, name: &str, message: &str) {
    println!("[{}] {} {}: {}", zulu_now(), level, name, message);
}

fn log_info(message: &str) {
    log("INFO", "wendy_rust_bridge", message);
}

fn log_error(message: &str) {
    log("ERROR", "wendy_rust_bridge", message);
}

/// IPC Payload structure matching the daemon's expected format
#[derive(Debug, Serialize, Deserialize)]
struct IpcPayload {
    action: String,
    uri: String,
    payload: String,
}

struct WendyRustBridge {
    host: String,
    port: u16,
}

impl WendyRustBridge {
    fn new(host: &str, port: u16) -> Self {
        Self {
            host: host.to_string(),
            port,
        }
    }
    
    fn commit_to_substrate(&self, uri: &str, symbolic_math: &str) -> Result<()> {
        let payload = IpcPayload {
            action: "commit".to_string(),
            uri: uri.to_string(),
            payload: symbolic_math.to_string(),
        };
        
        log_info(&format!(
            "transmitting crystallized math to rust substrate | uri={}",
            uri
        ));
        
        let addr = format!("{}:{}", self.host, self.port);
        
        // Establish TCP connection with timeout
        let mut stream = TcpStream::connect_timeout(
            &addr.parse().context("Invalid address")?,
            Duration::from_secs(TIMEOUT_SECS),
        )
        .with_context(|| format!(
            "connection refused | ensure wendy-cortex rust daemon is running on port {}",
            self.port
        ))?;
        
        stream
            .set_read_timeout(Some(Duration::from_secs(TIMEOUT_SECS)))
            .context("Failed to set read timeout")?;
        
        // Serialize and send
        let json_payload = serde_json::to_string(&payload)
            .context("Failed to serialize IPC payload")?;
        
        stream
            .write_all(json_payload.as_bytes())
            .context("Failed to write to socket")?;
        
        stream.flush().context("Failed to flush socket")?;
        
        // Read response
        let mut response_buf = vec![0u8; 1024];
        let bytes_read = stream
            .read(&mut response_buf)
            .context("Failed to read response")?;
        
        let response = String::from_utf8_lossy(&response_buf[..bytes_read]);
        
        if response.trim() == "ACK" {
            log_info("rust substrate acknowledged commit | state=synchronized");
            Ok(())
        } else {
            let msg = format!("rust substrate rejected commit | response={}", response);
            log_error(&msg);
            anyhow::bail!(msg)
        }
    }
}

fn main() -> Result<()> {
    let args: Vec<String> = env::args().collect();
    
    let bridge = WendyRustBridge::new(DEFAULT_HOST, DEFAULT_PORT);
    
    let (uri, symbolic_math) = if args.len() >= 3 {
        (args[1].clone(), args[2].clone())
    } else {
        // Self-test: Lock-Free CAS Axiom
        log_info("no arguments provided | running self-test with Lock-Free CAS axiom");
        
        let uri = "gemini://wendy/capsule/learned_cas_loop.gmi".to_string();
        let math = r#"# Lock-Free CAS Axiom
∀ counter ∈ AtomicUsize:
  mutate(counter) ≡ CAS(current, current + 1, SeqCst)
  ⊢ lock_free(counter) ≡ ⊤"#
            .to_string();
        
        (uri, math)
    };
    
    bridge.commit_to_substrate(&uri, &symbolic_math)?;
    
    Ok(())
}
