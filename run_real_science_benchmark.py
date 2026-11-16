import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# ============================================================================
# SOVEREIGN BRIDGE: Dynamic Rust Substrate Discovery
# ============================================================================

def zulu_now() -> str:
    """Generates Zulu timestamps with strict millisecond precision."""
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

def find_rust_binary() -> str:
    """Dynamically locates the compiled Rust binary regardless of CWD."""
    env_bin = os.environ.get("WENDY_CORTEX_BIN")
    if env_bin and os.path.isfile(env_bin):
        return env_bin

    current_dir = Path(__file__).resolve().parent
    for parent in [current_dir] + list(current_dir.parents):
        candidate = parent / "wendy-cortex" / "target" / "release" / "wendy-crystalline-executor"
        if candidate.is_file():
            return str(candidate)
        
        candidate_debug = parent / "wendy-cortex" / "target" / "debug" / "wendy-crystalline-executor"
        if candidate_debug.is_file():
            return str(candidate_debug)
    
    raise FileNotFoundError(
        f"❌ [{zulu_now()}] Could not locate wendy-crystalline-executor.\n"
        f"Ensure 'cargo build --release' has executed, or set the WENDY_CORTEX_BIN env var."
    )

class CrystallineExecutor:
    """Python wrapper that invokes the native Rust crystalline executor."""
    BINARY_PATH = find_rust_binary()

    @classmethod
    def run(cls, dream_file: str, manifest_file: str) -> str:
        print(f"[{zulu_now()}] Invoking Rust Substrate: {cls.BINARY_PATH}")
        
        if not os.path.exists(dream_file):
            raise FileNotFoundError(f"❌ [{zulu_now()}] Dream file not found: {dream_file}")

        # Read the dream content to feed via stdin (satisfies Rust binaries that read from std::io::stdin)
        with open(dream_file, "r", encoding="utf-8") as f:
            dream_content = f.read()

        # Execute the Rust binary. 
        # We pass the file as an argument AND pipe it to stdin to satisfy any CLI parser configuration.
        result = subprocess.run(
            [cls.BINARY_PATH, dream_file], 
            input=dream_content,
            capture_output=True, 
            text=True
        )
        
        # DIAGNOSTIC MIRROR: Expose exact Rust panics or CLI errors
        if result.returncode != 0:
            print(f"[{zulu_now()}] ❌ Rust substrate exited with code {result.returncode}.")
            print(f"--- STDOUT ---\n{result.stdout}\n--------------")
            print(f"--- STDERR ---\n{result.stderr}\n--------------")
            sys.exit(1)
            
        with open(manifest_file, "w", encoding="utf-8") as f:
            f.write(result.stdout)
            
        print(f"[{zulu_now()}] Consensus crystallized and written to {manifest_file}")
        return result.stdout

# ============================================================================
# BENCHMARK EXECUTION LAYER
# ============================================================================

def run_benchmark():
    print(f"[{zulu_now()}] === WENDY REAL SCIENCE BENCHMARK INITIATED ===")
    
    print(f"[{zulu_now()}] Rust substrate located at: {CrystallineExecutor.BINARY_PATH}")
    
    dream_file = "benchmark_dream.gmi"
    manifest_file = "benchmark_manifest.gmi"
    
    if not os.path.exists(dream_file):
        print(f"[{zulu_now()}] Generating synthetic dream for benchmark...")
        with open(dream_file, "w", encoding="utf-8") as f:
            f.write("# Synthetic Benchmark Dream\n\n")
            f.write("This is a generated chaos feed to test the crystalline executor's throughput and logic verification.\n")
            f.write("The organism must prove it can parse arbitrary entropy and reach consensus.\n")

    try:
        start_time = datetime.now(timezone.utc)
        output = CrystallineExecutor.run(dream_file, manifest_file)
        end_time = datetime.now(timezone.utc)
        
        duration_ms = (end_time - start_time).total_seconds() * 1000
        print(f"[{zulu_now()}] ✅ Benchmark complete. Execution time: {duration_ms:.2f}ms")
        
        if "CONSENSUS REACHED" in output:
            print(f"[{zulu_now()}] 🧊 Habermasian discourse successful.")
        else:
            print(f"[{zulu_now()}] ⚠️ Habermasian discourse failed to reach consensus.")
            
    except Exception as e:
        print(f"[{zulu_now()}] ❌ Benchmark orchestration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_benchmark()
