# src/agents/report_generator_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import json
import logging
from pathlib import Path
from typing import Dict, Any

from src.base.base_agent import BaseAgent, AgentLayer
from src.core.zulu_clock import get_zulu_timestamp_ms

logger = logging.getLogger("REPORT_GENERATOR")

class ReportGeneratorAgent(BaseAgent):
    LAYER = AgentLayer.SYNTHESIS

    def __init__(self, name: str = "report_generator_agent"):
        super().__init__(name=name, capabilities=["generate_report", "format_markdown", "seal_artifact"])
        self.reports_dir = Path("reports/scientific_reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _run_logic(self, data: Dict[str, Any], report_type: str = "scientific") -> str:
        logger.info(f"Generating {report_type} report...")
        
        ts_safe = get_zulu_timestamp_ms().replace(':', '').replace('-', '').replace('.', '')
        filename = f"report_{report_type}_{ts_safe}.md"
        filepath = self.reports_dir / filename
        
        report_content = f"""# {report_type.replace('_', ' ').title()} Report
**Generated:** {get_zulu_timestamp_ms()}
**Agent:** {self.name}
**Layer:** {self.LAYER.value}

## Summary
{json.dumps(data.get('summary', 'No summary provided.'), indent=2)}

## Data
{json.dumps(data.get('data', {}), indent=2)}

## Conclusion
{data.get('conclusion', 'Analysis complete.')}
"""
        filepath.write_text(report_content, encoding="utf-8")
        logger.info(f"✅ Report sealed: {filepath}")
        return str(filepath)

    def execute(self, data: Dict[str, Any], report_type: str = "scientific") -> Dict[str, Any]:
        return super().execute(data=data, report_type=report_type)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    agent = ReportGeneratorAgent()
    result = agent.execute({
        "summary": "Test run completed successfully.", 
        "data": {"metric": 1.0, "divergence": 0.0}, 
        "conclusion": "System is harmonious."
    })
    print(json.dumps(result, indent=2))
