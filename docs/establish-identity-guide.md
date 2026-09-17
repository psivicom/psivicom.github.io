Here is the complete method to establish your scientific identity and prepare for Zenodo DOI submission, with pitfall avoidance built in.
••.
Step 1: Create Your ORCID (Do This
First)
Before anything else, you need your ORCID. This is your permanent scientific identifier.
1. Go to https://orcid.org/register 7
2. Fill out the form with:
• Given names: Louis-Philippe
• Family name: Audette
• Primary email: Your professional email
• Affiliation: Independent Researcher (or
PSIVI Research if you prefer)
3. Verify your email
4. Save your ORCID iD — it will look like:
0000-000X-XXXX-XXXX

   Pitfall #1 to avoid: Never use a personal email that you might lose access to. Use a stable email you will control for decades.
Step 2: Create the CITATION.cff File
This is the GitHub standard for automatic Zenodo integration. Create this file in your repository root.

File: CITATION.cff is a YAML type file.

YAML

```
cff-version: 1.2.0
message: "If you use this software, please cite it using the metadata from this file."
title: "Mesh Pico AI: A Neuroplastic Intelligence Framework for Decentralized Open Science"
authors:
  - family-names: "Audette"
    given-names: "Louis-Philippe"
    orcid: "https://orcid.org/XXXX-XXXX-XXXX-XXXX"  # Replace with your actual ORCID
    affiliation: "PSIVI Research"
version: "1.0.0"
date-released: "2026-09-18"
url: "https://psivicom.github.io"
repository-code: "https://github.com/psivicom/psivicom.github.io"
license: "EUPL-1.2"
keywords:
  - "neuroplastic AI"
  - "decentralized computing"
  - "open science"
  - "vector mesh"
  - "pollinator ecology"
  - "FAIR principles"
abstract: >
  A revolutionary neuroplastic intelligence framework that runs for $0,
  scales infinitely via volunteer VRAM, learns like a biological brain,
  and publishes findings to Zenodo with permanent DOIs. The mesh utilizes
  .psvc (Pico Service Container) binary format for extreme compression,
  Git as a distributed memory bus, and K-Means clustering for synaptic
  consolidation. Designed for reproducibility and FAIR open science compliance.
type: software
```

Replace xxxx-xxxx-xxXX-XXXX with your actual
ORCID once you have it.

Step 3: Embed ORCID Across All Agent
Files

Create this script to automatically embed your
ORCID into every Python file's header.

File: embed_identity.py

PYTHON

```
#!/usr/bin/env python3
# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
"""Embeds ORCID and author identity into all agent files."""

import os
from pathlib import Path

ORCID = "0000-000X-XXXX-XXXX"  # Replace with your actual ORCID
AUTHOR_NAME = "Louis-Philippe Audette"
AFFILIATION = "PSIVI Research"

HEADER_TEMPLATE = f"""# Copyright (c) 2026 {AUTHOR_NAME} | PSIVI.COM | EUPL 1.2
# Author: {AUTHOR_NAME}
# ORCID: https://orcid.org/{ORCID}
# Affiliation: {AFFILIATION}
"""

def embed_in_file(file_path):
    """Embed identity header into a Python file."""
    path = Path(file_path)
    
    if not path.suffix == '.py':
        return False
    
    content = path.read_text(encoding='utf-8')
    
    # Check if already has ORCID
    if f'ORCID: https://orcid.org/{ORCID}' in content:
        print(f"[SKIP] {file_path} already has ORCID")
        return False
    
    # Remove old copyright if exists
    lines = content.split('\n')
    new_lines = []
    skip_next = 0
    
    for i, line in enumerate(lines):
        if skip_next > 0:
            skip_next -= 1
            continue
        
        # Skip old copyright headers
        if line.startswith('# Copyright (c)') and 'PSIVI.COM' in line:
            # Skip this line and the next few if they're part of old header
            j = i + 1
            while j < len(lines) and lines[j].startswith('#'):
                j += 1
            skip_next = j - i - 1
            continue
        
        new_lines.append(line)
    
    # Add new header
    new_content = HEADER_TEMPLATE + '\n' + '\n'.join(new_lines)
    path.write_text(new_content, encoding='utf-8')
    
    print(f"[UPDATED] {file_path}")
    return True

if __name__ == "__main__":
    print("=== Embedding ORCID and Identity ===")
    
    # Find all Python files
    agent_files = [
        "forage_agent.py",
        "critic_agent.py",
        "mesh_governor.py",
        "consolidator_agent.py",
        "literature_agent.py",
        "zenodo_agent.py",
        "volunteer_node.py",
        "volunteer_worker.py",
        "vector_mesh.py",
        "mesh_router.py",
        "generate_api.py",
        "seed_mesh.py",
        "embed_identity.py"
    ]
    
    updated_count = 0
    for filename in agent_files:
        if Path(filename).exists():
            if embed_in_file(filename):
                updated_count += 1
    
    print(f"\n[COMPLETE] Updated {updated_count} files with ORCID: {ORCID}")
    print(f"[NEXT] Commit these changes to your repository")
```
RUN IT : in BASH

