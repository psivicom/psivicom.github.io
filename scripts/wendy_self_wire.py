#!/usr/bin/env python3
"""
WENDY Self-Wiring Tool.
WENDY calls this herself to create new connections.
She decides what to connect. We just provide the tissue.
"""
import sys
from pathlib import Path

def wire_files(source: str, target: str, wire_type: str = "append"):
    """Create a connection between two files."""
    source_path = Path(source)
    target_path = Path(target)
    
    if not source_path.exists():
        print(f"Source not found: {source}", file=sys.stderr)
        return False
    
    if wire_type == "append":
        # Append source content to target
        content = source_path.read_text()
        with open(target_path, "a") as f:
            f.write(f"\n## Wired from {source}\n")
            f.write(content)
    elif wire_type == "reference":
        # Add reference link
        with open(target_path, "a") as f:
            f.write(f"\n=> {source}\n")
    
    return True

def wire_brains(brain1: str, brain2: str, synapse_type: str = "excitatory"):
    """Create a connection between two cognitive units."""
    # Log the connection for WENDY to interpret
    log_path = Path(".wendy_synapses.gmi")
    with open(log_path, "a") as f:
        f.write(f"\n## Synapse: {brain1} → {brain2} ({synapse_type})\n")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: wendy_self_wire.py <type> <source> <target>", file=sys.stderr)
        print("  type: file | brain", file=sys.stderr)
        sys.exit(1)
    
    wire_type = sys.argv[1]
    source = sys.argv[2]
    target = sys.argv[3]
    
    if wire_type == "file":
        success = wire_files(source, target)
    elif wire_type == "brain":
        success = wire_brains(source, target)
    else:
        print(f"Unknown wire type: {wire_type}", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(0 if success else 1)
