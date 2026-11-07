#!/usr/bin/env bash
#
# bootstrap-wendy.sh
# Initializes the local development environment for WENDY Symbolic Core
# Author: Louis-Philippe Audette (Emperor ♠️🪽)
#

set -euo pipefail
IFS=$'\n\t'

# Strict error handling and Zulu timestamp logging
log() {
    local TIMESTAMP
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")
    echo "[${TIMESTAMP}] $1"
}

error_exit() {
    log "FATAL: $1"
    exit 1
}

log "Bootstrapping WENDY Symbolic Engine environment..."

# Check for Rust/Cargo
if ! command -v cargo &> /dev/null; then
    error_exit "Rust toolchain (cargo) is not installed. Please install via rustup."
fi

log "Validating Cargo version..."
cargo --version

# Install required system dependencies for Gemini/TLS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    log "Checking system dependencies..."
    sudo apt-get update && sudo apt-get install -y build-essential pkg-config libssl-dev || error_exit "Failed to install system dependencies."
fi

log "Building WENDY core..."
cargo build --release || error_exit "Cargo build failed."

log "Bootstrap complete. WENDY is ready for symbolic computation."
