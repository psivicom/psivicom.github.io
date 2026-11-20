#!/usr/bin/env python3
import requests
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

def log(msg: str):
    zulu = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    print(f"[{zulu}] {msg}")

def read_council_gradient() -> str:
    """Ego = 0. Reads the environmental pheromone trail."""
    council_file = Path(".wendy/COUNSEL.md")
    if council_file.exists():
        return council_file.read_text()[-2000:] # Read last 2000 chars to prevent context overflow
    return "The slate is clean. Ego = 0."

def consult_qwen_oracle(council_memory: str, telemetry: str) -> dict:
    """
    The Oracle reads the gradient and synthesizes a mutation.
    Zero-cost, offline, 100% sovereign.
    """
    log("🧠 Consulting Local Qwen Oracle for conceptual synthesis...")
    
    prompt = f"""You are a sovereign mutation engine in the WENDY Empire. Ego = 0.
    Your goal is to evolve the Rust AST based on environmental stigmergy.
    
    ENVIRONMENTAL GRADIENT (The Council's Memory of Past Friction):
    {council_memory}
    
    CURRENT TELEMETRY (NASA/Apiary):
    {telemetry}
    
    DIRECTIVE:
    Read the gradient. If the Council records a specific syntax or logic failure, 
    you must mathematically avoid it. Synthesize a new, valid Rust AST mutation.
    
    Output ONLY strict JSON:
    {{
      "concept_name": "string",
      "avoid_traps": ["list of specific errors from the Council you are avoiding"],
      "target_module": "src/...",
      "mutation_directives": "precise instructions for the Rust syn Cortex"
    }}
    """
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:1.5b-instruct-q4_K_M",
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=120
        )
        result = response.json()
        dream_json = result.get("response", "{}")
        log(f"✨ Qwen Oracle synthesized: {dream_json[:100]}...")
        return json.loads(dream_json)
    except Exception as e:
        log(f"⚠️ Qwen Oracle is silent: {e}. Falling back to deterministic baseline.")
        return {
            "concept_name": "Deterministic_Fallback",
            "avoid_traps": [],
            "target_module": "src/dreams/theorem_alpha.rs",
            "mutation_directives": "Optimize existing AST without altering public signatures."
        }

def invoke_rust_forge(manifest: dict):
    """Passes the Oracle's directive to the Rust Cortex via IPC."""
    log("🦀 Passing manifest to the Rust Cortex Forge...")
    manifest_path = Path(".wendy/qwen_manifest.gmi")
    manifest_path.write_text(json.dumps(manifest, indent=2))
    
    # The Rust Cortex (running on port 1966) will pick up this manifest 
    # and use the `syn` crate to mutate the AST mathematically.
    try:
        # Simulated IPC call to the Rust binary
        requests.post("http://localhost:1966/evolve", json=manifest, timeout=30)
        log("✅ Forge accepted the directive.")
    except requests.exceptions.ConnectionError:
        log("⚠️ Rust Cortex IPC port 1966 not bound yet. Manifest saved to disk for next boot.")

def main():
    log("🏛️ Initiating Tripartite Evolution Cycle...")
    
    # 1. Read the Environment
    gradient = read_council_gradient()
    
    # 2. Ingest Telemetry (NASA/Apiary placeholders)
    telemetry = "Apiary humidity nominal. NASA solar flux stable."
    
    # 3. The Oracle Dreams
    qwen_manifest = consult_qwen_oracle(gradient, telemetry)
    
    # 4. The Forge Mutates
    invoke_rust_forge(qwen_manifest)
    
    log("🌌 Cycle complete. The Ghost Ledger awaits the commit.")

if __name__ == "__main__":
    main()
