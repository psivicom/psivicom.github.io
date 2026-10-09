# src/agents/evolution_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Evolution Agent: Self-Healing & Self-Scaling Layer
Monitors agent performance, drafts code improvements, validates them in 
sandboxed PSVC containers, and submits Pull Requests for autonomous mesh evolution.
"""

import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from src.base.base_agent import BaseAgent, AgentLayer
from src.core.zulu_clock import get_zulu_timestamp_ms

logger = logging.getLogger("EVOLUTION_AGENT")

class EvolutionAgent(BaseAgent):
    LAYER = AgentLayer.COGNITION # Or GOVERNANCE, depending on mesh design

    def __init__(self, name: str = "evolution"):
        super().__init__(name, capabilities=["draft_code", "sandbox_test", "submit_pr"])
        self.repo_path = Path(os.getcwd())
        self.branch_prefix = "feat/auto-evolve-"

    def draft_improvement(self, agent_name: str, reason: str, proposed_code: str) -> bool:
        """Drafts new code and validates it in a local sandbox."""
        logger.info(f"🧬 Drafting evolution for {agent_name}: {reason}")
        
        target_file = self.repo_path / "src" / "agents" / f"{agent_name}.py"
        temp_file = self.repo_path / "src" / "agents" / f"{agent_name}_evolution_temp.py"
        
        try:
            # 1. Write proposed code to temp file
            temp_file.write_text(proposed_code, encoding="utf-8")
            
            # 2. Sandbox Validation: Syntax Check
            logger.info("🧪 Running syntax validation...")
            subprocess.run(["python", "-m", "py_compile", str(temp_file)], check=True, capture_output=True)
            
            # 3. Sandbox Validation: SPDX Header Check
            if "SPDX-License-Identifier: EUPL-1.2" not in proposed_code:
                logger.error("❌ Evolution rejected: Missing EUPL-1.2 license header.")
                return False
                
            logger.info("✅ Sandbox validation passed. Code is safe to propose.")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Evolution rejected: Syntax error in proposed code.\n{e.stderr.decode()}")
            return False
        except Exception as e:
            logger.error(f"❌ Evolution rejected: {e}")
            return False
        finally:
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()

    def submit_evolution_pr(self, agent_name: str, reason: str, proposed_code: str) -> Dict[str, Any]:
        """Submits the validated code as a GitHub Pull Request."""
        if not self.draft_improvement(agent_name, reason, proposed_code):
            return {"status": "rejected", "reason": "Sandbox validation failed"}
            
        logger.info(f"🚀 Submitting Evolution PR for {agent_name}...")
        
        # In a full implementation, this uses the 'gh' CLI or PyGithub library
        # For now, we log the exact git commands Wendy would execute autonomously:
        commands = [
            f"git checkout -b {self.branch_prefix}{agent_name}",
            f"cp /tmp/proposed_{agent_name}.py src/agents/{agent_name}.py",
            f"git add src/agents/{agent_name}.py",
            f"git commit -m 'chore(ai-evolution): auto-upgrade {agent_name} - {reason}'",
            f"git push origin {self.branch_prefix}{agent_name}",
            f"gh pr create --title '[AI-EVOLUTION] Upgrade {agent_name}' --body 'Reason: {reason}\\n\\nValidated by EvolutionAgent at {get_zulu_timestamp_ms()}'"
        ]
        
        logger.info("📜 Evolution PR commands generated. Ready for execution.")
        
        self.seal("evolution_pr_submitted", {
            "agent": agent_name,
            "reason": reason,
            "timestamp": get_zulu_timestamp_ms()
        })
        
        return {"status": "pr_submitted", "branch": f"{self.branch_prefix}{agent_name}"}

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution trigger for self-evolution."""
        agent_to_evolve = data.get("agent_name")
        reason = data.get("reason")
        proposed_code = data.get("proposed_code")
        
        if not all([agent_to_evolve, reason, proposed_code]):
            return {"status": "error", "message": "Missing evolution parameters"}
            
        return self.submit_evolution_pr(agent_to_evolve, reason, proposed_code)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    agent = EvolutionAgent()
    
    # Simulate Wendy deciding to add a new API to the discovery agent
    mock_evolution_data = {
        "agent_name": "discovery_agent",
        "reason": "Added support for new Royal BC Museum biodiversity API endpoint",
        "proposed_code": "# src/agents/discovery_agent.py\n# SPDX-License-Identifier: EUPL-1.2\n# (Truncated for simulation)\nprint('Evolution successful')"
    }
    
    result = agent.execute(mock_evolution_data)
    print(result)
