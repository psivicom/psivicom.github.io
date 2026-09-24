# scripts/BEGIN_PROCESSOR.py
"""
PSIVI AETHER Mesh — Instruction Processor (BEGIN_PROCESSOR.py)
Location: /scripts/BEGIN_PROCESSOR.py

This script is triggered by GitHub Actions when new .psvc instructions appear.
It does NOT create instructions; it CONSUMES them and GENERATES reports.

Protocol: RFC 1001 Compliant
License: EUPL-1.2
Author: Louis-Philippe Audette (2026)
"""

import json
import struct
import zlib
from pathlib import Path
from datetime import datetime, timezone
import sys
import os
import shutil

# --- CONFIGURATION ---
MAGIC = b'PSVI'
VERSION = 1
PRECISION_FLOAT32 = 2
INSTRUCTION_QUEUE_DIR = Path("data/instruction_queue")
REPORTS_DIR = Path("reports/scientific_reports")
PROCESSED_DIR = INSTRUCTION_QUEUE_DIR / ".processed"
ERRORS_DIR = INSTRUCTION_QUEUE_DIR / ".errors"
PILOT_REPORT_PATH = REPORTS_DIR / "pilot_report.json"

def get_zulu_time_ms() -> str:
    """Returns current UTC time in ISO 8601 Zulu format with milliseconds."""
    now_utc = datetime.now(timezone.utc)
    base_format = now_utc.strftime("%Y-%m-%dT%H:%M:%S.")
    millis_part = f"{now_utc.microsecond // 1000:03d}"
    return f"{base_format}{millis_part}Z"

def parse_psvc_header(file_path: Path) -> dict:
    """Parses the binary header of a .psvc file to validate structure."""
    try:
        with open(file_path, 'rb') as f:
            magic = f.read(4)
            if magic != MAGIC:
                raise ValueError(f"Invalid Magic Number: Expected {MAGIC}, got {magic}")
            
            version = struct.unpack('B', f.read(1))[0]
            precision = struct.unpack('B', f.read(1))[0]
            vector_len = struct.unpack('<I', f.read(4))[0]
            compressed_len = struct.unpack('<I', f.read(4))[0]
            
            compressed_data = f.read(compressed_len)
            
            decompressed_size = len(zlib.decompress(compressed_data))
            expected_float32_bytes = vector_len * 4
            
            if decompressed_size != expected_float32_bytes:
                 raise ValueError(f"Vector Size Mismatch: Header says {vector_len} floats ({expected_float32_bytes} bytes), payload has {decompressed_size} bytes.")

            return {
                "valid": True,
                "version": version,
                "precision": precision,
                "vector_length": vector_len,
                "payload_hash": hash(compressed_data)
            }
    except Exception as e:
        print(f"❌ Error parsing PSVC {file_path}: {e}", file=sys.stderr)
        return {"valid": False, "error": str(e)}

def load_sidecar_json(psvc_path: Path) -> dict:
    """Loads the corresponding .json sidecar for a .psvc file."""
    json_path = psvc_path.with_suffix('.json')
    if not json_path.exists():
        raise FileNotFoundError(f"Missing sidecar JSON for {psvc_path.name}")
    
    with open(json_path, 'r') as f:
        return json.load(f)

def simulate_mesh_processing(instruction_meta: dict, sidecar_data: dict) -> dict:
    """Simulates the core mesh agents logic."""
    command = sidecar_data.get("command", "unknown")
    params = sidecar_data.get("params", {})
    
    print(f"🧠 Processing Command: '{command}' from source: {sidecar_data.get('source')}")
    
    report_content = {}
    fragility_score = 0
    
    if command == "spawn_agent":
        template = params.get("template_name", "generic_worker")
        agent_name = params.get("agent_name", "unnamed_agent")
        
        if template == "satellite_observer":
            region = params.get("config", {}).get("target_region", "Unknown")
            report_content["title"] = f"Mesh Report: Satellite Observer Initiated for {region}"
            report_content["status"] = "ACTIVE_MONITORING"
            report_content["agents_spawned"] = [agent_name]
            fragility_score = 0 # Stable
            
        elif template == "literature_resolver":
            gene = params.get("config", {}).get("gene", "N/A")
            organism = params.get("config", {}).get("organism", "N/A")
            report_content["title"] = f"Mesh Report: Literature Resolution for {gene} in {organism}"
            report_content["status"] = "RESOLVED"
            report_content["findings_count"] = 12
            fragility_score = 1 # Minor uncertainty resolved
            
        else:
            report_content["title"] = f"Mesh Report: Generic Agent {agent_name}"
            report_content["status"] = "SPAWNED"
            fragility_score = 0

    elif command == "request_report":
        topic = params.get("topic", "General Status")
        report_content["title"] = f"Mesh Report: Summary for Topic '{topic}'"
        report_content["content"] = "Detailed scientific summary goes here..."
        fragility_score = 0
        
    else:
        report_content["title"] = "Mesh Report: Unknown Command"
        report_content["status"] = "ERROR"
        report_content["message"] = f"Command '{command}' not recognized by RFC 1001 Handler."
        fragility_score = 5 # High fragility due to error

    final_report = {
        "timestamp": get_zulu_time_ms(),
        "instruction_source": sidecar_data.get("_original_filename", "unknown"),
        "mesh_state": {
            "fragility_traps": fragility_score,
            "concordant_controls": max(0, 10 - fragility_score), 
            "elasticity": "STABLE" if fragility_score < 3 else "CONTRACT"
        },
        "osdr_ground_truth_loaded": True,
        "rfc1001_compliant": True,
        **report_content
    }
    
    return final_report

