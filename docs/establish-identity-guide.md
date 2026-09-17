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


   
