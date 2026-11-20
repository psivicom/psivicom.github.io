//! WENDY IPC Client — Shared module for communicating with the Rust Cortex daemon
//! SPDX-License-Identifier: EUPL-1.2
//!
//! Provides a unified interface for all binaries to transmit telemetry
//! to the running wendy-cortex daemon via TCP on port 1966.
//!
//! Used by: rust_bridge, build_polyglot, mobile_airgap, etc.

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::io::{Read, Write};
use std::net::TcpStream;
use std::time::Duration;

pub const DEFAULT_HOST: &str = "127.0.0.1";
pub const DEFAULT_PORT: u16 = 1966;
pub const TIMEOUT_SECS: u64 = 5;

/// IPC Payload structure matching the daemon's expected format
#[derive(Debug, Serialize, Deserialize)]
pub struct IpcPayload {
    pub action: String,
    pub uri: String,
    pub payload: String,
}

/// Transmit a payload to the Rust Cortex daemon.
/// Returns Ok(true) if ACK received, Ok(false) if rejected, Err on connection failure.
pub fn notify_rust_core(action: &str, uri: &str, payload: &str) -> Result<bool> {
    let ipc = IpcPayload {
        action: action.to_string(),
        uri: uri.to_string(),
        payload: payload.to_string(),
    };
    
    let addr = format!("{}:{}", DEFAULT_HOST, DEFAULT_PORT);
    
    let mut stream = match TcpStream::connect_timeout(
        &addr.parse().context("Invalid address")?,
        Duration::from_secs(TIMEOUT_SECS),
    ) {
        Ok(s) => s,
        Err(e) => {
            // Daemon not running is not fatal — log and continue
            eprintln!(
                "[IPC] Daemon not reachable at {}:{} ({}) | continuing without telemetry",
                DEFAULT_HOST, DEFAULT_PORT, e
            );
            return Ok(false);
        }
    };
    
    stream
        .set_read_timeout(Some(Duration::from_secs(TIMEOUT_SECS)))
        .context("Failed to set read timeout")?;
    
    let json_payload = serde_json::to_string(&ipc)
        .context("Failed to serialize IPC payload")?;
    
    stream
        .write_all(json_payload.as_bytes())
        .context("Failed to write to socket")?;
    stream.flush().context("Failed to flush socket")?;
    
    let mut response_buf = vec![0u8; 1024];
    let bytes_read = stream
        .read(&mut response_buf)
        .context("Failed to read response")?;
    
    let response = String::from_utf8_lossy(&response_buf[..bytes_read]);
    
    if response.trim() == "ACK" {
        Ok(true)
    } else {
        eprintln!("[IPC] Daemon rejected payload | response={}", response);
        Ok(false)
    }
}

/// Convenience wrapper matching the Python `notify_rust_core` signature.
/// Logs success/failure with a caller-provided context label.
pub fn notify_or_log(context: &str, action: &str, uri: &str, payload: &str) {
    match notify_rust_core(action, uri, payload) {
        Ok(true) => {
            // ACK received — silent success
        }
        Ok(false) => {
            eprintln!("[{}] IPC telemetry not acknowledged by daemon", context);
        }
        Err(e) => {
            eprintln!("[{}] IPC error: {}", context, e);
        }
    }
}
