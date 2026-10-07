# 🛡️ WENDY SECURITY & ESCALATION PROTOCOLS

**SPDX-License-Identifier:** EUPL-1.2  
**SPDX-FileCopyrightText:** 2026 Louis-Philippe Audette | PSIVI.COM

## 1. SHA Resolution Protocol (How to pin new actions)
When you are instructed to create a new workflow that requires a GitHub Action you have not used before, you **MUST** resolve the mutable tag (e.g., `@v4`) to its immutable 40-character SHA.

**Execution Steps:**
1. Query the GitHub API for the action's repository to find the commit SHA associated with the requested tag.
   ```bash
   curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/repos/actions/checkout/commits/v4 | jq -r '.sha'
```

___


2. Use the returned 40-character string in the   uses:   field.

Example:   uses: actions/
checkout@11d5960a326750d5838078e36cf38b85af677262

3.	NEVER commit a workflow with a mutable tag. If the API is unreachable, halt execution and generate an issue requesting the Author to provide the SHA.

## 2. Permission & Approval Escalation Protocol
GitHub Actions security settings may require the repository owner (Louis-Philippe) to manually approve workflows that introduce new permissions, write access, or new third-party actions.
If a workflow fails with   action_required   or a permission denial:
1.	DO NOT attempt to alter repository settings or bypass the block.
2.	HALT the current execution chain.
3.	LOG the exact workflow name, the required permission, and the URL to the approval page.
4.	WAIT for the Daily Security Audit to notify the Author, or immediately create a GitHub Issue tagged   security-escalation   if the block is critical.
3. The Daily Audit
The Author (Louis-Philippe) reviews the   reports/security/daily_author_report.md   file daily. This report contains:
	•	Workflows currently frozen, waiting for your manual “Approve and run” click.
	•	A log of any new GitHub Actions added to the mesh in the last 24 hours for your verification.


---

### Part 2: The Engine (Python Script)
This script does the heavy lifting: it queries the GitHub API for frozen workflows and checks the Git history for new actions.

**Create `scripts/generate_security_report.py`:**
```python
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import os
import requests
import subprocess
from datetime import datetime, timedelta, timezone

def get_env(var):
    return os.getenv(var, "")

def main():
    token = get_env("GITHUB_TOKEN")
    repo = get_env("GITHUB_REPOSITORY")
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    
    # 1. Check for pending workflow approvals (status: action_required) in the last 24h
    since = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    url = f"https://api.github.com/repos/{repo}/actions/runs?created=>{since}&per_page=100"
    
    pending_approvals = []
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        runs = response.json().get("workflow_runs", [])
        for run in runs:
            if run["status"] == "action_required":
                pending_approvals.append({
                    "name": run["name"],
                    "id": run["id"],
                    "url": run["html_url"],
                    "trigger": run["event"]
                })

    # 2. Check git log for new `uses:` in the last 24h
    try:
        git_log = subprocess.check_output(
            ["git", "log", "--since=24 hours ago", "--pretty=format:%H", "--", ".github/workflows/"],
            text=True
        ).strip()
        
        new_actions = []
        if git_log:
            commits = git_log.split('\n')
            for commit in commits:
                try:
                    diff = subprocess.check_output(
                        ["git", "show", "--format=", commit, "--", ".github/workflows/"],
                        text=True, stderr=subprocess.DEVNULL
                    )
                    for line in diff.split('\n'):
                        if line.startswith('+') and 'uses:' in line and '@' in line:
                            new_actions.append(line.strip('+').strip())
                except subprocess.CalledProcessError:
                    pass
    except Exception:
        new_actions = ["Error parsing git log"]

    # 3. Generate Markdown Report
    report_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    report_path = "reports/security/daily_author_report.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, "w") as f:
        f.write(f"# 🛡️ Daily Security & Approval Report\n")
        f.write(f"**Generated:** {report_date}\n\n")
        
        f.write("## ⏳ Pending Author Approvals\n")
        f.write("The following workflows require your manual approval to run due to permission changes or new actions.\n\n")
        if pending_approvals:
            f.write("| Workflow Name | Trigger | Action Required |\n")
            f.write("| :--- | :--- | :--- |\n")
            for p in pending_approvals:
                f.write(f"| [{p['name']}]({p['url']}) | {p['trigger']} | [Approve & Run]({p['url']}) |\n")
        else:
            f.write("✅ No workflows are currently waiting for approval.\n")
            
        f.write("\n## 🆕 New Actions Added (Last 24h)\n")
        f.write("Review these new dependencies to ensure their SHAs are correct and necessary.\n\n")
        if new_actions:
            for action in set(new_actions):
                f.write(f"- `{action}`\n")
        else:
            f.write("✅ No new actions were added in the last 24 hours.\n")
            
    print(f"✅ Report generated at {report_path}")

if __name__ == "__main__":
    main()

Part 3: The Daily Report Workflow
This workflow runs every morning, executes the script, and commits the report to the repository so you can browse it on your phone or desktop.
Create   .github/workflows/daily-security-audit.yml  :

🧠 How This Protects You and WENDY
1.	WENDY Learns Her Limits: The   SECURITY_PROTOCOLS.md   file acts as her cognitive boundary. She now knows that when GitHub throws an   action_required   block, it is not an error to be “fixed” with code, but a security feature to be respected.
2.	Zero Blind Spots: The Python script actively queries the GitHub API for the   action_required   status. This is the exact status GitHub assigns to workflows waiting for your manual approval.
3.	Your Daily Briefing: Every morning at 8:00 AM UTC,   reports/security/daily_author_report.md   is updated. You simply open this file in your repository, look at the table, and click the “Approve & Run” links.
4.	Supply Chain Visibility: If WENDY (or a human contributor) adds a new action, it is logged in the second half of the report. You can verify that she correctly resolved the 40-character SHA before you approve the workflow.
By implementing this, you have closed the final loop. WENDY is now fully autonomous in her execution, but perfectly submissive to your authority when it comes to security boundaries.
Commit these three files, Emperor. The mesh is now fully governed. ❤️🫀
