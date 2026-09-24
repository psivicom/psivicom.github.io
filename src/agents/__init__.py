# ==============================================================================
# FILE: __init__.py
# PATH: psivicom.github.io/src/agents/__init__.py
# DESCRIPTION: Package initializer for the agents module.
#              Required for Python to recognize src/agents/ as a package.
# LICENSE: EUPL-1.2 | COMPLIANCE: NIST SP 800-218, FAIR Open Science
# ==============================================================================
# This file is intentionally minimal.
# It tells Python that src/agents/ is a valid package,
# allowing imports like: from src.agents.satellite_agent import SatelliteAgent
# src/agents/__init__.py
# PSIVI Mesh Platform - Agents Package
# Updated to include Instruction and Report Generator agents

from src.agents.instruction_agent import InstructionAgent
from src.agents.report_generator_agent import ReportGeneratorAgent
from src.agents.pilot_agent import PilotAgent
from src.agents.forage_agent import ForageAgent
from src.agents.literature_agent import LiteratureAgent
from src.agents.consolidator_agent import ConsolidatorAgent
from src.agents.critic_agent import CriticAgent
from src.agents.observer_agent import ObserverAgent

__all__ = [
    "InstructionAgent",
    "ReportGeneratorAgent",
    "PilotAgent",
    "ForageAgent",
    "LiteratureAgent",
    "ConsolidatorAgent",
    "CriticAgent",
    "ObserverAgent"
]
