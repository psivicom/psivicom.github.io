mod daemon;
mod topology;
mod veto;

use tokio::net::TcpListener;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tracing::{info, error};
use tracing_subscriber::{fmt, EnvFilter};
use time::macros::format_description;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::Mutex;

#[derive(Debug, Serialize, Deserialize)]
pub struct IpcPayload {
    pub action: String,
    pub uri: String,
    pub payload: String,
}

#[tokio::main]
async fn main() {
    // 1. Strict Zulu (UTC) Formatting with Millisecond Precision
    let format = format_description!(
        "[year]-[month]-[day]T[hour]:[minute]:[second].[subsecond digits:3]Z"
    );
    // FIXED: UtcTime::new() now takes only 1 argument (the format).
    // It assumes UTC internally, which is exactly what WENDY requires.
    let timer = fmt::time::UtcTime::new(format);

    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::new("info"))
        .with_timer(timer)
        .with_ansi(false)
        .with_target(true)
        .init();

    info!(target: "wendy_cortex", "booting rust substrate | initializing modules");

    // 2. Initialize Subsystems
    let gemini_daemon = Arc::new(Mutex::new(daemon::GeminiDaemon::new("./capsule".to_string())));
    let hebbian_topology = Arc::new(Mutex::new(topology::HebbianTopology::new()));

    // 3. Bind IPC Control Port (1966) for Python Bridge
    let listener = TcpListener::bind("127.0.0.1:1966").await.unwrap();
    info!(target: "wendy_cortex", "ipc_listener bound to 127.0.0.1:1966 | awaiting python orchestrator");

    loop {
        let (mut socket, addr) = listener.accept().await.unwrap();
        let daemon_clone = Arc::clone(&gemini_daemon);
        let topology_clone = Arc::clone(&hebbian_topology);

        tokio::spawn(async move {
            let mut buf = vec![0; 8192];
            let n = match socket.read(&mut buf).await {
                Ok(n) if n > 0 => n,
                _ => return,
            };

            let raw_data = String::from_utf8_lossy(&buf[..n]);
            info!(target: "ipc_server", "received payload from {} | bytes={}", addr, n);

            match serde_json::from_str::<IpcPayload>(&raw_data) {
                Ok(payload) => {
                    if payload.action == "commit" {
                        let mut d = daemon_clone.lock().await;
                        d.write_axiom(&payload.uri, &payload.payload).await;
                        
                        let mut t = topology_clone.lock().await;
                        t.update_weight(&payload.uri, 0.05).await;
                        
                        let _ = socket.write_all(b"ACK").await;
                    }
                }
                Err(e) => {
                    error!(target: "ipc_server", "failed to parse json payload | error={}", e);
                    let _ = socket.write_all(b"ERR").await;
                }
            }
        });
    }
}