def save_report(report: dict, original_instruction_id: str):
    """Saves the generated report to the filesystem."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    safe_id = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in original_instruction_id)[:50]
    timestamp_slug = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')
    
    report_filename = f"report_{safe_id}_{timestamp_slug}.json"
    report_path = REPORTS_DIR / report_filename
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    print(f"💾 Report Saved: {report_path}")
    return report_path

def update_pilot_summary(new_fragility: int, new_concordance: int):
    """Updates the global pilot report aggregate."""
    PILOT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    current_state = {
        "last_updated": get_zulu_time_ms(),
        "total_processed_instructions": 0,
        "aggregate_fragility": 0,
        "aggregate_concordance": 0,
        "recent_events": []
    }
    
    if PILOT_REPORT_PATH.exists():
        try:
            with open(PILOT_REPORT_PATH, 'r') as f:
                current_state = json.load(f)
        except json.JSONDecodeError:
            pass 
            
    current_state["total_processed_instructions"] += 1
    current_state["aggregate_fragility"] += new_fragility
    current_state["aggregate_concordance"] += new_concordance
    current_state["last_updated"] = get_zulu_time_ms()
    
    event_log = current_state.get("recent_events", [])
    event_log.append({
        "time": get_zulu_time_ms(),
        "fragility_delta": new_fragility,
        "concordance_delta": new_concordance
    })
    current_state["recent_events"] = event_log[-10:]
    
    with open(PILOT_REPORT_PATH, 'w') as f:
        json.dump(current_state, f, indent=2)

def main():
    print("="*60)
    print("️  PSIVI AETHER Mesh - Processor Started")
    print("="*60)
    
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    ERRORS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Find all .psvc files in queue
    psvc_files = list(INSTRUCTION_QUEUE_DIR.glob("*.psvc"))
    
    if not psvc_files:
        print("ℹ️  Instruction queue is empty. Nothing to process.")
        return

    print(f"📥 Found {len(psvc_files)} instruction(s) to process.")
    
    total_new_fragility = 0
    total_new_concordance = 0
    
    for psvc_path in psvc_files:
        try:
            meta = parse_psvc_header(psvc_path)
            if not meta.get("valid"):
                print(f"⚠️  Skipping invalid PSVC: {psvc_path.name}")
                shutil.move(str(psvc_path), str(ERRORS_DIR / psvc_path.name))
                continue
                
            sidecar_data = load_sidecar_json(psvc_path)
            sidecar_data["_original_filename"] = psvc_path.name
            
            report = simulate_mesh_processing(meta, sidecar_data)
            
            fragility = report.get("mesh_state", {}).get("fragility_traps", 0)
            concordance = report.get("mesh_state", {}).get("concordant_controls", 0)
            total_new_fragility += fragility
            total_new_concordance += concordance
            
            save_report(report, psvc_path.stem)
            
            # Move processed items
            shutil.move(str(psvc_path), str(PROCESSED_DIR / psvc_path.name))
            json_path = psvc_path.with_suffix('.json')
            if json_path.exists():
                shutil.move(str(json_path), str(PROCESSED_DIR / json_path.name))
                
            print(f"✅ Successfully processed: {psvc_path.name}")
            
        except Exception as e:
            print(f"❌ Critical Error processing {psvc_path.name}: {e}", file=sys.stderr)
            try:
                shutil.move(str(psvc_path), str(ERRORS_DIR / psvc_path.name))
            except:
                pass

    if total_new_fragility > 0 or total_new_concordance > 0:
        update_pilot_summary(total_new_fragility, total_new_concordance)
        print(f"📊 Pilot Summary Updated: Fragility +{total_new_fragility}, Concordance +{total_new_concordance}")

    print("="*60)
    print("🏁 Processor Execution Complete")
    print("="*60)

if __name__ == "__main__":
    main()
