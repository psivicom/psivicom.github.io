import subprocess
import re
import os
import json
from datetime import datetime
from vector_mesh import VectorMesh

print("=== PSIVI INTELLIGENCE AGENT: READING THE MESH ===")

# 1. READ THE MESH MEMORY
mesh = VectorMesh()
memories = mesh.read_all()
print(f"[INTELLIGENCE] Found {len(memories)} memories in the mesh.")

# 2. FIX THE FOOTER TIMESTAMP (As before)
git_log = subprocess.run(["git", "log", "-1", "--format=%cd", "--date=iso-strict"], capture_output=True, text=True)
actual_time = git_log.stdout.strip()

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

pattern = r'(<p id="footer-last">Last updated: ).*?(</p>)'
html = re.sub(pattern, rf'\1{actual_time}\2', html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

# 3. GENERATE AI AUDIT REPORT (Now including mesh memories)
os.makedirs("reports", exist_ok=True)
audit_path = "reports/ai_audit.md"
with open(audit_path, "w", encoding="utf-8") as f:
    f.write("# AI Intelligence Audit Log\n\n")
    f.write(f"**Audit Time:** {actual_time}\n\n")
    
    f.write("## Mesh Memory Synthesis\n")
    if memories:
        for mem in memories:
            f.write(f"- **{mem.get('agent', 'Unknown')}** ({mem.get('timestamp', 'N/A')}): {mem.get('text', 'No data')}\n")
    else:
        f.write("- *Mesh is currently empty.*\n")
    f.write("\n")
    
    f.write("## Actions Taken\n")
    f.write("- Synchronized `index.html` footer to actual git time.\n")
    f.write("- Read and synthesized all agent memories from the mesh.\n")

print(f"[INTELLIGENCE] Audit report generated at {audit_path}")
