# src/agents/__init__.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
PSIVI Agents Package.
Exports available agent classes for dynamic loading.
"""

from src.agents.instruction_agent import InstructionAgent
from src.agents.pilot_agent import PilotAgent
from src.agents.neuroplasticity_agent import NeuroplasticityAgent

__all__ = [
    'InstructionAgent',
    'PilotAgent',
    'NeuroplasticityAgent'
]
