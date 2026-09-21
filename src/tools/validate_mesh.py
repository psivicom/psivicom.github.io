#!/usr/bin/env python3
# src/tools/validate_mesh.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# 
# Mesh Validation Script - Checks all paths and imports before execution
# Run this BEFORE any agent or workflow to catch broken configurations

import sys
import json
from pathlib import Path
from typing import List, Tuple

class MeshValidator:
    """Validates mesh configuration before execution"""
    
    def __init__(self):
        self.root = Path(__file__).parent.parent.parent
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def check_file_exists(self, path: str, description: str) -> bool:
        """Check if a required file exists"""
        full_path = self.root / path
        if not full_path.exists():
            self.errors.append(f"❌ MISSING {description}: {path}")
            return False
        print(f"✓ Found {description}: {path}")
        return True
    
    def check_imports(self, file_path: str, expected_imports: List[str]) -> bool:
        """Check if a file contains expected import statements"""
        full_path = self.root / file_path
        if not full_path.exists():
            return False
        
        content = full_path.read_text()
        for imp in expected_imports:
            if imp not in content:
                self.warnings.append(f"⚠️  {file_path} may be missing import: {imp}")
        
        return True
    
    def check_osdr_data(self) -> bool:
        """Verify OSDR ground truth data exists and is valid"""
        osdr_path = self.root / "data" / "osdr_ground_truth.jsonl"
        if not osdr_path.exists():
            self.errors.append("❌ MISSING OSDR data: data/osdr_ground_truth.jsonl")
            return False
        
        # Validate first line is valid JSON
        try:
            with open(osdr_path) as f:
                first_line = f.readline()
                json.loads(first_line)
            print(f"✓ OSDR data valid: {osdr_path}")
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"❌ INVALID OSDR data: {e}")
            return False
    
    def check_directory_structure(self) -> bool:
        """Verify expected directory structure exists"""
        required_dirs = [
            "src/agents",
            "src/orchestrator",
            "src/core",
            "src/mesh",
            "src/base",
            "src/tools",
            "data",
            "reports/pico_containers",
            ".github/workflows"
        ]
        
        all_exist = True
        for dir_path in required_dirs:
            full_path = self.root / dir_path
            if not full_path.exists():
                self.errors.append(f"❌ MISSING directory: {dir_path}")
                all_exist = False
            else:
                print(f"✓ Directory exists: {dir_path}")
        
        return all_exist
    
    def check_workflow_files(self) -> bool:
        """Check if workflow files exist (cannot validate content from here)"""
        workflows = [
            ".github/workflows/pilot-scan.yml",
            ".github/workflows/chain-orchestrator.yml"
        ]
        
        for wf in workflows:
            if not (self.root / wf).exists():
                self.warnings.append(f"⚠️  Workflow not found: {wf}")
            else:
                print(f"✓ Workflow exists: {wf}")
        
        return True
    
    def run_all_checks(self) -> bool:
        """Run all validation checks"""
        print("=" * 60)
        print("PSIVI MESH VALIDATION REPORT")
        print("=" * 60)
        print()
        
        self.check_directory_structure()
        print()
        
        self.check_osdr_data()
        print()
        
        self.check_workflow_files()
        print()
        
        # Check critical agent files
        print("Checking critical files...")
        self.check_file_exists("src/agents/pilot_agent.py", "Pilot Agent")
        self.check_file_exists("src/orchestrator/chain_orchestrator.py", "Chain Orchestrator")
        self.check_file_exists("src/base/base_agent.py", "Base Agent")
        self.check_file_exists("src/core/psvc_reference.py", "PSVC Reference")
        print()
        
        # Summary
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for err in self.errors:
                print(f"  {err}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warn in self.warnings:
                print(f"  {warn}")
        
        if not self.errors and not self.warnings:
            print("\n✅ ALL CHECKS PASSED - Mesh is ready to run")
            return True
        elif not self.errors:
            print("\n⚠️  WARNINGS ONLY - Mesh can run but may have issues")
            return True
        else:
            print("\n❌ CRITICAL ERRORS - Fix before running mesh")
            return False


if __name__ == "__main__":
    validator = MeshValidator()
    success = validator.run_all_checks()
    sys.exit(0 if success else 1)
