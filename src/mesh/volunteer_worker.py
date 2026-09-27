# src/mesh/volunteer_worker.py
import os
import json
from pathlib import Path
from datetime import datetime, timezone

def main():
    print("👷 Volunteer Worker Starting...")
    
    # Example task: Check for pending instructions in queue
    queue_dir = Path("data/instruction_queue")
    if queue_dir.exists():
        files = list(queue_dir.glob("*.json"))
        if files:
            print(f"Found {len(files)} instructions. Processing oldest...")
            # Placeholder logic
            oldest = sorted(files, key=lambda f: f.stat().st_mtime)[0]
            try:
                data = json.loads(oldest.read_text())
                print(f"Processing: {data.get('command', 'unknown')}")
                # Move to processed folder or delete
                processed_dir = Path("data/processed_instructions")
                processed_dir.mkdir(exist_ok=True)
                oldest.rename(processed_dir / oldest.name)
                print("✅ Instruction processed.")
            except Exception as e:
                print(f"❌ Error processing instruction: {e}")
        else:
            print("💤 No instructions in queue.")
    else:
        print("⚠️ Instruction queue directory missing.")

if __name__ == "__main__":
    main()
