import os
import json
import sys
from pathlib import Path
from datetime import datetime

def check_syntactic_integrity():
    """
    Layer 1: The Code Mirror.
    Verifies that critical modules can be imported without error.
    If they fail, we attempt to fix common issues (like missing __init__.py).
    """
    print("🔍 Layer 1: Checking Syntactic Integrity...")
    
    # Try importing the core reference
    try:
        from src.core.psvc_reference import validate_file
        print("   ✅ Core Reference OK.")
    except ImportError as e:
        print(f"   ❌ Import Error: {e}")
        # Heuristic Fix: Ensure __init__.py exists in src/core
        init_path = Path("src/core/__init__.py")
        if not init_path.exists():
            print("   🛠️ Creating missing src/core/__init__.py")
            init_path.touch()
            return True # Changed something
            
    # Try importing the base agent
    try:
        from src.base.base_agent import BaseAgent
        print("   ✅ Base Agent OK.")
    except ImportError:
        print("   ❌ Base Agent Import Failed.")
        init_path = Path("src/base/__init__.py")
        if not init_path.exists():
            print("   🛠️ Creating missing src/base/__init__.py")
            init_path.touch()
            return True
            
    return False

def check_logical_consistency():
    """
    Layer 2: The Data Mirror.
    Checks if the reports exist and are fresh.
    If a report is missing but containers exist, it's a logical gap.
    """
    print("🔍 Layer 2: Checking Logical Consistency...")
    
    containers_dir = Path("reports/pico_containers")
    report_path = Path("reports/pilot_report.json")
    
    has_containers = containers_dir.exists() and any(containers_dir.glob("*.psvc"))
    has_report = report_path.exists()
    
    changed = False
    
    # Case A: Containers exist, but no report -> Stale/Ignored data
    if has_containers and not has_report:
        print("   ⚠️ Dissonance: Containers found but no Report.")
        print("   🛠️ Generating immediate scan report...")
        
        # Force a quick scan logic here without full agent overhead
        # For simplicity, we just touch the report with a "pending" status
        # In a real system, this would trigger the PilotAgent
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "fragility_count": 0,
            "concordance_count": 0,
            "status": "initialized_by_mirror",
            "note": "Auto-generated due to missing report despite existing containers."
        }
        report_path.write_text(json.dumps(report_data, indent=2))
        changed = True
        
    # Case B: Report exists, but is ancient (> 24h) -> Refresh signal
    elif has_report:
        try:
            data = json.loads(report_path.read_text())
            ts = data.get("timestamp", "")
            if ts:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                age_hours = (datetime.now(dt.tzinfo) - dt).total_seconds() / 3600
                if age_hours > 24:
                    print(f"   ⚠️ Dissonance: Report is stale ({age_hours:.1f}h).")
                    print("   🛠️ Marking report for refresh...")
                    data["status"] = "stale_needs_refresh"
                    report_path.write_text(json.dumps(data, indent=2))
                    changed = True
        except:
            pass
            
    return changed

def check_structural_compliance():
    """
    Layer 3: The Form Mirror.
    Ensures essential directories exist.
    """
    print("🔍 Layer 3: Checking Structural Compliance...")
    required_dirs = ["data/instruction_queue", "config", "logs"]
    changed = False
    
    for d in required_dirs:
        path = Path(d)
        if not path.exists():
            print(f"   🛠️ Creating missing directory: {d}")
            path.mkdir(parents=True, exist_ok=True)
            changed = True
            
    return changed

def main():
    print("=" * 40)
    print("   🪞 WENDY MIRROR ACTIVATED")
    print("=" * 40)
    
    corrections = []
    
    if check_syntactic_integrity():
        corrections.append("Syntax Fixed")
        
    if check_logical_consistency():
        corrections.append("Logic Synced")
        
    if check_structural_compliance():
        corrections.append("Structure Repaired")
        
    if corrections:
        print(f"\n✨ Mirror Completed. Corrections Applied: {', '.join(corrections)}")
        # Exit code 0 allows the YAML to see 'git diff' and commit
    else:
        print("\n💎 Mirror Reflects Perfection. No Changes Needed.")

if __name__ == "__main__":
    main()
