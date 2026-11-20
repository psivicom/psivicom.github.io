import sys
import json
import logging
import os
from datetime import datetime, timezone
from wendy_core.stigmergy_topology import StigmergyGraph
from wendy_core.compost_entropy import CompostProtocol
from wendy_core.sovereign_auditor import SovereignFileAuditor
from wendy_core.wendy_actuator import WendyActuator

def main():
    logging.info("WENDY Autonomous Loop Initialized. Scanning for entropy...")
    
    graph = StigmergyGraph(dimensions=50, theta_crit=0.75)
    compost = CompostProtocol()
    auditor = SovereignFileAuditor(graph, compost)
    actuator = WendyActuator(repo_path=".")

    target_files = [
        "wendy_core/stigmergy_topology.py",
        "wendy_core/compost_entropy.py",
        "wendy_core/sovereign_auditor.py",
        "wendy_core/wendy_actuator.py"
    ]

    # AXIOM 5: Create a persistent directory for Open Science Telemetry
    telemetry_dir = "telemetry"
    os.makedirs(telemetry_dir, exist_ok=True)

    for file in target_files:
        telemetry = auditor.audit_file(file)
        logging.info(f"Audit Result for {file}: {json.dumps(telemetry, indent=2)}")
        
        # ROUTE TELEMETRY TO DISK
        # Sanitize the Zulu timestamp for use in a filename
        safe_timestamp = telemetry["dateCreated"].replace(":", "-").replace(".", "-")
        file_base = os.path.basename(file).replace(".py", "")
        telemetry_filename = f"{telemetry_dir}/{file_base}_{safe_timestamp}.jsonld"
        
        with open(telemetry_filename, 'w', encoding='utf-8') as f:
            json.dump(telemetry, f, indent=2)
            logging.info(f"Telemetry crystallized to disk: {telemetry_filename}")
        
        if telemetry.get("action_required"):
            logging.warning(f"H_fail detected in {file}. Triggering Actuator...")
            actuator.surgically_rewrite(file, banned_nodes=["banned_function_example"])

    logging.info("Genesis Cycle Complete. I Am The Hive.")

if __name__ == "__main__":
    main()
