# # Installation Guide & Repository Tree — Excellence Edition

**Architect & Principal Investigator:** Louis-Philippe Audette  
**Affiliation:** Independent Researcher, Goldstream, Langford, BC, Canada  
**Last Updated:** 2026-09-11T00:00:00.000Z  

---

## 1. Overview

This guide provides step-by-step instructions for cloning, setting up, and navigating the PSIVI.COM Open Science Hub repository. The repository is designed for maximum reproducibility, FAIR compliance, and seamless integration with NASA, ESA, and CSA open-science workflows.

**Important:** This repository contains open-source software, open data, and open documentation. Hardware designs and physical implementations are **All Rights Reserved** and managed separately at [w-1-n.com](https://w-1-n.com).

---

## 2. Prerequisites

Before cloning the repository, ensure you have the following installed:

### 2.1 Required Software

| Software | Version | Purpose |
| :--- | :--- | :--- |
| **Git** | 2.30+ | Version control |
| **Python** | 3.10+ | Data processing scripts |
| **Go** | 1.21+ | Tree rendering and automation tools |
| **Node.js** | 18+ (optional) | Jekyll local development |
| **Jekyll** | 4.3+ (optional) | Local website preview |

### 2.2 Recommended Tools

- **VS Code** or **Cursor** — Code editor with Markdown preview
- **GitHub CLI (`gh`)** — Streamlined GitHub workflows
- **jq** — JSON processing for metadata validation
- **tree** — Visualize repository structure

---

## 3. Installation Steps

### 3.1 Clone the Repository

```bash
# Clone via HTTPS
git clone https://github.com/psivicom/psivicom.github.io.git

# Or via GitHub CLI
gh repo clone psivicom/psivicom.github.io

# Navigate into the repository
cd psivicom.github.io
```

3.2 Verify License Compliance after cloning, verify that all license files are present and correctly configured:

Expected output:

LICENSE-EUPL-1.2.txt
LICENSE-CC-BY-SA-4.0.md
NOTICE.md
LICENSES/
  ├── README.md
  ├── COPYRIGHT.md
  └── ...

3.3 Install Python Dependencies (Optional)If you plan to run data processing scripts:

```bash
# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (if requirements.txt exists)
pip install -r requirements.txt

# Or install manually
pip install pandas numpy xarray gdal
```
3.4 Install Go Dependencies (Optional)If you plan to run tree rendering or automation tools:

```bash
# Navigate to Go tools directory
cd docs/GO_TREE/

# Download dependencies
go mod download

# Build tools
go build -o update-tree update-tree/main.go
go build -o render-readme render-readme/main.go
```
3.5 Local Website Preview (Optional)To preview the website locally with Jekyll:

```bash
# Install Jekyll and Bundler
gem install jekyll bundler

# Install dependencies
bundle install

# Serve the site locally
bundle exec jekyll serve

# Open in browser
# http://localhost:4000
```
4. Repository Tree StructureThe repository is organized for maximum clarity, FAIR compliance, and institutional interoperability.
```text
psivicom.github.io/
│
├── 📄 LICENSE-EUPL-1.2.txt          # EUPL 1.2 license (code)
├── 📄 LICENSE-CC-BY-SA-4.0.md       # CC BY-SA 4.0 license (data/docs)
├── 📄 NOTICE.md                     # Audette Clause & attributions
├── 📄 README.md                     # Main project overview
├── 📄 CITATION.cff                  # GitHub "Cite this repository" metadata
├── 📄 codemeta.json                 # Machine-readable software metadata
├── 📄 .zenodo.json                  # Zenodo DOI minting metadata
├── 📄 _config.yml                   # Jekyll configuration
├── 📄 index.html                    # Homepage (Excellence Edition)
├── 📄 CNAME                         # Custom domain (psivi.com)
│
├── 📁 LICENSES/                     # License documentation
│   ├── README.md                    # Dual-license compliance matrix
│   ├── COPYRIGHT.md                 # Copyright notices
│   └── ...                          # Additional license files
│
├── 📁 docs/                         # Documentation & policies
│   ├── OPEN_SCIENCE_POLICY.md       # Overarching research policy
│   ├── LICENSE_COMPLIANCE.md        # Licensing legalities
│   ├── DATA_MANAGEMENT.md           # Data lifecycle & FAIR compliance
│   ├── FAIR_CHECKLIST.md            # FAIR 15 sub-principles validation
│   ├── INTEROPERABILITY.md          # Cross-platform compatibility
│   ├── Installation-Guide-Repository-Tree.md  # This file
│   ├── osdmp.md                     # Open Science Data Management Plan
│   ├── osdmp.html                   # Live OSDMP (rendered)
│   └── GO_TREE/                     # Go-based tree rendering tools
│       ├── update-tree/
│       ├── render-readme/
│       └── ...
│
├── 📁 data/                         # Open datasets (CC BY-SA 4.0)
│   ├── sample-pollinator-data/
│   │   ├── data.csv                 # Sample dataset
│   │   ├── metadata.json            # FAIR metadata
│   │   └── datapackage.json         # Frictionless Data standard
│   ├── images/                      # Research images
│   └── README.md
│
├── 📁 scripts/                      # Automation & processing scripts (EUPL 1.2)
│   ├── update-tree/
│   │   └── main.go                  # Tree update tool
│   └── README.md
│
├── 📁 tools/                        # Utility scripts
│   └── fix_timestamps.py            # Timestamp standardization
│
├── 📁 assets/                       # Website assets
│   ├── css/
│   ├── icons/
│   └── README.md
│
├── 📁 archive/                      # Deprecated or historical files
│   └── ...
│
├── 📁 .github/                      # GitHub Actions workflows
│   └── workflows/
│       ├── docs.yml
│       ├── update-tree.yml
│       └── ...
│
└── 📁 _techreports/                 # Technical report templates
    └── YYYY-MM-DD-templatezenodo.md
```

5. Understanding the License Boundaries:
   
5.1 What is Open Source (EUPL 1.2 / CC BY-SA 4.0)
✅ You can:Use, modify, and distribute all code (EUPL 1.2)Use, modify, and distribute all data and documentation (CC BY-SA 4.0)
Cite the research using the provided DOI and CITATION.cff
Contribute improvements via pull requests
⚠️ You must:Retain the "Audette Clause" attribution in NOTICE.md
Keep derivative code under EUPL 1.2 
Keep derivative data/docs under CC BY-SA 4.0
Clearly state any changes you make.

5.2 What is NOT Open Source (All Rights Reserved)🚫 Hardware & Physical IP:CAD files, PCB layouts, schematics, and Bill of Materials (BOM)Physical implementation designs Proprietary sensor configurations 
These are managed separately at https//w-1-n.com and are available for commercial licensing only.

6.0 Validation & Testing

6.1 Validate JSON Metadata

```bash
# Validate codemeta.json
jq . codemeta.json > /dev/null && echo "✅ codemeta.json is valid JSON"

# Validate .zenodo.json
jq . .zenodo.json > /dev/null && echo "✅ .zenodo.json is valid JSON"

# Validate data metadata
jq . data/sample-pollinator-data/metadata.json > /dev/null && echo "✅ metadata.json is valid JSON"
```
6.2 Check License HeadersVerify that code files include proper SPDX identifiers:

```bash
# Check a Go file
head -n 3 scripts/update-tree/main.go

# Expected output:
# // Copyright 2026 Louis-Philippe Audette
# // SPDX-License-Identifier: EUPL-1.2
# // Licensed under the EUPL 1.2 — see /LICENSE-EUPL-1.2.txt
```
6.3 Verify TimestampsEnsure all timestamps follow the Zulu format with milliseconds:

```bash
# Check a documentation file
grep "Last Updated:" docs/OPEN_SCIENCE_POLICY.md

# Expected output:
# **Last Updated:** 2026-09-11T00:00:00.000Z
```
7. Troubleshooting
7.1 Jekyll Build ErrorsProblem: bundle exec jekyll serve fails with dependency errors.
Solution:

```bash
# Update Bundler
gem install bundler

# Clean and reinstall
rm -rf .bundle Gemfile.lock
bundle install
```
7.2 Go Build ErrorsProblem: go build fails with missing dependencies.
Solution:

```bash
# Navigate to Go directory
cd docs/GO_TREE/

# Download dependencies
go mod tidy
go mod download
```
7.3 Git LFS IssuesProblem: Large files fail to clone.
Solution:

```bash
# Install Git LFS
git lfs install

# Pull LFS files
git lfs pull
```

8.0 Compliance Cross-ReferenceFor licensing legalities, see: LICENSE_COMPLIANCE.md
For overarching research policies, see: OPEN_SCIENCE_POLICY.md
For data management details, see: DATA_MANAGEMENT.md
For FAIR validation, see: FAIR_CHECKLIST.md
For interoperability standards, see: INTEROPERABILITY.md

9.0 Contact to Support Research: support@psivi.com

For Research inquiries: louis@psivi.com

For GitHub Issues: github.com/psivicom/psivicom.github.io/issues

For Hardware/Commercial Licensing: https://w-1-n.com 

This guide is a living document. It is updated as the repository structure evolves and new tools are added.

---

## 10. Intellectual Property & Licensing

**Copyright © 2026 Louis-Philippe Audette — Independent Researcher, Goldstream, Langford, BC, Canada**

This installation guide is part of the PSIVI.COM Open Science Hub and is released under a domain-separated licensing framework:

- **This document (and all documentation/data):** Licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). You are free to share and adapt it, provided you give appropriate credit to Louis-Philippe Audette and distribute derivative works under the same license.
- **Referenced code and scripts:** Licensed under [EUPL 1.2](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12), ensuring strong copyleft protection for all executable software.
- **Hardware designs and physical IP:** Managed separately under All Rights Reserved at [w-1-n.com](https://w-1-n.com). This guide covers software and documentation only.

### The Audette Clause

This architecture — including its distributed systems, telemetry design, and operational frameworks — was conceived, authored, and architected by **Louis-Philippe Audette**. Any deployment, publication, derivative work, or commercial application must prominently retain attribution and provide clear credit to the original architect.

### Full License Texts

- Code → [`/LICENSE-EUPL-1.2.txt`](/LICENSE-EUPL-1.2.txt)
- Docs & Data → [`/LICENSE-CC-BY-SA-4.0.md`](/LICENSE-CC-BY-SA-4.0.md)
- Attribution & Origin → [`/NOTICE.md`](/NOTICE.md)
- Compliance Matrix → [`/LICENSES/README.md`](/LICENSES/README.md)

---

*Part of the PSIVI.COM Open Science Hub — Excellence Edition.*  
*Aligned with NASA TOPS, ESA Open Science Policy, CSA, and Horizon Europe standards.*  
*Last Updated: 2026-09-11T00:00:00.000Z*
