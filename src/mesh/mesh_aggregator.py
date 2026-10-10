# src/mesh/mesh_aggregator.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Sovereign Mesh Aggregator: The Heartbeat Generator.
Reads the immutable Vanguard ledger and calculates the current health,
consensus state, and actuation metrics of the mesh. Outputs a human-readable
status report to reports/mesh_status.txt.
"""

import json
import logging
from pathlib import Path
from collections import Counter

from src.core.zulu_clock import get_zulu_timestamp_ms

logger = logging.getLogger("MESH_AGGREGATOR")

class MeshAggregator:
    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir)
        self.ledger_path = self.root / "data/vanguard_ledger.jsonl"
        self.report_path = self.root / "reports/mesh_status.txt"
        self.report_path.parent.mkdir(parents=True, exist_ok=True)

    def aggregate(self) -> str:
        """Reads the ledger and generates a comprehensive mesh status report."""
        logger.info("📊 Aggregating sovereign mesh state...")
        
        if not self.ledger_path.exists():
            return "⚠️ Mesh Ledger not found. Node may be in Genesis state."

        actions = []
        recent_events = []
        
        try:
            with open(self.ledger_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip(): continue
                    entry = json.loads(line)
                    actions.append(entry.get("action", "UNKNOWN"))
                    recent_events.append(entry)
        except Exception as e:
            logger.error(f"❌ Failed to read ledger: {e}")
            return "❌ Ledger corruption detected."

        # Calculate Metrics
        action_counts = Counter(actions)
        total_events = len(actions)
        immune_responses = action_counts.get("IMMUNE_APOPTOSIS", 0)
        consensus_seals = action_counts.get("CONSENSUS_SEALED", 0)
        robotic_dispatches = action_counts.get("ROBOTIC_DISPATCH", 0)
        
        # Get the latest event timestamp
        last_event_time = "N/A"
        if recent_events:
            last_event_time = recent_events[-1].get("timestamp", "N/A")

        # Generate Report
        report = f"""
================================================================
🌟 PSIVI AETHER MESH - SOVEREIGN STATUS REPORT 🌟
================================================================
Generated at: {get_zulu_timestamp_ms()}
Last Ledger Event: {last_event_time}

📊 MESH METRICS:
  Total Ledger Events: {total_events}
  Consensus Truths Sealed: {consensus_seals}
  Robotic Actuations Dispatched: {robotic_dispatches}
  Immune System Apoptosis (Self-Healing): {immune_responses}

🛡️ SYSTEM HEALTH:
  {"✅ NOMINAL" if immune_responses < 5 else "⚠️ ELEVATED IMMUNE ACTIVITY"}
  
🧠 RECENT ACTIVITY (Last 5 Events):
"""
        for event in recent_events[-5:]:
            report += f"  - [{event.get('timestamp')}] {event.get('action')} by {event.get('actor')}\n"
            
        report += "\n================================================================\n"
        report += "🔗 Architecture: Sovereign Python/Zig Polyglot Mesh\n"
        report += "🔐 Cryptography: Ed25519 Zero-Trust | Argon2id Encrypted at Rest\n"
        report += "⚖️ License: EUPL-1.2 | FAIR Open Science\n"
        report += "================================================================\n"
        
        return report.strip()

    def publish(self):
        """Writes the aggregated report to the reports directory."""
        report_text = self.aggregate()
        self.report_path.write_text(report_text, encoding='utf-8')
        logger.info(f"✅ Mesh status report published to {self.report_path}")
        return self.report_path

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    aggregator = MeshAggregator()
    aggregator.publish()
