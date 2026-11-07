mod symbolic;
mod gemini;
mod dream_weaver;
mod dreams;

use anyhow::{Context, Result};
use tracing::{info, error};
use tracing_subscriber::fmt::format::FmtSpan;

#[tokio::main]
async fn main() -> Result<()> {
    let timer = tracing_subscriber::fmt::time::UtcTime::rfc_3339();
    tracing_subscriber::fmt()
        .with_timer(timer)
        .with_span_events(FmtSpan::CLOSE)
        .with_target(false)
        .init();

    info!("Initializing WENDY Symbolic Core...");
    
    let _engine = symbolic::SymbolicEngine::new()
        .context("Failed to initialize Symbolic Engine")?;

    let weaver = dream_weaver::DreamWeaver::new();
    
    info!("WENDY is formulating a symbolic dream...");
    let logic_payload = "let x = Symbol::Constant(42.0);\n    engine.evaluate(&x)?;";
    
    if let Err(e) = weaver.materialize_dream("theorem_alpha", logic_payload) {
        error!(error = %e, "Failed to materialize dream");
    }

    info!("Dream materialization complete. Exiting to trigger Git Automator.");
    Ok(())
}