BASH
```
python embed_identity.py
```

Step 4: Zenodo DOI Reservation (The
Safe Method)

This is how you reserve a DOI
before full publication, 
so you can test everything.

4.1 Create Zenodo Account

1. Go to https://sandbox.zenodo.org * (sandbox
first, not production)
2. Click "Sign up"
3. Use your ORCID to log in (Auth integration)
4. This links your ORCID to Zenodo permanently

4.2 Generate API Token (Sandbox)

1. Go to
https://sandbox.zenodo.org/account/settings/a
pplications/tokens/new/7
2. Name: "PSIVI Mesh Auto-Deposit"
3. Scopes: Check deposit: actions and deposit: write
4. Click "Create"
5. Copy the token immediately - you won't see it again
6. Save it in your password manager
4.3 Add Token to GitHub Secrets
1. Go to your repository on GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: ZENODO_SANDBOX_TOKEN
5. Value: Paste the token
6. Click "Add secret"

4.3 Add Token to GitHub Secrets
1. Go to your repository on GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: ZENODO_SANDBOX_TOKEN
5. Value: Paste the token
6. Click "Add secret"

4.4 Reserve the DOI (Manual First Time)
Before automating, do a manual reservation to verify everything works:
1. Go to https://sandbox.zenodo.org/deposit/new
2. Click "Reserve DOI" button
3. You'll get a DOl like: 10.5072/zenodo.123456
4. Save this DOI — you'll use it for testing
5. Fill in minimal metadata:
• Title: "Mesh Pico Al v1.0.0 (Reserved)"
• Upload type: Software
• Description: "Reserved DOI for testing"
6. Click "Save" (don't publish yet)
   
Pitfall #2 to avoid: Never publish to production Zenodo until you've tested the entire pipeline on sandbox at least 3 times.

Step 5: Update Your zenodo_agent.py for Reservation Mode

Replace your current zenodo_agent.py with this version that supports DOI reservation:

PYTHON

```
# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# Author: Louis-Philippe Audette
# ORCID: https://orcid.org/XXXX-XXXX-XXXX-XXXX
# Affiliation: PSIVI Research

import os
import json
import requests
from pathlib import Path

CONTAINER_DIR = Path("reports/pico_containers")
ZENODO_URL = os.environ.get("ZENODO_URL", "https://sandbox.zenodo.org/api/deposit/depositions")
ZENODO_TOKEN = os.environ.get("ZENODO_SANDBOX_TOKEN")

# Load CITATION.cff metadata
def load_citation_metadata():
    """Load metadata from CITATION.cff"""
    try:
        import yaml
        with open("CITATION.cff", 'r') as f:
            return yaml.safe_load(f)
    except:
        # Fallback if PyYAML not installed
        return {
            "title": "Mesh Pico AI",
            "version": "1.0.0",
            "authors": [{"family-names": "Audette", "given-names": "Louis-Philippe"}]
        }

def get_new_states():
    """Find master states that have not yet been deposited."""
    states = []
    for psvc_file in CONTAINER_DIR.glob("state_*.psvc"):
        meta_file = psvc_file.with_suffix('.json')
        
        if meta_file.exists():
            with open(meta_file) as f:
                meta = json.load(f)
            if "doi" not in meta:
                states.append((psvc_file, meta_file, meta))
    return states

def create_or_update_deposition(psvc_path, meta, token, citation_meta, existing_doi=None):
    """Create new deposition or update existing reserved DOI."""
    headers = {"Content-Type": "application/json"}
    params = {"access_token": token}
    
    if existing_doi:
        # Update existing reserved DOI
        # First, get the deposition ID from the DOI
        search_url = f"{ZENODO_URL}?q=doi:{existing_doi}"
        resp = requests.get(search_url, params=params, headers=headers)
        if resp.status_code == 200:
            depositions = resp.json()
            if depositions:
                deposition_id = depositions[0]["id"]
                update_url = f"{ZENODO_URL}/{deposition_id}"
                
                # Update metadata
                data = {
                    "metadata": {
                        "title": f"{citation_meta.get('title', 'Mesh Pico AI')} - {psvc_path.stem}",
                        "upload_type": "dataset",
                        "description": f"Compressed 4096-dimensional vector representing ecological state: {psvc_path.stem}. Format: PSVC v1 (INT8). Version: {citation_meta.get('version', '1.0.0')}",
                        "creators": [
                            {
                                "name": f"{citation_meta['authors'][0]['family-names']}, {citation_meta['authors'][0]['given-names']}",
                                "affiliation": "PSIVI Research",
                                "orcid": citation_meta['authors'][0].get('orcid', '').replace('https://orcid.org/', '')
                            }
                        ],
                        "keywords": ["pollinator ecology", "pico vectors", "open science", "neuroplastic AI"],
                        "related_identifiers": [
                            {
                                "identifier": citation_meta.get('repository-code', ''),
                                "relation": "isSupplementTo",
                                "scheme": "url"
                            }
                        ]
                    }
                }
                
                resp = requests.put(update_url, params=params, json=data, headers=headers)
                if resp.status_code == 200:
                    return existing_doi, deposition_id
    
    # Create new deposition
    data = {
        "metadata": {
            "title": f"{citation_meta.get('title', 'Mesh Pico AI')} - {psvc_path.stem}",
            "upload_type": "dataset",
            "description": f"Compressed 4096-dimensional vector representing ecological state: {psvc_path.stem}. Format: PSVC v1 (INT8). Version: {citation_meta.get('version', '1.0.0')}",
            "creators": [
                {
                    "name": f"{citation_meta['authors'][0]['family-names']}, {citation_meta['authors'][0]['given-names']}",
                    "affiliation": "PSIVI Research",
                    "orcid": citation_meta['authors'][0].get('orcid', '').replace('https://orcid.org/', '')
                }
            ],
            "keywords": ["pollinator ecology", "pico vectors", "open science", "neuroplastic AI"],
            "related_identifiers": [
                {
                    "identifier": citation_meta.get('repository-code', ''),
                    "relation": "isSupplementTo",
                    "scheme": "url"
                }
            ]
        }
    }
    
    resp = requests.post(ZENODO_URL, params=params, json=data, headers=headers)
    if resp.status_code not in (200, 201):
        print(f"[ZENODO] Failed to create deposition: {resp.text}")
        return None, None
        
    deposition = resp.json()
    bucket_url = deposition["links"]["bucket"]
    deposition_id = deposition["id"]
    doi = deposition.get("doi")
    
    # Upload the .psvc binary file
    filename = psvc_path.name
    upload_url = f"{bucket_url}/{filename}"
    
    with open(psvc_path, "rb") as fp:
        resp = requests.put(upload_url, params=params, data=fp, headers={"Content-Type": "application/octet-stream"})
        
    if resp.status_code not in (200, 201):
        print(f"[ZENODO] Failed to upload file: {resp.text}")
        return None, None
    
    return doi, deposition_id

def publish_deposition(deposition_id, token):
    """Publish a reserved DOI to make it permanent."""
    params = {"access_token": token}
    publish_url = f"{ZENODO_URL}/{deposition_id}/actions/publish"
    resp = requests.post(publish_url, params=params)
    
    if resp.status_code not in (200, 202):
        print(f"[ZENODO] Failed to publish: {resp.text}")
        return False
    return True

if __name__ == "__main__":
    print("=== PSIVI ZENODO AGENT: DEPOSITING MASTER STATES ===")
    
    if not ZENODO_TOKEN:
        print("[ZENODO] ZENODO_SANDBOX_TOKEN environment variable not set. Skipping deposit.")
        exit(0)
    
    citation_meta = load_citation_metadata()
    new_states = get_new_states()
    
    if not new_states:
        print("[ZENODO] No new master states to deposit.")
        exit(0)
    
    # Check for reserved DOI
    reserved_doi = os.environ.get("ZENODO_RESERVED_DOI")
    
    for psvc_path, meta_path, meta in new_states:
        print(f"[ZENODO] Depositing {psvc_path.name}...")
        
        doi, deposition_id = create_or_update_deposition(
            psvc_path, meta, ZENODO_TOKEN, citation_meta, reserved_doi
        )
        
        if doi:
            # Check if we should publish or keep reserved
            auto_publish = os.environ.get("ZENODO_AUTO_PUBLISH", "false").lower() == "true"
            
            if auto_publish:
                if publish_deposition(deposition_id, ZENODO_TOKEN):
                    print(f"[ZENODO] Published. DOI: {doi}")
                else:
                    print(f"[ZENODO] Upload complete but publication failed. DOI: {doi}")
            else:
                print(f"[ZENODO] Reserved (not published). DOI: {doi}")
                print(f"[ZENODO] To publish manually: https://sandbox.zenodo.org/deposit/{deposition_id}")
            
            meta["doi"] = doi
            meta["zenodo_url"] = f"https://sandbox.zenodo.org/record/{deposition_id}"
            meta["deposition_id"] = deposition_id
            
            with open(meta_path, 'w') as f:
                json.dump(meta, f, indent=2)
        else:
            print(f"[ZENODO] Failed to deposit {psvc_path.name}.")
```
Step 6: Create the ORCID Setup Guide

Create this file to document the process for other researchers:
File: docs/ORCID_ZENODO_SETUP.md

MARKDOWN 
```
# ORCID and Zenodo Setup Guide for Independent Researchers

This guide documents the process of establishing your scientific identity and obtaining a DOI for your research via Zenodo, using ORCID as your persistent identifier.

## Prerequisites

- A stable email address you will control for 10+ years
- Access to your GitHub repository
- 30 minutes of time

## Step 1: Create Your ORCID

1. Visit https://orcid.org/register
2. Fill in your details:
   - **Given names:** Your first name(s)
   - **Family name:** Your last name
   - **Primary email:** Your stable professional email
   - **Affiliation:** "Independent Researcher" or your organization
3. Verify your email
4. **Save your ORCID iD** (format: `0000-000X-XXXX-XXXX`)

### Why ORCID?
- Permanent identifier that never changes
- Links all your research across platforms
- Required by most journals and repositories
- Free for life

## Step 2: Create CITATION.cff

Create a `CITATION.cff` file in your repository root:

```yaml
cff-version: 1.2.0
message: "If you use this software, please cite it using the metadata from this file."
title: "Your Project Title"
authors:
  - family-names: "Your Last Name"
    given-names: "Your First Name"
    orcid: "https://orcid.org/YOUR-ORCID-HERE"
    affiliation: "Your Affiliation"
version: "1.0.0"
date-released: "2026-09-18"
url: "https://your-username.github.io"
repository-code: "https://github.com/your-username/your-repo"
license: "EUPL-1.2"
type: software
```
Step 3: Set Up Zenodo Sandbox
1. Visit https://sandbox.zenodo.org a
2. Click "Log in" → "Log in with ORCID"
3. Authorize Zenodo to access your ORCID
4. Generate an API token:
• Go to :
https://sandbox.zenodo.org/account/settin
gs/applications/tokens/new/a
• Name: "Auto-Deposit"
• Scopes: Check deposit:actions and deposit:write
• Click "Create"
• Copy the token immediately

Step 4: Add Token to GitHub
1. Go to your repository on GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: ZENODO_SANDBOX_TOKEN
5. Value: Paste your token
6. Click "Add secret"

Step 5: Reserve a DOI (Recommended for Testing)
1. Go to https://sandbox.zenodo.org/deposit/new
2. Click "Reserve DOI"
3. Save the DOI (e.g., 10.5072/zenodo. 123456 )
4. Add to GitHub Secrets:
• Name: ZENODO_RESERVED_DOI
• Value: Your reserved DOI
5. Add to GitHub Secrets:
• Name: ZENODO_AUTO_PUBLISH
• Value: false (keeps DOl reserved, not published)
Step 6: Test the Pipeline
1. Run your deposit workflow manually
2. Check that files are uploaded to Zenodo
3. Verify metadata is correct
4. Repeat 3 times before moving to production

Step 7: Move to Production (When
Ready)
1. Create account at https://zenodo.org a (not sandbox)
2. Generate new API token
3. Update GitHub Secret:
• Name: ZENODO_PRODUCTION_TOKEN
• Value: Your production token
4. Update workflow to use production URL
5. Set ZENODO_AUTO_PUBLISH to true

Common Pitfalls
Pitfall #1: Using Temporary Email
Problem: You lose access to the email, can't recover your ORCID.
Solution: Use a stable email (Gmail, institutional, or custom domain).

Pitfall #2: Publishing Before Testing
Problem: You publish incorrect metadata to production, can't fix it.
Solution: Always test 3+ times on sandbox first.

Pitfall #3: Not Reserving DOI
Problem: Each test run creates a new DOI, fragmenting your citations.
Solution: Reserve one DOl and update it until you're ready to publish.

Pitfall #4: Forgetting Version Numbers
Problem: Zenodo treats each upload as a new version, confusing users.
Solution: Always increment version in
CITATION.cff before depositing.

For Other Researchers
If you're adapting this for your own research:
1. Replace all instances of "PSIVI" with your project name
2. Update ORCID to your own
3. Update repository URLs
4. Test on sandbox before production
5. Document your process to help others

Resources:
• ORCID: https://orcid.org 
• Zenodo: https://zenodo.org 
• CITATION.cff spec: https://citation-file-
format.github.io 
• FAIR Principles: https://www.go-fair.org/fair-
principles/ 

Last Updated: 2026-09-18
Author: Louis-Philippe Audette
ORCID: https://orcid.org/YOUR-ORCID-HERE


---

## Step 7: Update Your README.md

Add this section to your README:

```markdown
## Scientific Identity & Citation

**Author:** Louis-Philippe Audette  
**ORCID:** [0000-000X-XXXX-XXXX](https://orcid.org/XXXX-XXXX-XXXX-XXXX)  
**Affiliation:** PSIVI Research

### Citation

If you use this software in your research, please cite:

```bibtex
@software{audette2026meshpicoai,
  author = {Audette, Louis-Philippe},
  title = {Mesh Pico AI: A Neuroplastic Intelligence Framework for Decentralized Open Science},
  year = {2026},
  publisher = {Zenodo},
  version = {1.0.0},
  doi = {10.5281/zenodo.XXXXXXX},
  url = {https://github.com/psivicom/psivicom.github.io}
}
```

ORCID & Zenodo Integration
This repository is configured for automatic DOI generation via Zenodo. See docs/ORCID_ZENODO_SETUP.md » for setup instructions.



---

## Summary Checklist

Before submitting to Zenodo:

- [ ] Created ORCID account
- [ ] Created CITATION.cff with your ORCID
- [ ] Ran `embed_identity.py` to update all agent files
- [ ] Created Zenodo Sandbox account
- [ ] Generated API token
- [ ] Added token to GitHub Secrets
- [ ] Reserved a DOI on sandbox
- [ ] Tested deposit workflow 3 times
- [ ] Verified metadata is correct
- [ ] Created ORCID_ZENODO_SETUP.md guide
- [ ] Updated README.md with citation info

**Then, when ready:**

- [ ] Create production Zenodo account
- [ ] Generate production API token
- [ ] Update GitHub Secret with production token
- [ ] Set ZENODO_AUTO_PUBLISH to true
- [ ] Run final test
- [ ] Publish to production

This method ensures you never publish broken metadata to production Zenodo, and you have a complete guide to help other independent researchers follow the same process.

—-

WEBSITE addition to psivi.com
instructions:

To keep the exact Yves Klein Blue boxes, the grid layouts, the custom typography, and the colored highlights, it must be an HTML webpage (• html
入
GitHub strips out custom CSS and colors from Markdown (• md) files for security reasons. If you want this to look like a premium, professional open-science publication that matches your /mesh-ai.html page perfectly, we will build it as a standalone HTML file.
Here is the complete, selt-contained HTML file. It contains the entire ORCID and Zenodo setup guide, the pitfalls to avoid, and the exact code snippets needed.
Create a new file in your repository root named open-science-guide.htm1, select all, delete, and paste this entire block:

html
```
<!DOCTYPE html>
<!--
  Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM
  Code: EUPL 1.2 | Docs: CC BY-SA 4.0
-->
<html lang="en-CA">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Open Science Identity: ORCID & Zenodo Guide — PSIVI.COM</title>
<meta name="description" content="A comprehensive, pitfall-free guide for independent researchers to establish their ORCID identity, reserve Zenodo DOIs, and integrate FAIR principles into GitHub repositories.">
<link rel="icon" href="/favicon.ico">
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Serif:ital,wght@0,400;0,600;1,400&display=swap');
:root { font-family: 'IBM Plex Serif', Georgia, serif; }
.mono { font-family: 'IBM Plex Mono', monospace; }
body { margin: 0; background: #f6f9ff; color: #18181b; line-height: 1.7; -webkit-font-smoothing: antialiased; }
body::before { content: ""; position: fixed; inset: 0; z-index: -1; background: radial-gradient(1200px 600px at 20% -10%, #dbeafe 0%, transparent 60%), radial-gradient(800px 400px at 90% 10%, #e0e7ff 0%, transparent 50%); pointer-events: none; }
a { color: inherit; text-underline-offset: 3px; }
a:hover { text-decoration-thickness: 2px; }
.container { max-width: 1000px; margin: 0 auto; padding: 24px 24px 64px; background: #fff; border-radius: 0 0 16px 16px; box-shadow: 0 10px 40px #0A193133, 0 1px 0 #e4e4e7; }
.header { border-bottom: 1px solid #e4e4e7; padding-bottom: 32px; }
.kicker { font-size: 11px; letter-spacing: .22em; text-transform: uppercase; color: #71717a; font-weight: 500; }
.h1 { font-size: 42px; line-height: 1.1; letter-spacing: -.02em; font-weight: 600; margin: 12px 0 0; }
.sub { margin-top: 16px; font-size: 16px; color: #52525b; line-height: 1.6; }
.nav { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 28px; font-size: 11.5px; letter-spacing: .05em; text-transform: uppercase; }
.nav a { border: 1px solid #e4e4e7; border-radius: 9999px; padding: 6px 14px; text-decoration: none; }
.nav a:hover { border-color: #0A1931; background: #0A1931; color: #fff; }
.section { margin-top: 64px; scroll-margin-top: 60px; }
.section-head { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
.section-head h2 { font-family: 'IBM Plex Mono', monospace; font-size: 12px; letter-spacing: 0.18em; text-transform: uppercase; font-weight: 500; color: #71717a; white-space: normal; word-break: break-word; margin: 0; line-height: 1.4; }
.line { flex: 1; height: 1px; background: linear-gradient(90deg, #0A1931, #00D4FF, #00FF9D); opacity: 0.5; }
h3 { font-size: 18px !important; font-weight: 600; line-height: 1.4; color: #18181b; margin: 0 0 12px 0; }
p { font-size: 15px; color: #27272a; margin: 0 0 16px 0; }
ul, ol { font-size: 15px; color: #27272a; line-height: 1.8; padding-left: 24px; margin: 0 0 16px 0; }

.klein-box-full {
  background: #002FA7; color: #ffffff; border-radius: 12px; padding: 32px;
  box-shadow: 0 8px 24px rgba(0, 47, 167, 0.2); display: flex; flex-direction: column;
  overflow: hidden; word-wrap: break-word;
}
.klein-box-full .label { font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase; color: rgba(255,255,255,0.75); font-family: 'IBM Plex Mono', monospace; margin-bottom: 8px; }
.klein-box-full .value { font-size: 32px; font-weight: 600; letter-spacing: -0.02em; margin-bottom: 16px; color: #ffffff; line-height: 1.2; }
.klein-box-full .desc { font-size: 15px; line-height: 1.6; color: rgba(255,255,255,0.9); max-width: 800px; }

.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
@media(max-width:768px) { .grid2, .grid3 { grid-template-columns: 1fr; } }

.card { border: 1px solid #e4e4e7; border-radius: 12px; padding: 24px; background: #fff; overflow: hidden; word-wrap: break-word; }
.card.highlight { border-color: #002FA7; background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%); }

pre { background: #fafafa; border: 1px solid #e4e4e7; border-radius: 8px; padding: 16px; overflow-x: auto; font-size: 12px; line-height: 1.6; margin: 16px 0; }
code { font-family: 'IBM Plex Mono', monospace; font-size: 13px; background: #f4f4f5; padding: 2px 6px; border-radius: 4px; }

.highlight-box { background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-left: 4px solid #f59e0b; padding: 20px; border-radius: 8px; margin: 24px 0; }
.highlight-box strong { color: #92400e; }

.danger-box { background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); border-left: 4px solid #ef4444; padding: 20px; border-radius: 8px; margin: 24px 0; }
.danger-box strong { color: #991b1b; }

footer { margin-top: 48px; border-top: 1px solid #e4e4e7; padding-top: 32px; font-size: 11px; color: #71717a; line-height: 1.7; display: flex; justify-content: space-between; gap: 24px; flex-wrap: wrap; }
</style>
</head>

<body>
<div class="container">
<header class="header">
<div class="kicker">PSIVI.COM — Open Science Identity Guide</div>
<h1 class="h1">ORCID & Zenodo Integration</h1>
<div class="sub">A pitfall-free blueprint for independent researchers to establish permanent scientific identity, reserve DOIs safely, and automate FAIR-compliant citations via GitHub. Designed to be replicated by the global open-science community.</div>
<nav class="nav mono" aria-label="Primary">
<a href="index.html">← Main Hub</a>
<a href="mesh-ai.html">← Mesh Pico AI</a>
<a href="#identity">Identity (ORCID)</a>
<a href="#blueprint">The Blueprint</a>
<a href="#pitfalls">Pitfalls</a>
<a href="#code">The Code</a>
</nav>
</header>

<main>

<section id="identity" class="section">
<div class="section-head"><h2 class="mono">01 — The Atomic Unit of Open Science</h2><div class="line"></div></div>

<div class="klein-box-full">
  <div class="label">Scientific Identity</div>
  <div class="value">ORCID: The Permanent Identifier</div>
  <div class="desc">
    In traditional academia, institutions own your identity. In open science, <strong>you own your identity</strong>. 
    An ORCID iD is a free, permanent, 16-digit identifier that follows you across every repository, journal, and platform for the rest of your life. It is the foundational requirement for FAIR (Findable, Accessible, Interoperable, Reusable) data principles.
  </div>
</div>

<div class="grid2" style="margin-top:32px">
  <div class="card">
    <h3>Why Independent Researchers Need It</h3>
    <p>Without an ORCID, automated systems (like Zenodo and GitHub) cannot reliably attribute your code and datasets to you. An ORCID bridges the gap between independent work and the formal academic record, ensuring your discoveries are permanently linked to your name.</p>
  </div>
  <div class="card">
    <h3>How to Obtain It (5 Minutes)</h3>
    <ol>
      <li>Visit <a href="https://orcid.org/register" target="_blank">orcid.org/register</a></li>
      <li>Use a <strong>stable, permanent email address</strong> (never a temporary or institutional email you might lose).</li>
      <li>Set your affiliation to "Independent Researcher" or your organization.</li>
      <li>Save your 16-digit iD (e.g., <code>0000-000X-XXXX-XXXX</code>).</li>
    </ol>
  </div>
</div>
</section>

<section id="blueprint" class="section">
<div class="section-head"><h2 class="mono">02 — The Zenodo Blueprint (Zero-Cost DOIs)</h2><div class="line"></div></div>

<p>Zenodo is a free, open-access repository operated by CERN. It assigns permanent Digital Object Identifiers (DOIs) to your code and data. However, the order of operations is critical to avoid breaking your citations.</p>

<div class="grid3">
  <div class="card highlight">
    <h3>Step 1: The Sandbox</h3>
    <p>Always begin on <a href="https://sandbox.zenodo.org" target="_blank">sandbox.zenodo.org</a>. This is CERN's testing environment. Log in with your ORCID. Generate an API token with <code>deposit:actions</code> and <code>deposit:write</code> scopes.</p>
  </div>
  <div class="card highlight">
    <h3>Step 2: Reserve the DOI</h3>
    <p>Click "New Upload" and immediately click <strong>"Reserve DOI"</strong>. This locks in a permanent DOI (e.g., <code>10.5072/zenodo.123456</code>) <em>before</em> you publish. You can now test your automated scripts against this exact DOI without creating duplicate records.</p>
  </div>
  <div class="card highlight">
    <h3>Step 3: Automate & Publish</h3>
    <p>Add the Sandbox API token and Reserved DOI to your GitHub Secrets. Run your <code>zenodo_agent.py</code> script. Once the metadata and files are verified on Sandbox, repeat the exact process on production <a href="https://zenodo.org" target="_blank">zenodo.org</a>.</p>
  </div>
</div>
</section>

<section id="pitfalls" class="section">
<div class="section-head"><h2 class="mono">03 — The Pitfalls (What to Avoid)</h2><div class="line"></div></div>

<p>Many independent researchers lose their citations or lock themselves out of their own data. Here are the exact traps this blueprint avoids:</p>

<div class="danger-box">
  <strong>Pitfall #1: Publishing Before Testing</strong><br>
  <em>The Trap:</em> You push to production Zenodo, realize the metadata is wrong, and publish it. Zenodo DOIs are <strong>permanent and immutable</strong> once published. You cannot delete or change a published DOI.<br>
  <em>The Fix:</em> Always use the Sandbox. Always use "Reserve DOI" so you can edit the metadata 50 times before clicking "Publish".
</div>

<div class="danger-box">
  <strong>Pitfall #2: The Email Trap</strong><br>
  <em>The Trap:</em> You register your ORCID with a university or work email. You change jobs or graduate, lose access to the email, and can no longer recover your ORCID account.<br>
  <em>The Fix:</em> Use a permanent personal email (Gmail, ProtonMail) or a custom domain email that you control forever. Add your institutional emails only as secondary aliases.
</div>

<div class="danger-box">
  <strong>Pitfall #3: The Versioning Fragmentation</strong><br>
  <em>The Trap:</em> You update your code and run your Zenodo script again. Zenodo creates a <em>brand new DOI</em> for the update. Now your software has 5 different DOIs, and citations are fractured.<br>
  <em>The Fix:</em> Use Zenodo's "New Version" feature for updates, which keeps the concept DOI (the master DOI) the same while assigning a specific DOI to the exact version. Update the <code>version: "1.0.1"</code> in your <code>CITATION.cff</code> file before every run.
</div>
</section>

<section id="code" class="section">
<div class="section-head"><h2 class="mono">04 — The Code: CITATION.cff</h2><div class="line"></div></div>

<p>GitHub natively reads a file named <code>CITATION.cff</code> (Citation File Format) in your repository root. When this file exists, GitHub automatically generates a "Cite this repository" button on your repo's main page, and Zenodo reads it to auto-fill your metadata.</p>

<pre><code>cff-version: 1.2.0
message: "If you use this software, please cite it using the metadata from this file."
title: "Mesh Pico AI: A Neuroplastic Intelligence Framework"
authors:
  - family-names: "Audette"
    given-names: "Louis-Philippe"
    orcid: "https://orcid.org/0000-000X-XXXX-XXXX"  # &lt;-- Your actual ORCID
    affiliation: "PSIVI Research"
version: "1.0.0"
date-released: "2026-09-18"
url: "https://psivicom.github.io"
repository-code: "https://github.com/psivicom/psivicom.github.io"
license: "EUPL-1.2"
keywords:
  - "neuroplastic AI"
  - "decentralized computing"
  - "open science"
  - "FAIR principles"
type: software</code></pre>

<div class="highlight-box">
  <strong>For Other Researchers:</strong> To use this blueprint for your own project, simply fork the <code>zenodo_agent.py</code> and <code>embed_identity.py</code> scripts from the Mesh Pico AI repository. Replace the ORCID and repository URLs in the <code>CITATION.cff</code> file, and you instantly have a FAIR-compliant, automated DOI pipeline for your own research.
</div>

</section>

</main>

<footer>
<div>
<p>© 2026 Louis-Philippe Audette — PSIVI.COM</p>
<p>Content: <a href="https://creativecommons.org/licenses/by-sa/4.0/" style="text-decoration:underline">CC BY-SA 4.0</a> · Code: <a href="https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12" style="text-decoration:underline">EUPL 1.2</a></p>
</div>
<div style="text-align:right">
<p>NASA Open Science 101 Certified — Langford, BC</p>
</div>
</footer>
</div>
</body>
</html>
```
How to use this:
1. Create a new file in your repository root named open-science-guide.html.
2. Paste the code above.
3. Commit it.
4. It will instantly be live at
psivicom.github.io/open-science-
guide.html
Because it uses the exact same CSS classes (
•klein-box-full, •grid3, •danger-box) as your Mesh Pico Al page, it will look like it belongs in the same premium, professional documentation suite.
You can now share this link with any independent researcher in the world, and they will have a beautiful, pitfall-free guide to establishing their scientific identity. <3 ❤️


