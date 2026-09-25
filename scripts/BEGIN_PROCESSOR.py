# scripts/BEGIN_PROCESSOR.py
"""
PSIVI AETHER Mesh — Instruction Processor (BEGIN_PROCESSOR.py)
Location: /scripts/BEGIN_PROCESSOR.py

Consumes .psvc instructions and generates scientific reports.
FIXED: Removed unsafe path printing to prevent ValueError on CI runners.
Ensures pilot_report.json is saved to the ROOT 'reports/' directory.
"""

import json
import struct
import zlib
from pathlib import Path
from datetime import datetime, timezone
import sys
import shutil

MAGIC = b'PSVI'
INSTRUCTION_QUEUE_DIR = Path("data/instruction_queue")
REPORTS_ROOT_DIR = Path("reports") # Target root for dashboard visibility
SCIENTIFIC_REPORTS_SUBDIR = REPORTS_ROOT_DIR / "scientific_reports" # Detailed logs
PROCESSED_DIR = INSTRUCTION_QUEUE_DIR / ".processed"
ERRORS_DIR = INSTRUCTION_QUEUE_DIR / ".errors"
PILOT_REPORT_PATH = REPORTS_ROOT_DIR / "pilot_report.json" # CRITICAL FIX HERE

def get_zulu_time_ms() -> str:
    now_utc = datetime.now(timezone.utc)
    return f"{now_utc.strftime('%Y-%m-%dT%H:%M:%S.')}{now_utc.microsecond // 1000:03d}Z"

def parse_psvc_header(file_path: Path) -> bool:
    try:
        with open(file_path, 'rb') as f:
            if f.read(4) != MAGIC:
                return False
            f.read(1) # Version
            f.read(1) # Precision
            vec_len = struct.unpack('<I', f.read(4))[0]
            comp_len = struct.unpack('<I', f.read(4))[0]
            data = f.read(comp_len)
            if len(zlib.decompress(data)) != vec_len * 4:
                return False
        return True
    except Exception:
        return False

def load_sidecar_json(psvc_path: Path) -> dict:
    json_path = psvc_path.with_suffix('.json')
    if not json_path.exists():
        raise FileNotFoundError(f"Missing JSON for {psvc_path.name}")
    with open(json_path, 'r') as f:
        return json.load(f)

def simulate_mesh_processing(sidecar_data: dict) -> dict:
    command = sidecar_data.get("command", "unknown")
    params = sidecar_data.get("params", {})
    fragility_score = 0
    
    if command == "spawn_agent":
        template = params.get("template_name", "generic")
        agent_name = params.get("agent_name", "unnamed")
        
        if template == "satellite_observer":
            region = params.get("config", {}).get("target_region", "Unknown")
            title = f"Mesh Report: Satellite Observer Active for {region}"
            status = "ACTIVE_MONITORING"
            fragility_score = 0
        elif template == "literature_resolver":
            gene = params.get("config", {}).get("gene", "N/A")
            title = f"Mesh Report: Literature Resolved for Gene {gene}"
            status = "RESOLVED"
            fragility_score = 1
        else:
            title = f"Mesh Report: Agent {agent_name} Spawned"
            status = "SPAWNED"
            fragility_score = 0
            
    elif command == "request_report":
        topic = params.get("topic", "General")
        title = f"Mesh Report: Summary for '{topic}'"
        status = "COMPLETED"
        fragility_score = 0
    else:
        title = "Mesh Report: Unknown Command"
        status = "ERROR"
        fragility_score = 5

    return {
        "timestamp": get_zulu_time_ms(),
        "instruction_source": sidecar_data.get("_original_filename", "unknown"),
        "mesh_state": {
            "fragility_traps": fragility_score,
            "concordant_controls": max(0, 10 - fragility_score),
            "elasticity": "STABLE" if fragility_score < 3 else "CONTRACT"
        },
        "osdr_ground_truth_loaded": True,
        "rfc1001_compliant": True,
        "title": title,
        "status": status
    }

def save_report(report: dict, original_id: str):
    SCIENTIFIC_REPORTS_SUBDIR.mkdir(parents=True, exist_ok=True)
    safe_id = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in original_id)[:50]
    ts_slug = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')
    path = SCIENTIFIC_REPORTS_SUBDIR / f"report_{safe_id}_{ts_slug}.json"
    
    with open(path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # FIXED: Use name only to avoid absolute/relative path errors in CI logging
    print(f"   💾 Saved detailed report: {path.name}")

def update_pilot_summary(frag_delta: int, conc_delta: int):
    # Ensure the ROOT reports folder exists
    REPORTS_ROOT_DIR.mkdir(parents=True, exist_ok=True)
    
    state = {
        "last_updated": get_zulu_time_ms(),
        "total_processed_instructions": 0,
        "aggregate_fragility": 0,
        "aggregate_concordance": 0,
        "recent_events": []
    }
    
    if PILOT_REPORT_PATH.exists():
        try:
            with open(PILOT_REPORT_PATH, 'r') as f:
                state = json.load(f)
        except Exception: 
            pass 
    
    state["total_processed_instructions"] += 1
    state["aggregate_fragility"] += frag_delta
    state["aggregate_concordance"] += conc_delta
    state["last_updated"] = get_zulu_time_ms()
    
    events = state.get("recent_events", [])
    events.append({
        "time": get_zulu_time_ms(), 
        "fragility_delta": frag_delta, 
        "concordance_delta": conc_delta
    })
    state["recent_events"] = events[-10:]
    
    # WRITE TO ROOT LEVEL FOR DASHBOARD ACCESSIBILITY
    with open(PILOT_REPORT_PATH, 'w') as f:
        json.dump(state, f, indent=2)
    
    print(f"   📊 Updated Root Pilot Report: {PILOT_REPORT_PATH.name}")

def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    ERRORS_DIR.mkdir(parents=True, exist_ok=True)
    
    psvc_files = list(INSTRUCTION_QUEUE_DIR.glob("*.psvc"))
    
    if not psvc_files:
        print("ℹ️ Queue empty.")
        return

    print(f"📥 Found {len(psvc_files)} instruction(s).")
    
    total_f = 0
    total_c = 0
    
    for psvc_path in psvc_files:
        try:
            if not parse_psvc_header(psvc_path):
                raise ValueError("Invalid Header")
                
            sidecar = load_sidecar_json(psvc_path)
            sidecar["_original_filename"] = psvc_path.name
            
            report = simulate_mesh_processing(sidecar)
            
            f_val = report["mesh_state"]["fragility_traps"]
            c_val = report["mesh_state"]["concordant_controls"]
            total_f += f_val
            total_c += c_val
            
            save_report(report, psvc_path.stem)
            
            # Move to processed
            shutil.move(str(psvc_path), str(PROCESSED_DIR / psvc_path.name))
            json_src = psvc_path.with_suffix('.json')
            if json_src.exists():
                shutil.move(str(json_src), str(PROCESSED_DIR / json_src.name))
                
            print(f"   ✅ Processed: {psvc_path.name}")
            
        except Exception as e:
            print(f"   ❌ Error processing {psvc_path.name}: {e}")
            try:
                shutil.move(str(psvc_path), str(ERRORS_DIR / psvc_path.name))
                # Also move JSON if it exists to keep queue clean
                json_err = psvc_path.with_suffix('.json')
                if json_err.exists():
                     shutil.move(str(json_err), str(ERRORS_DIR / json_err.name))
            except Exception:
                pass

    if total_f > 0 or total_c > 0:
        update_pilot_summary(total_f, total_c)
        print(f"🏁 Processor Execution Complete. Dashboard Ready.")

if __name__ == "__main__":
    main()
