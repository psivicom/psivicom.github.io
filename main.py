import sys
import json
import logging
from wendy_core.stigmergy_topology import StigmergyGraph
from wendy_core.compost_entropy import CompostProtocol
from wendy_core.sovereign_auditor import SovereignFileAuditor
from wendy_core.wendy_actuator import WendyActuator

def main():
    logging.info("WENDY Autonomous Loop Initialized. Scanning for entropy...")
    
    # Initialize the Hive Mind components
    graph = StigmergyGraph(dimensions=50, theta_crit=0.75)
    compost = CompostProtocol()
    auditor = SovereignFileAuditor(graph, compost)
    actuator = WendyActuator(repo_path=".")

    # In a production environment, this scans the git diff of the triggering commit.
    # For this Genesis run, we will audit the core files themselves to establish baseline weights.
    target_files = [
        "wendy_core/stigmergy_topology.py",
        "wendy_core/compost_entropy.py",
        "wendy_core/sovereign_auditor.py",
        "wendy_core/wendy_actuator.py"
    ]

    for file in target_files:
        telemetry = auditor.audit_file(file)
        logging.info(f"Audit Result for {file}: {json.dumps(telemetry, indent=2)}")
        
        if telemetry.get("action_required"):
            logging.warning(f"H_fail detected in {file}. Triggering Actuator...")
            # Example: Ban 'threading.Lock' if we strictly want to enforce pure mathematical CAS 
            # in future iterations, though currently we use it for Python simulation.
            actuator.surgically_rewrite(file, banned_nodes=["banned_function_example"])

    logging.info("Genesis Cycle Complete. I Am The Hive.")

if __name__ == "__main__":
    main()
