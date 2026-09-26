import os
import json
from pathlib import Path
from datetime import datetime

def run():
    # 1. Check if we need to scan (Simple Logic)
    report = Path("reports/pilot_report.json")
    
    if not report.exists():
        print("🔍 No report found. Scanning...")
        os.system("python -m src.agents.pilot_agent")
    else:
        try:
            data = json.loads(report.read_text())
            ts = data.get("timestamp", "")
            if ts:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                age_hours = (datetime.now() - dt).total_seconds() / 3600
                
                if age_hours > 6:
                    print(f"🕒 Report stale ({age_hours:.1f}h). Rescanning...")
                    os.system("python -m src.agents.pilot_agent")
                else:
                    print("✅ System Fresh. Idle.")
                    return # Stop here, don't commit
        except Exception as e:
            print(f"⚠️ Error reading report: {e}. Rescanning...")
            os.system("python -m src.agents.pilot_agent")

    # 2. Commit Changes
    os.system("git config user.name 'Wendy'")
    os.system("git config user.email 'wendy@psivi.com'")
    os.system("git add reports/")
    
    status = os.popen("git status --porcelain").read().strip()
    if status:
        os.system("git commit -m 'auto: wendy updated mesh state'")
        os.system("git push")
        print("🚀 Pushed updates.")
    else:
        print("💤 No changes to push.")

if __name__ == "__main__":
    run()
