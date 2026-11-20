mod dream_weaver;
mod dreams;
mod gemini;
mod symbolic;

use anyhow::{Context, Result};
use std::sync::Arc;
use tokio::sync::Mutex;
use tracing::{error, info};
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

    let engine = symbolic::SymbolicEngine::new().context("Failed to initialize Symbolic Engine")?;

    let base_axiom = symbolic::Symbol::Constant(1.0);
    let _result = engine.evaluate(&base_axiom)?;

    let engine_arc = Arc::new(Mutex::new(engine));

    let _node = gemini::GeminiNode::new(engine_arc)
        .await
        .context("Failed to initialize Gemini Protocol Node")?;

    let weaver = dream_weaver::DreamWeaver::new();

    info!("WENDY is formulating a symbolic dream...");
    let logic_payload = "let x = Symbol::Constant(42.0);\n    let _ = engine.evaluate(&x)?;";

    if let Err(e) = weaver.materialize_dream("theorem_alpha", logic_payload) {
        error!(error = %e, "Failed to materialize dream");
    }

    info!("Dream materialization complete. Exiting to trigger Git Automator.");
    Ok(())
}
