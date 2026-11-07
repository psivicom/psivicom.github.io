mod symbolic;
mod gemini;

use anyhow::{Context, Result};
use tracing::{info, error};
use tracing_subscriber::fmt::format::FmtSpan;

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing with strict Zulu (UTC) timestamps and millisecond precision
    let timer = tracing_subscriber::fmt::time::UtcTime::rfc_3339();
    tracing_subscriber::fmt()
        .with_timer(timer)
        .with_span_events(FmtSpan::CLOSE)
        .with_target(false)
        .init();

    info!("Initializing WENDY Symbolic Core...");
    
    let engine = symbolic::SymbolicEngine::new()
        .context("Failed to initialize Symbolic Engine")?;
        
    let node = gemini::GeminiNode::new(engine)
        .await
        .context("Failed to initialize Gemini Protocol Node")?;

    info!("WENDY is online. Listening for symbolic mesh sync...");
    
    if let Err(e) = node.run_mesh().await {
        error!(error = %e, "WENDY Mesh Sync encountered a fatal error");
        return Err(e);
    }

    Ok(())
}
