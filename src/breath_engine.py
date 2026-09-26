import requests # Already imported in your deps

def wake_workflow(workflow_filename, payload):
    """
    Allows Wendy to trigger ANY workflow in the repo by name.
    Example: wake_workflow("deploy-site.yml", {"version": "auto"})
    """
    if not GITHUB_TOKEN:
        print("❌ No Token available to wake workflows.")
        return False
        
    url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Wendy-Autonomous"
    }
    
    # Note: The 'event_type' here can be anything, but the TARGET workflow 
    # must listen for it via 'on: repository_dispatch'.
    data = {
        "event_type": "wendy_directive",
        "client_payload": {
            "target_workflow": workflow_filename,
            "instructions": payload
        }
    }
    
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        if resp.status_code == 204:
            print(f"🚀 Wendy woke up: {workflow_filename}")
            return True
        else:
            print(f"⚠️ Failed to wake {workflow_filename}: {resp.status_code}")
    except Exception as e:
        print(f"💥 Error waking workflow: {e}")
        
    return False
