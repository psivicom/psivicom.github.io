# src/agents/instruction_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import json
from pathlib import Path
from datetime import datetime, timezone
from src.base.base_agent import BaseAgent, AgentLayer

class InstructionAgent(BaseAgent):
    LAYER = AgentLayer.INGESTION
    
    def __init__(self):
        super().__init__("instruction_ingester", capabilities=["queue_processing"])
        self.queue_dir = Path("data/instruction_queue")
        self.processed_dir = Path("data/processed_instructions")
        
    def _run_logic(self):
        """Scans the queue and processes pending instructions."""
        print(f" Scanning instruction queue: {self.queue_dir}")
        
        if not self.queue_dir.exists():
            print("⚠️ Queue directory does not exist. Creating it.")
            self.queue_dir.mkdir(parents=True, exist_ok=True)
            return []

        files = list(self.queue_dir.glob("*.json"))
        if not files:
            print("💤 No pending instructions in queue.")
            return []

        processed_results = []
        for file_path in sorted(files, key=lambda p: p.stat().st_mtime):
            try:
                print(f"Processing: {file_path.name}")
                data = json.loads(file_path.read_text())
                
                # Simulate processing logic
                command = data.get("command", "unknown")
                params = data.get("params", {})
                
                result = {
                    "original_id": file_path.stem,
                    "command": command,
                    "status": "completed",
                    "output_summary": f"Executed {command} with {len(params)} parameters.",
                    "timestamp": datetime.now(timezone.utc).isoformat(timespec='microseconds')
                }
                
                processed_results.append(result)
                
                # Move to processed folder
                self.processed_dir.mkdir(exist_ok=True)
                dest_path = self.processed_dir / file_path.name
                file_path.rename(dest_path)
                
                # Record in receipt chain
                self.seal("process_instruction", {"command": command, "source_file": str(file_path)})
                
            except Exception as e:
                print(f"❌ Error processing {file_path.name}: {e}")
                # Optionally move to failed folder
                
        return processed_results

    def finalize(self):
        """Writes the summary report of ingested instructions."""
        results = self._run_logic()
        
        report_path = Path("reports/instruction_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        report_data = {
            "generated_at": datetime.now(timezone.utc).isoformat(timespec='microseconds'),
            "total_processed": len(results),
            "details": results
        }
        
        report_path.write_text(json.dumps(report_data, indent=2))
        print(f"📄 Instruction report written to {report_path}")
        
        # Seal the agent's own result using the base method
        # We pass an empty array as signal since this agent produces logs/reports, not vectors
        self.seal_result([], Path("reports"), meta={"type": "instruction_batch"})

if __name__ == "__main__":
    agent = InstructionAgent()
    agent.finalize()
