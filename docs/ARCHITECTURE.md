# WENDY Symbolic Architecture

## Core Philosophy
WENDY bypasses the probabilistic hallucinations of Large Language Models (LLMs) by utilizing **Mathematical Symbolic Text** and **First-Order Logic**. It requires zero GPU acceleration, relying entirely on highly optimized CPU instruction sets via Rust.

## The Gemini Protocol Integration
Instead of relying on centralized cloud GPUs, WENDY distributes its symbolic reasoning workload across a peer-to-peer mesh using the **Gemini Protocol** (`gemini://`). This ensures:
1. **Decentralization**: No single point of failure.
2. **Lightweight Sync**: Text-based symbolic state transfer requires minimal bandwidth.
3. **Self-Healing**: If a node drops, the mesh automatically recalculates the symbolic logic tree.

## Strict Engineering Standards
- All logs and artifacts are stamped with **Zulu (UTC) timestamps** down to the millisecond.
- **OIDC Tokens** are used for all CI/CD deployments to ensure scoped, secure permissions.
- **Race conditions** in symbolic evaluation are prevented via Rust's `Arc<Mutex<T>>` concurrency model.
