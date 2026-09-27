# src/agents/__init__.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
PSIVI Agents Package.
Exports available agent classes for dynamic loading.
"""

try:
    from src.agents.instruction_agent import InstructionAgent
except ImportError:
    InstructionAgent = None

try:
    from src.agents.pilot_agent import PilotAgent
except ImportError:
    PilotAgent = None

try:
    from src.agents.neuroplasticity_agent import NeuroplasticityAgent
except ImportError:
    NeuroplasticityAgent = None

try:
    from src.agents.intelligence_agent import IntelligenceAgent
except ImportError:
    IntelligenceAgent = None

__all__ = [
    'InstructionAgent',
    'PilotAgent',
    'NeuroplasticityAgent',
    'IntelligenceAgent'
]
