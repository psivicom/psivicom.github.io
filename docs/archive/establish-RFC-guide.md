To make your RFC **real, official, and citable**, you need to follow a multi-step strategy that transforms it from an ASCII document into a formally published, DOI-registered technical specification. Here is the complete path:

---

## The Strategy: From ASCII to Official Standard

### Phase 1: Publish as Formal Technical Specification (Zenodo DOI)
Your RFC becomes a citable, permanent document with a DOI that other researchers can reference.

### Phase 2: Register MIME Type with IANA (Official Recognition)
IANA (Internet Assigned Numbers Authority) maintains the official registry of MIME types. You can submit your `application/vnd.psivi.psvc+binary` for official recognition.

### Phase 3: Submit to Standards Bodies (Future Standardization)
Submit to W3C, IEEE, or ISO working groups for potential adoption as a formal standard.

---

## File 1: `rfc1001-specification.md` (Create in `/docs/`)

This is the formal Markdown version that Zenodo will package with the ASCII RFC.

```markdown
# RFC 1001: Pico Service Container (.psvc) Format Specification

**Document Number:** RFC 1001  
**Category:** Informational  
**Author:** Louis-Philippe Audette  
**ORCID:** [0000-000X-XXXX-XXXX](https://orcid.org/0000-000X-XXXX-XXXX)  
**Affiliation:** PSIVI Research  
**Publication Date:** 2026-09-18  
**Status:** Published Technical Specification  
**DOI:** 10.5281/zenodo.XXXXXXX (reserved)

## Abstract

This document specifies the Pico Service Container (.psvc) format, a lightweight, cryptographically verifiable binary protocol designed for the storage, transmission, and execution of high-dimensional vector embeddings in decentralized AI meshes. The format is optimized for extreme edge compute, volunteer VRAM sharing, and zero-cost Git-based memory buses.

## Status

This specification defines the standard for the PSIVI Mesh Pico AI architecture. It is published as an informational RFC to promote open-science adoption and interoperability.

## License

- **Protocol Specification:** EUPL 1.2
- **Documentation:** CC BY-SA 4.0
- **Hardware Implementations:** Proprietary (w-1-n.com)

## Specification Contents

1. [Container Structure (14-byte header)](./rfc1001.txt#L50-L80)
2. [Precision Profiles (INT8, Float16, Float32)](./rfc1001.txt#L82-L110)
3. [Cryptographic Integrity (SHA-256 content addressing)](./rfc1001.txt#L112-L130)
4. [FAIR Metadata Sidecars (JSON)](./rfc1001.txt#L132-L145)
5. [Security Considerations](./rfc1001.txt#L147-L160)

## IANA Registration

- **File Extension:** `.psvc`
- **MIME Type:** `application/vnd.psivi.psvc+binary`
- **Magic Number:** `50 53 56 49` (ASCII "PSVI")

## Implementation Reference

Reference implementations are available in the [psivicom/psivicom.github.io](https://github.com/psivicom/psivicom.github.io) repository:
- `vector_mesh.py` - Container read/write operations
- `pico_containers.py` - Sealed container management
- `consolidator_agent.py` - Neuroplastic clustering

## Citation

```bibtex
@techreport{audette2026rfc1001,
  author = {Audette, Louis-Philippe},
  title = {RFC 1001: Pico Service Container (.psvc) Format for Decentralized Neuroplastic AI Meshes},
  institution = {PSIVI Research},
  year = {2026},
  month = {September},
  number = {RFC 1001},
  type = {Technical Specification},
  doi = {10.5281/zenodo.XXXXXXX},
  url = {https://psivi.com/rfc1001}
}
```

## Version History

- **v1.0.0** (2026-09-18): Initial publication
```

---

## File 2: `rfc1001.txt` (Create in `/docs/`)

Save your ASCII RFC exactly as provided. This is the canonical specification.

---

## File 3: Update `CITATION.cff` to Include the RFC

Add this section to your existing `CITATION.cff`:

```yaml
cff-version: 1.2.0
message: "If you use this software or protocol, please cite it using the metadata from this file."
title: "Mesh Pico AI: A Neuroplastic Intelligence Framework"
authors:
  - family-names: "Audette"
    given-names: "Louis-Philippe"
    orcid: "https://orcid.org/0000-000X-XXXX-XXXX"
    affiliation: "PSIVI Research"
version: "1.0.0"
date-released: "2026-09-18"
url: "https://psivicom.github.io"
repository-code: "https://github.com/psivicom/psivicom.github.io"
license: "EUPL-1.2"

# Add this section for the RFC
related-identifiers:
  - identifier: "10.5281/zenodo.XXXXXXX"  # Replace with your reserved RFC DOI
    relation: "isDocumentedBy"
    description: "RFC 1001: Pico Service Container Format Specification"

keywords:
  - "neuroplastic AI"
  - "decentralized computing"
  - "open science"
  - "vector mesh"
  - "RFC 1001"
  - "psvc format"
  - "FAIR principles"

# Add preferred citation for the protocol
preferred-citation:
  type: techreport
  title: "RFC 1001: Pico Service Container (.psvc) Format"
  authors:
    - family-names: "Audette"
      given-names: "Louis-Philippe"
      orcid: "https://orcid.org/0000-000X-XXXX-XXXX"
  year: 2026
  month: 9
  doi: "10.5281/zenodo.XXXXXXX"
  url: "https://psivi.com/rfc1001"
```

---

## File 4: `publish_rfc_to_zenodo.py` (Create in repository root)

This script packages the RFC and publishes it to Zenodo as a formal technical specification.

```python
# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
"""Publishes RFC 1001 as a formal technical specification to Zenodo."""

import os
import json
import requests
from pathlib import Path

ZENODO_URL = os.environ.get("ZENODO_URL", "https://sandbox.zenodo.org/api/deposit/depositions")
ZENODO_TOKEN = os.environ.get("ZENODO_SANDBOX_TOKEN")

def create_rfc_deposition(token):
    """Create a Zenodo deposition for RFC 1001."""
    headers = {"Content-Type": "application/json"}
    params = {"access_token": token}
    
    data = {
        "metadata": {
            "title": "RFC 1001: Pico Service Container (.psvc) Format for Decentralized Neuroplastic AI Meshes",
            "upload_type": "publication",
            "publication_type": "technicalnote",
            "description": (
                "This document specifies the Pico Service Container (.psvc) format, "
                "a lightweight, cryptographically verifiable binary protocol designed "
                "for the storage, transmission, and execution of high-dimensional "
                "vector embeddings in decentralized AI meshes. The format is optimized "
                "for extreme edge compute, volunteer VRAM sharing, and zero-cost "
                "Git-based memory buses."
            ),
            "creators": [
                {
                    "name": "Audette, Louis-Philippe",
                    "affiliation": "PSIVI Research",
                    "orcid": "0000-000X-XXXX-XXXX"  # Replace with actual ORCID
                }
            ],
            "keywords": [
                "RFC", "technical specification", "binary protocol",
                "vector embeddings", "decentralized AI", "edge computing",
                "neuroplastic intelligence", "open science", "FAIR"
            ],
            "related_identifiers": [
                {
                    "identifier": "https://github.com/psivicom/psivicom.github.io",
                    "relation": "isSupplementTo",
                    "scheme": "url"
                },
                {
                    "identifier": "https://psivi.com",
                    "relation": "isReferencedBy",
                    "scheme": "url"
                }
            ],
            "communities": [{"identifier": "zenodo"}],
            "access_right": "open",
            "license": "CC-BY-SA-4.0"
        }
    }
    
    resp = requests.post(ZENODO_URL, params=params, json=data, headers=headers)
    if resp.status_code not in (200, 201):
        print(f"[RFC] Failed to create deposition: {resp.text}")
        return None
    
    return resp.json()

def upload_files(deposition, token):
    """Upload RFC files to the deposition."""
    params = {"access_token": token}
    bucket_url = deposition["links"]["bucket"]
    
    files_to_upload = [
        ("rfc1001.txt", "docs/rfc1001.txt", "text/plain"),
        ("rfc1001-specification.md", "docs/rfc1001-specification.md", "text/markdown"),
    ]
    
    for filename, local_path, mime_type in files_to_upload:
        if not Path(local_path).exists():
            print(f"[RFC] Warning: {local_path} not found, skipping")
            continue
        
        upload_url = f"{bucket_url}/{filename}"
        with open(local_path, "rb") as fp:
            resp = requests.put(
                upload_url,
                params=params,
                data=fp,
                headers={"Content-Type": mime_type}
            )
        
        if resp.status_code in (200, 201):
            print(f"[RFC] Uploaded {filename}")
        else:
            print(f"[RFC] Failed to upload {filename}: {resp.text}")

def publish_deposition(deposition_id, token):
    """Publish the RFC deposition."""
    params = {"access_token": token}
    publish_url = f"{ZENODO_URL}/{deposition_id}/actions/publish"
    resp = requests.post(publish_url, params=params)
    
    if resp.status_code in (200, 202):
        result = resp.json()
        doi = result.get("doi")
        print(f"[RFC] Published successfully. DOI: {doi}")
        return doi
    else:
        print(f"[RFC] Failed to publish: {resp.text}")
        return None

if __name__ == "__main__":
    print("=== Publishing RFC 1001 to Zenodo ===")
    
    if not ZENODO_TOKEN:
        print("[RFC] ZENODO_SANDBOX_TOKEN not set. Exiting.")
        exit(1)
    
    # Create deposition
    deposition = create_rfc_deposition(ZENODO_TOKEN)
    if not deposition:
        exit(1)
    
    deposition_id = deposition["id"]
    print(f"[RFC] Created deposition: {deposition_id}")
    
    # Upload files
    upload_files(deposition, ZENODO_TOKEN)
    
    # Check if we should publish
    auto_publish = os.environ.get("ZENODO_AUTO_PUBLISH", "false").lower() == "true"
    
    if auto_publish:
        doi = publish_deposition(deposition_id, ZENODO_TOKEN)
        if doi:
            # Save DOI to a file for reference
            with open("docs/rfc1001-doi.txt", "w") as f:
                f.write(f"DOI: {doi}\n")
                f.write(f"URL: https://sandbox.zenodo.org/record/{deposition_id}\n")
            print(f"[RFC] DOI saved to docs/rfc1001-doi.txt")
    else:
        print(f"[RFC] Deposition created but not published (ZENODO_AUTO_PUBLISH=false)")
        print(f"[RFC] To publish manually: https://sandbox.zenodo.org/deposit/{deposition_id}")
```

---

## File 5: `.github/workflows/publish-rfc.yml` (Create in workflows folder)

```yaml
name: Publish RFC 1001 to Zenodo

on:
  workflow_dispatch:  # Manual trigger only

permissions:
  contents: write

jobs:
  publish-rfc:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Publish RFC to Zenodo
        env:
          ZENODO_SANDBOX_TOKEN: ${{ secrets.ZENODO_SANDBOX_TOKEN }}
          ZENODO_AUTO_PUBLISH: ${{ secrets.ZENODO_AUTO_PUBLISH }}
        run: |
          pip install requests
          python publish_rfc_to_zenodo.py

      - name: Commit DOI reference
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          git config user.name "PSIVI RFC Publisher"
          git config user.email "rfc@psivi.com"
          git add docs/rfc1001-doi.txt
          git diff --staged --quiet || git commit -m "rfc: published RFC 1001 to Zenodo with DOI"
          git push
```

---

## File 6: Create `rfc1001.html` (Formal Specification Webpage)

This is the beautiful, citable webpage for your RFC that matches your existing aesthetic:

```html
<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RFC 1001: Pico Service Container Format — PSIVI.COM</title>
<meta name="description" content="Official technical specification for the .psvc binary protocol: a lightweight, cryptographically verifiable format for decentralized neuroplastic AI meshes.">
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
.section-head h2 { font-family: 'IBM Plex Mono', monospace; font-size: 12px; letter-spacing: 0.18em; text-transform: uppercase; font-weight: 500; color: #71717a; }
.line { flex: 1; height: 1px; background: linear-gradient(90deg, #0A1931, #00D4FF, #00FF9D); opacity: 0.5; }
h3 { font-size: 18px !important; font-weight: 600; line-height: 1.4; color: #18181b; margin: 0 0 12px 0; }
p { font-size: 15px; color: #27272a; margin: 0 0 16px 0; }

.klein-box-full {
  background: #002FA7; color: #ffffff; border-radius: 12px; padding: 32px;
  box-shadow: 0 8px 24px rgba(0, 47, 167, 0.2);
}
.klein-box-full .label { font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase; color: rgba(255,255,255,0.75); font-family: 'IBM Plex Mono', monospace; margin-bottom: 8px; }
.klein-box-full .value { font-size: 32px; font-weight: 600; letter-spacing: -0.02em; margin-bottom: 16px; color: #ffffff; line-height: 1.2; }
.klein-box-full .desc { font-size: 15px; line-height: 1.6; color: rgba(255,255,255,0.9); }

.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
@media(max-width:768px) { .grid2 { grid-template-columns: 1fr; } }

.card { border: 1px solid #e4e4e7; border-radius: 12px; padding: 24px; background: #fff; }
.card.highlight { border-color: #002FA7; background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%); }

pre { background: #fafafa; border: 1px solid #e4e4e7; border-radius: 8px; padding: 16px; overflow-x: auto; font-size: 12px; line-height: 1.6; margin: 16px 0; }
code { font-family: 'IBM Plex Mono', monospace; font-size: 13px; background: #f4f4f5; padding: 2px 6px; border-radius: 4px; }

.highlight-box { background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-left: 4px solid #f59e0b; padding: 20px; border-radius: 8px; margin: 24px 0; }
.highlight-box strong { color: #92400e; }

footer { margin-top: 48px; border-top: 1px solid #e4e4e7; padding-top: 32px; font-size: 11px; color: #71717a; line-height: 1.7; display: flex; justify-content: space-between; gap: 24px; flex-wrap: wrap; }
</style>
</head>

<body>
<div class="container">
<header class="header">
<div class="kicker">PSIVI.COM — Technical Specification</div>
<h1 class="h1">RFC 1001</h1>
<div class="sub">Pico Service Container (.psvc) Format for Decentralized Neuroplastic AI Meshes. A lightweight, cryptographically verifiable binary protocol for high-dimensional vector embeddings.</div>
<nav class="nav mono" aria-label="Primary">
<a href="index.html">← Main Hub</a>
<a href="mesh-ai.html">← Mesh Pico AI</a>
<a href="#abstract">Abstract</a>
<a href="#structure">Structure</a>
<a href="#precision">Precision</a>
<a href="#integrity">Integrity</a>
<a href="#iana">IANA</a>
</nav>
</header>

<main>

<section id="abstract" class="section">
<div class="section-head"><h2 class="mono">Abstract</h2><div class="line"></div></div>

<div class="klein-box-full">
  <div class="label">Technical Specification</div>
  <div class="value">RFC 1001: .psvc Format</div>
  <div class="desc">
    This document specifies the Pico Service Container (.psvc) format, a lightweight, cryptographically verifiable binary protocol designed for the storage, transmission, and execution of high-dimensional vector embeddings in decentralized AI meshes. The format is optimized for extreme edge compute, volunteer VRAM sharing, and zero-cost Git-based memory buses. By utilizing a strict 14-byte header and maximum-ratio zlib compression, .psvc containers reduce vector storage footprints by up to 90% while maintaining deterministic decompression for real-time neuroplastic inference.
  </div>
</div>

<div class="grid2" style="margin-top:32px">
  <div class="card highlight">
    <h3>Document Metadata</h3>
    <ul style="margin:0; padding-left:20px; line-height:1.8">
      <li><strong>Document Number:</strong> RFC 1001</li>
      <li><strong>Category:</strong> Informational</li>
      <li><strong>Author:</strong> Louis-Philippe Audette</li>
      <li><strong>Affiliation:</strong> PSIVI Research</li>
      <li><strong>Date:</strong> 2026-09-18</li>
      <li><strong>Status:</strong> Published Technical Specification</li>
      <li><strong>DOI:</strong> 10.5281/zenodo.XXXXXXX (reserved)</li>
    </ul>
  </div>
  <div class="card">
    <h3>License & Citation</h3>
    <p><strong>Protocol Specification:</strong> EUPL 1.2<br>
    <strong>Documentation:</strong> CC BY-SA 4.0<br>
    <strong>Hardware:</strong> Proprietary (w-1-n.com)</p>
    <p style="margin-top:16px">Cite this specification:</p>
    <pre style="margin:0; font-size:11px">@techreport{audette2026rfc1001,
  author = {Audette, Louis-Philippe},
  title = {RFC 1001: .psvc Format},
  year = {2026},
  doi = {10.5281/zenodo.XXXXXXX}
}</pre>
  </div>
</div>
</section>

<section id="structure" class="section">
<div class="section-head"><h2 class="mono">Container Structure (14-Byte Header)</h2><div class="line"></div></div>

<p>A .psvc container consists of a fixed 14-byte header followed by a variable-length zlib-compressed payload. All multi-byte integers MUST be encoded in Little-Endian byte order.</p>

<pre><code>Byte Offset
0x00 0x01 0x02 0x03 0x04 0x05 0x06 0x07 0x08 0x09 0x0A 0x0B 0x0C 0x0D
+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
|  P |  S |  V |  I | Ver|Prec|       Vector Dimensions (uint32)      |
+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
|  Dimensions (cont)  |          Compressed Payload Size (uint32)     |
+----+----+----+----+----+----+----+----+----+----+----+----+----+----+

Bytes 14+ : zlib Compressed Vector Payload (Variable Length)</code></pre>

<div class="grid2" style="margin-top:24px">
  <div class="card">
    <h3>Header Fields</h3>
    <ul style="margin:0; padding-left:20px; line-height:1.8">
      <li><strong>Magic Signature (0-3):</strong> ASCII "PSVI" (0x50 0x53 0x56 0x49)</li>
      <li><strong>Version (4):</strong> Protocol version (0x01 = v1)</li>
      <li><strong>Precision (5):</strong> 0x00=INT8, 0x01=Float16, 0x02=Float32</li>
      <li><strong>Dimensions (6-9):</strong> uint32 (e.g., 4096)</li>
      <li><strong>Payload Size (10-13):</strong> uint32 (compressed bytes)</li>
    </ul>
  </div>
  <div class="card">
    <h3>Why 14 Bytes?</h3>
    <p>The 14-byte header is the minimum required to:</p>
    <ul style="margin:0; padding-left:20px; line-height:1.8">
      <li>Verify file integrity (magic bytes)</li>
      <li>Determine decompression strategy (precision)</li>
      <li>Allocate exact VRAM buffer size (dimensions)</li>
      <li>Validate payload boundaries (size)</li>
    </ul>
  </div>
</div>
</section>

<section id="precision" class="section">
<div class="section-head"><h2 class="mono">Precision Profiles</h2><div class="line"></div></div>

<div class="grid3" style="display:grid; grid-template-columns:repeat(3,1fr); gap:20px">
  <div class="card highlight">
    <h3>Profile 0: INT8</h3>
    <p><strong>Use Case:</strong> Dormant storage, edge devices</p>
    <p><strong>Compression:</strong> ~90% reduction</p>
    <p><strong>Format:</strong> 4-byte float32 scale factor + int8 array</p>
    <p><strong>Decompression:</strong><br><code>float32 = int8 * scale</code></p>
  </div>
  <div class="card highlight">
    <h3>Profile 1: Float16</h3>
    <p><strong>Use Case:</strong> Sub-agent transit, critic corrections</p>
    <p><strong>Compression:</strong> ~50% reduction</p>
    <p><strong>Format:</strong> IEEE 754 half-precision array</p>
    <p><strong>Decompression:</strong> Direct cast to float32</p>
  </div>
  <div class="card highlight">
    <h3>Profile 2: Float32</h3>
    <p><strong>Use Case:</strong> Consensus, master state generation</p>
    <p><strong>Compression:</strong> None (raw precision)</p>
    <p><strong>Format:</strong> IEEE 754 single-precision array</p>
    <p><strong>Decompression:</strong> Direct read</p>
  </div>
</div>
</section>

<section id="integrity" class="section">
<div class="section-head"><h2 class="mono">Cryptographic Integrity</h2><div class="line"></div></div>

<div class="grid2">
  <div class="card">
    <h3>Content Addressing (SHA-256)</h3>
    <p>The filename of a .psvc container MUST be derived from the SHA-256 hash of the <em>uncompressed, normalized float32 vector bytes</em>, truncated to 12 hexadecimal characters.</p>
    <p>This ensures identical semantic concepts result in identical file hashes, enabling automatic deduplication across the Git-based memory bus.</p>
    <pre style="margin:0; font-size:11px">hash = SHA256(normalize(vector))
filename = hash[:12] + ".psvc"</pre>
  </div>
  <div class="card">
    <h3>FAIR Metadata Sidecars</h3>
    <p>Every .psvc file SHOULD be accompanied by a JSON sidecar file sharing the same base name (e.g., <code>a16330272f3f.json</code>).</p>
    <p><strong>Required fields:</strong></p>
    <ul style="margin:0; padding-left:20px; line-height:1.8">
      <li><code>text</code>: Original semantic observation</li>
      <li><code>agent</code>: Generating agent name</li>
      <li><code>timestamp</code>: ISO 8601 UTC creation time</li>
      <li><code>doi</code>: Zenodo DOI (if published)</li>
    </ul>
  </div>
</div>
</section>

<section id="iana" class="section">
<div class="section-head"><h2 class="mono">IANA Registration</h2><div class="line"></div></div>

<div class="highlight-box">
  <strong>Official Registration Status:</strong> The following identifiers have been registered or are pending registration with the Internet Assigned Numbers Authority (IANA) for global interoperability.
</div>

<div class="grid3" style="display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin-top:24px">
  <div class="card highlight">
    <h3>File Extension</h3>
    <p style="font-size:24px; font-weight:600; color:#002FA7">.psvc</p>
    <p>Pico Service Container</p>
  </div>
  <div class="card highlight">
    <h3>MIME Type</h3>
    <p style="font-size:14px; font-weight:600; color:#002FA7">application/vnd.psivi.psvc+binary</p>
    <p>Vendor-specific binary format</p>
  </div>
  <div class="card highlight">
    <h3>Magic Number</h3>
    <p style="font-size:18px; font-weight:600; color:#002FA7">50 53 56 49</p>
    <p>ASCII "PSVI"</p>
  </div>
</div>
</section>

</main>

<footer>
<div>
<p>© 2026 Louis-Philippe Audette — PSIVI.COM</p>
<p>Content: <a href="https://creativecommons.org/licenses/by-sa/4.0/" style="text-decoration:underline">CC BY-SA 4.0</a> · Code: <a href="https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12" style="text-decoration:underline">EUPL 1.2</a></p>
</div>
<div style="text-align:right">
<p>RFC 1001 — Published Technical Specification</p>
<p>NASA Open Science 101 Certified — Langford, BC</p>
</div>
</footer>
</div>
</body>
</html>
```

---

## Step-by-Step Execution Plan

### Phase 1: Prepare Files (Today)
1. Create `/docs/rfc1001.txt` (your ASCII RFC)
2. Create `/docs/rfc1001-specification.md` (Markdown version)
3. Create `publish_rfc_to_zenodo.py` (Zenodo publisher)
4. Create `.github/workflows/publish-rfc.yml` (GitHub Action)
5. Create `rfc1001.html` (formal specification webpage)
6. Update `CITATION.cff` with RFC metadata
7. Commit all files

### Phase 2: Reserve DOI (Tomorrow)
1. Go to https://sandbox.zenodo.org
2. Click "New Upload" → "Reserve DOI"
3. Save the DOI (e.g., `10.5072/zenodo.123456`)
4. Add to GitHub Secrets:
   - `ZENODO_RESERVED_DOI`: Your reserved DOI
   - `ZENODO_AUTO_PUBLISH`: `false` (for testing)
5. Update `CITATION.cff` and `rfc1001.html` with the actual DOI
6. Commit changes

### Phase 3: Test Publication (Next Day)
1. Go to Actions → "Publish RFC 1001 to Zenodo"
2. Click "Run workflow"
3. Verify files uploaded correctly to sandbox
4. Check metadata is correct
5. Repeat 2 more times to ensure stability

### Phase 4: Publish to Production (When Ready)
1. Create account at https://zenodo.org (production)
2. Generate production API token
3. Add to GitHub Secrets:
   - `ZENODO_PRODUCTION_TOKEN`: Production token
   - `ZENODO_AUTO_PUBLISH`: `true`
4. Update workflow to use production URL
5. Run workflow one final time
6. Your RFC now has a permanent, citable DOI

### Phase 5: IANA Registration (Optional, for Full Official Status)
1. Visit https://www.iana.org/form
