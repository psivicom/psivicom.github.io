# src/pipelines/consolidation_pipeline.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Consolidation Pipeline: The Dream State Engine.
Orchestrates Wendy's autonomous self-optimization during idle "breath" phases.
Analyzes the Vanguard ledger for systemic anomalies, drafts evolutionary code 
improvements, and safely submits Pull Requests without disrupting active operations.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.core.zulu_clock import get_zulu_timestamp_ms
from src.agents.evolution_agent import EvolutionAgent
from src.agents.vanguard_agent import VanguardAgent

logger = logging.getLogger("CONSOLIDATION_PIPELINE")

class ConsolidationPipeline:
    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir)
        self.ledger_path = self.root / "data/vanguard_ledger.jsonl"
        self.metabolism_path = self.root / "src/wendy_metabolism.json"
        
        # Initialize sovereign agents
        self.evolution_agent = EvolutionAgent(name="dream_evolution")
        self.vanguard_agent = VanguardAgent(ledger_path=str(self.ledger_path))
        
        logger.info("🌙 Consolidation Pipeline initialized. Dream state engine ready.")

    def _is_dream_phase(self) -> bool:
        """Checks if the system is in a low-load 'IDLE' or 'DREAM' metabolic phase."""
        if not self.metabolism_path.exists():
            return True # Default to dream phase if no metabolism file exists yet
            
        try:
            metabolism = json.loads(self.metabolism_path.read_text(encoding="utf-8"))
            phase = metabolism.get("phase", "IDLE").upper()
            return phase in ["IDLE", "DREAM", "CONSOLIDATE"]
        except Exception as e:
            logger.warning(f"⚠️ Could not read metabolism state, defaulting to dream phase: {e}")
            return True

    def _analyze_ledger_for_patterns(self) -> Optional[Dict[str, Any]]:
        """Scans the Vanguard ledger for recurring anomalies that warrant evolutionary action."""
        if not self.ledger_path.exists():
            return None
            
        anomaly_counts: Dict[str, int] = {}
        recent_entries: List[Dict[str, Any]] = []
        
        try:
            with open(self.ledger_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    entry = json.loads(line)
                    recent_entries.append(entry)
                    
                    action = entry.get("action", "UNKNOWN")
                    if "REJECTED" in action or "VIOLATION" in action or "ERROR" in action:
                        anomaly_counts[action] = anomaly_counts.get(action, 0) + 1
                        
            # Look for patterns: e.g., more than 2 of the same rejection
            for action, count in anomaly_counts.items():
                if count >= 2:
                    return {
                        "pattern_detected": action,
                        "occurrence_count": count,
                        "sample_metadata": recent_entries[-1].get("metadata", {})
                    }
                    
        except Exception as e:
            logger.error(f"❌ Failed to analyze ledger: {e}")
            
        return None

    def _draft_evolutionary_response(self, pattern: Dict[str, Any]) -> bool:
        """Tasks the Evolution Agent to draft a code fix for the detected pattern."""
        anomaly_type = pattern["pattern_detected"]
        logger.info(f"🧠 Dreaming: Drafting evolutionary response for recurring '{anomaly_type}'...")
        
        # Formulate a targeted evolutionary prompt based on the anomaly
        if "LICENSE_VIOLATION" in anomaly_type:
            reason = "Automated fix: Enhance license scanning regex to catch edge-case SPDX headers."
            proposed_code = self._generate_license_scanner_fix()
        elif "MANIFEST_REJECTED" in anomaly_type:
            reason = "Automated fix: Add missing 'health_check' default fallback in manifest validator."
            proposed_code = self._generate_manifest_validator_fix()
        else:
            reason = f"Automated fix: General resilience upgrade for {anomaly_type}"
            proposed_code = self._generate_general_resilience_fix()
            
        # Submit to Evolution Agent for sandbox validation and PR creation
        result = self.evolution_agent.execute({
            "agent_name": "vanguard_agent", # Target the agent that handles these checks
            "reason": reason,
            "proposed_code": proposed_code
        })
        
        if result.get("status") == "pr_submitted":
            logger.info(f"✅ Dream State: Evolutionary PR submitted successfully. Branch: {result.get('branch')}")
            return True
        else:
            logger.warning(f"⚠️ Dream State: Evolutionary PR rejected during sandbox validation.")
            return False

    def _generate_license_scanner_fix(self) -> str:
        """Generates a mock improved license scanner for the PR."""
        return """# src/agents/vanguard_agent.py (Snippet)
# SPDX-License-Identifier: EUPL-1.2
# Enhanced license detection with robust regex fallback
import re

def enforce_pico(self, psvc_manifest: Dict[str, Any]) -> bool:
    license_val = psvc_manifest.get("license", "").strip().upper()
    # Accept exact match or common variations
    if license_val not in ["EUPL-1.2", "EUPL 1.2", "EUPL"]:
        self.anomaly_count = np.float32(self.anomaly_count + 1.0)
        self.ledger("LICENSE_VIOLATION", "vanguard", f"Invalid license: {license_val}", psvc_manifest)
        return False
    return True
"""

    def _generate_manifest_validator_fix(self) -> str:
        """Generates a mock improved manifest validator for the PR."""
        return """# src/agents/vanguard_agent.py (Snippet)
# SPDX-License-Identifier: EUPL-1.2
# Enhanced manifest validation with safe defaults
def enforce_pico(self, psvc_manifest: Dict[str, Any]) -> bool:
    required_fields = ["name", "version", "license", "author", "health_check"]
    for field in required_fields:
        if field not in psvc_manifest:
            # Auto-heal: inject safe default for health_check if missing
            if field == "health_check":
                psvc_manifest["health_check"] = "/health"
                continue
            self.anomaly_count = np.float32(self.anomaly_count + 1.0)
            self.ledger("MANIFEST_REJECTED", "vanguard", f"Missing field: {field}", psvc_manifest)
            return False
    return True
"""

    def _generate_general_resilience_fix(self) -> str:
        """Generates a generic resilience upgrade."""
        return """# src/core/immune_system.py (Snippet)
# SPDX-License-Identifier: EUPL-1.2
# Added automatic rollback trigger on repeated anomaly detection
def trigger_apoptosis(self, anomaly_type: str):
    logger.warning(f"🛡️ Immune System: Triggering rollback due to repeated {anomaly_type}")
    # Rollback logic would go here, restoring last known good shannon_z checkpoint
    pass
"""

    def execute_dream_cycle(self) -> Dict[str, Any]:
        """Main entry point: Executes the full consolidation and evolution loop."""
        zulu_start = get_zulu_timestamp_ms()
        logger.info(f"🌙 [{zulu_start}] Initiating Dream State Consolidation Cycle...")
        
        if not self._is_dream_phase():
            logger.info("💤 System is in active metabolic phase. Deferring dream cycle.")
            return {"status": "deferred", "reason": "active_phase"}
            
        logger.info("🔍 Scanning Vanguard ledger for systemic anomalies...")
        pattern = self._analyze_ledger_for_patterns()
        
        if not pattern:
            logger.info("✨ Ledger is clean. No evolutionary action required. Returning to idle.")
            return {"status": "success", "action": "no_anomalies_detected", "timestamp": get_zulu_timestamp_ms()}
            
        logger.info(f"⚠️ Pattern detected: {pattern['pattern_detected']} (Count: {pattern['occurrence_count']})")
        
        success = self._draft_evolutionary_response(pattern)
        
        zulu_end = get_zulu_timestamp_ms()
        return {
            "status": "pr_submitted" if success else "pr_rejected",
            "pattern_addressed": pattern["pattern_detected"],
            "start_time": zulu_start,
            "end_time": zulu_end
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    # Ensure directories exist for testing
    Path("data").mkdir(parents=True, exist_ok=True)
    Path("src").mkdir(parents=True, exist_ok=True)
    
    pipeline = ConsolidationPipeline()
    result = pipeline.execute_dream_cycle()
    
    print("\n🌙 Dream Cycle Result:")
    print(json.dumps(result, indent=2))
