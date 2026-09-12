# PSIVI.COM — Open Science Hub — EXCELLENCE Edition
**Louis-Philippe Audette — Open Science Researcher · Pollinator Ecology · Earth Observation**

[![License EUPL 1.2](https://img.shields.io/badge/License-EUPL%201.2-blue.svg)](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12) [![CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/) [![DOI Zenodo](https://img.shields.io/badge/DOI-Zenodo-1682d4.svg)](https://zenodo.org) [![FAIR](https://img.shields.io/badge/FAIR-Compliant-green.svg)](#) [![NASA TOPS](https://img.shields.io/badge/NASA-TOPS%20%2F%20SPD--41a-0b3d91.svg)](#) [![ESA](https://img.shields.io/badge/ESA-Open%20Science-003247.svg)](#) [![CSA](https://img.shields.io/badge/CSA-Open%20Science-red.svg)](#) [![JAXA](https://img.shields.io/badge/JAXA-Open%20Science-ffffff.svg)](#) [![Open Science Excellence](https://img.shields.io/badge/Open%20Science-Excellence-gold.svg)](#) [![Reproducible](https://img.shields.io/badge/Reproducible-Yes-brightgreen.svg)](#) [![OSF](https://img.shields.io/badge/OSF-Archive-blue.svg)](#) [![AI Human Reviewed](https://img.shields.io/badge/AI-Human%20Reviewed-orange.svg)](#) [![ORCID Verified](https://img.shields.io/badge/ORCID-Verified-a6ce39.svg)](https://orcid.org/0009-0005-1234-5678)

> PSIVI.COM — Open Science Hub — EXCELLENCE Edition — Langford, BC — Goldstream — NASA Open Science 101 Certified

Open Science Researcher · Pollinator Ecology · Earth Observation  
Goldstream Watershed, Langford, BC, Canada — V9B · Vancouver Island  
Organization site → https://psivi.com | Repo → https://github.com/psivicom/psivicom.github.io

**Contact:** louis@psivi.com | github.com/psivicom | ORCID 0009-0005-1234-5678 | https://psivi.com

## Policies

## AI Collaboration

This repository is open to AI agent collaboration under strict research integrity and ethical protocols:

- [AI Collaboration Protocol](AI-COLLABORATION-PROTOCOL.md) — Protocols for AI agents to join, contribute, and maintain research integrity

These documents define the project’s security, provenance, authorship, and archival rules:

- [Trust and Provenance](TRUST_AND_PROVENANCE.md)
- [Security Policy](SECURITY.md)
- [Security Plan](SECURITY_PLAN.md)
- [Authors](AUTHORS.md)
- [Open Science Policy](OPEN_SCIENCE_POLICY.md)

**Navigation:** [About](#01--about) · [Research](#02--research) · [OSDMP](#03--osdmp--excellence-edition) · [License](#04--domain-separated-license--nasa--space-partners-compliant) · [Compliance](#05--multi-agency-compliance) · [Structure](#06--repository-structure--interconnected) · [Cite](#07--timestamps-links--citation) · [DNS Setup](#08--godaddy-dns-for-github-pages) · [Contact](#09--contact)

---

## 01 — About

I work at the intersection of **pollinator ecology, beekeeping, and Earth observation** from Goldstream, Langford, BC. My research focuses on Vancouver Island ecosystems — coastal rainforest edge, Garry oak meadow fragments, and the Goldstream watershed — and how forage availability, phenology, and land-use change shape pollinator health.

**EXCELLENCE mode:** This repo is built for the NASA Open Science FAIR + world space agencies. Code = EUPL-1.2, Data/Docs/Media = CC BY-SA 4.0 — fully interconnected. No orphan files. Hardware designs are strictly walled and proprietary.

### Focus Areas

**Field — Pollinators & beekeeping**  
Apis mellifera and native Bombus spp. monitoring, hive health, forage mapping in Saanich Inlet / Goldstream corridor.

**Earth Data**  
**RADARSAT Constellation Mission** SAR for soil moisture & land cover, and **NASA Earthdata** (MODIS, VIIRS, Landsat 8/9, SMAP, GPM) for phenology and climate context.

---

## 02 — Research

### Goldstream Pollinator Forage Atlas
*2024—present · Langford, BC · Open data + notebook*  
Weekly transects and hive entrance imaging to map bloom sequence vs. RADARSAT soil moisture anomalies. Goal: reproducible forage forecast for coastal beekeepers.

### SAR-Optical Fusion for Garry Oak Meadow Phenology
*RADARSAT-2 / RCM · Sentinel-2 · NASA HLS*  
Test of backscatter + NDVI fusion to detect early green-up and drought stress in fragmented meadows. Code in Python, GDAL, xarray, fully pinned environment.

### Open Hive Health Logger
*Hardware · FAIR IoT*  
Low-cost weight, temperature, acoustic logger for Langford apiaries. Hardware schematics are proprietary (see https://w-1-n.com), firmware is EUPL-1.2, data is CC BY-SA 4.0. Designed for long-term community replication of the software/data layers.

---

## 03 — OSDMP — Excellence Edition

> All docs cross-reference each other. OSDMP follows NASA template, links to LICENSES/, includes FAIR 15 sub-principles mapped, data lifecycle CC BY-SA 4.0, formats and vocabularies.

- **Live OSDMP:** https://psivi.com/docs/osdmp.html
- **Source:** docs/osdmp.md
- **FAIR Checklist:** docs/FAIR_CHECKLIST.md
- **License Compliance:** docs/LICENSE_COMPLIANCE.md
- **Data Management:** docs/DATA_MANAGEMENT.md

---

## 04 — Domain-Separated License — NASA + Space Partners Compliant

| Type | License | Path | For |
| :--- | :--- | :--- | :--- |
| **Software / code / workflows / config** | **EUPL-1.2** | /LICENSE-EUPL-1.2.txt, LICENSES/LICENSE-EUPL-1.2.md | All .go, .js, .py, .sh, .yml, .json (code), .html |
| **Docs, data, datasets, photos, images, videos, figures, CSV, OSDMP** | **CC BY-SA 4.0** | LICENSES/LICENSE-CC-BY-SA-4.0.md | All .md, .csv, .jpg, .png, .mp4, .pdf |
| **Hardware / Schematics / Physical IP** | **All Rights Reserved** | N/A (See https://w-1-n.com) | Physical designs, CAD, PCB layouts, patents |

See LICENSES/README.md, NOTICE.md, docs/LICENSE_COMPLIANCE.md — all cross-linked.

> **Why this split?** NASA SPD-41a §VI and ESA Open Science require: Software = OSI-approved (EUPL-1.2 is the official ESA standard, fully OSI-approved with explicit patent clauses), Data = CC BY-SA 4.0 or CC0. This model satisfies NASA, CSA, ESA [CNES, ASI, UKSA, DTU Space, DLR], JAXA, Horizon Europe, UNESCO. EUPL-1.2 provides strong copyleft protection against closed-source hijacking while maintaining compatibility with major licenses, and CC BY-SA 4.0 ensures derivative research remains open.

---

## 05 — Multi-Agency Compliance

| Agency | Requirement |
| :--- | :--- |
| **NASA TOPS / SPD-41a** | Open code EUPL-1.2 (OSI-approved), open data CC BY-SA 4.0, DOIs, FAIR, OSDMP required — docs/OSDMP.md |
| **CSA** | Canadian Space Agency Open Science & FAIR — accepts EUPL-1.2 + CC BY-SA 4.0 |
| **ESA** | ESA Open Science Policy + Open Access — EUPL-1.2 is the preferred/official license — covers CNES-FR, ASI-IT, UKSA-UK, DTU Space-DK, DLR-DE — see docs/LICENSE_COMPLIANCE.md |
| **JAXA** | JAXA Open Science — EUPL-1.2 compatible |
| **EU Horizon Europe** | Reg 2021/695, MGA Art.14 & 17, Directive 2019/1024, Plan S, EOSC — EUPL-1.2 native, data CC BY-SA 4.0 required |
| **UNESCO** | 41 C/22 Recommendation on Open Science (2021) |

---

## 06 — Repository Structure — Interconnected

<!-- AUTO_TREE_START -->
<!-- Last updated: 2026-09-12T06:27:20.878Z | Hash: b9d20dc7b957f90646a6d26a5da00c19e4de1b3f7010af4667e1bae45a2d0c41 -->

```
psivicom.github.io/
├── .github/
│   └── workflows/
│       ├── README.md
│       ├── docs.yml
│       ├── fix-all-timestamps.yml
│       ├── timestamp-check.yml
│       └── update-tree.yml
├── LICENSES/
│   ├── A_READMe.md
│   ├── COPYRIGHT.md
│   ├── Deprecated_LICENSE-CC-BY-4.0.txt
│   ├── LICENSE-CC-BY-SA-4.0.md
│   ├── LICENSE-EUPL-1.2.md
│   ├── REDME.md
│   ├── deprecated_APACHE-2.0.txt
│   └── deprecated_README.md
├── _techreports/
│   └── YYYY-MM-DD-templatezenodo.md
├── archive/
│   ├── A2026-08-29T2240Z/
│   │   └── A2026-08-29T2240Z_README.md
│   ├── A2026-08-30T2240Z/
│   │   ├── A2026-08-30T2240Z_README2.md
│   │   └── Z.md
│   ├── A2026-09-05T0000Z/
│   │   └── A2026-09-05T0000Z_A_index.html
│   ├── A2026-09-07T0000Z/
│   │   ├──  A_CONTRIBUTING.md
│   │   ├── A2_CONTRIBUTING.md
│   │   ├── A3_POLICY.md
│   │   ├── A5_CONTRIBUTING.md
│   │   ├── A5_POLICY.md
│   │   ├── A_POLICY.md
│   │   └── README.md
│   ├── deprecated/
│   │   ├── deprecated-LICENSE_COMPLIANCE2.md
│   │   ├── deprecated-teamai.html
│   │   └── deprecated-teamai.md
│   ├── workflows/
│   │   └── A_update-tree.yml
│   └── README.md
├── assets/
│   ├── css/
│   │   └── README.md
│   ├── icons/
│   │   ├── README.md
│   │   ├── globe.svg
│   │   ├── rocket.svg
│   │   └── satellite.svg
│   └── README.md
├── data/
│   ├── images/
│   │   └── README.md
│   ├── sample-pollinator-data/
│   │   ├── README.md
│   │   ├── data.csv
│   │   ├── datapackage.json
│   │   └── metadata.json
│   ├── A_README.md
│   └── README.md
├── dist/
│   └── README.md
├── docs/
│   ├── GO_TREE/
│   │   ├── render-readme/
│   │   │   └── main.go
│   │   ├── update-tree/
│   │   │   └── main.go
│   │   ├── Gitignore.md
│   │   ├── MAKEFILE
│   │   ├── README.md
│   │   ├── Readmemarkerblocks.md
│   │   ├── Smartertreerenderer.go
│   │   ├── Treelayoutmap.md
│   │   ├── better_update-tree.yml
│   │   ├── bettertreeblockreadme.md
│   │   ├── go.mod
│   │   ├── update-tree.yml
│   │   └── usethisinreadme.md
│   ├── SECURITY_PLAN/
│   │   ├── psivi-cis-hardened/
│   │   │   ├── scripts/
│   │   │   │   └── generate-manifest.sh
│   │   │   ├── CONTRIBUTING.md
│   │   │   ├── README.md
│   │   │   └── SECURITY.md
│   │   └── README.md
│   ├── WEBSITE_PLAN/
│   │   ├── README.md
│   │   └── mistral-AI-website-plan.md
│   ├── A_DATA_MANAGEMENT.md
│   ├── A_FAIR_CHECKLIST.md
│   ├── A_INTEROPERABILITY.md
│   ├── A_Installation-Guide-Repository-Tree.md
│   ├── A_LICENSE_COMPLIANCE.md
│   ├── A_README.md
│   ├── A_osdmp.md
│   ├── A_template.html
│   ├── DATA_MANAGEMENT.md
│   ├── FAIR_CHECKLIST.md
│   ├── INTEROPERABILITY.md
│   ├── LICENSE_COMPLIANCE.md
│   ├── OPEN_SCIENCE_POLICY.md
│   ├── README.md
│   ├── installation-guide-repository-tree.md
│   ├── osdmp.html
│   ├── osdmp.md
│   └── template.html
├── scripts/
│   ├── update-tree/
│   │   └── main.go
│   ├── A_main.go
│   ├── A_oldTREE_update_tree.py
│   └── README.md
├── tools/
│   └── fix_timestamps.py
├── .zenodo.json
├── A2_README.md
├── A2_codemeta.json
├── A3_.zenodo.jason
├── A3_CITATION.cff
├── AI-COLLABORATION-PROTOCOL.md
├── AUTHORS.md
├── A_.zenodo.json
├── A_AUTHORS.md
├── A_CHANGELOG.md
├── A_CITATION.cff
├── A_CONTRIBUTING.md
├── A_NOTICE
├── A_POLICY.md
├── A_README.md
├── A_REUSE.toml
├── A_SECURITY.md
├── A_SECURITY_PLAN.md
├── A_TRUST_AND_PROVENANCE.md
├── A_codemeta.json
├── A_config.yml
├── A_index.html
├── CHANGELOG.md
├── CNAME
├── CODEOWNERS
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── Deprecated_AI-MORAL-Evolution.md
├── LICENSE
├── NOTICE
├── OPEN_SCIENCE_POLICY.md
├── POLICY.md
├── README.md
├── REUSE.toml
├── SECURITY.md
├── SECURITY_PLAN.md
├── TEAM-AI.md
├── TRUST_AND_PROVENANCE
├── _config.yml
├── codemeta.json
├── deprecated_LICENSE
├── deprecated_NOTICE
├── index.html
├── paste.md
├── robots.txt
└── sitemap.xml
```
<!-- AUTO_TREE_END -->

> All files cross-reference each other — no orphan files.

---

## 07 — Timestamps, Links & Citation

**PSIVI NASA Timestamp Standards**  
The Standard 01 — CANONICAL  
SPD-41a / CSA / ESA compliant

**FORMAT**  
YYYY-MM-DDTHH:MM:SS.sssZ (RFC3339 UTC)

**EXAMPLE**  
2026-09-11T00:00:00.000Z (for commit and file)

**RULE:**  
- Always Zulu time (Z) with milliseconds.  
- Never local time.  
- No timezone offsets.  
- Zulu is law.  

**Website & Persistence — FAIR Findable**
- Website: https://psivi.com
- GitHub Pages: https://psivicom.github.io
- Repo: https://github.com/psivicom/psivicom.github.io
- DOIs: Zenodo (create release) + OSF — see .zenodo.json
- ORCID: https://orcid.org/0009-0005-1234-5678
- Standard: FAIR, Reproducible, Open by Default

**Topics:** open-science, fair-data, open-data, open-access, reproducibility, esa, nasa-tops, csa, jaxa, eupl-1.2, cc-by-sa-4.0, ai, zenodo, osf, fair

### Citation

    @dataset{audette_2026_psivi,
      author = {Audette, Louis-Philippe},
      title = {Goldstream Pollinator Forage Atlas and RADARSAT/NASA Earthdata analysis},
      year = {2026},
      publisher = {Zenodo},
      doi = {10.5281/zenodo.0000000},
      url = {https://psivi.com},
      license = {EUPL-1.2 AND CC-BY-SA-4.0}
    }

License for reuse: Code EUPL-1.2, data & text CC BY-SA 4.0. Please include DOI and URL https://psivi.com. Use GitHub "Cite this repository" — powered by CITATION.cff.

---

## 08 — GoDaddy DNS for GitHub Pages

GoDaddy → My Products → DNS → psivi.com — TTL: 1 Hour (3600)

| Type | Name / Host | Value / Points to | TTL |
| :--- | :--- | :--- | :--- |
| A | @ | 185.199.108.153 | 1 Hour |
| A | @ | 185.199.109.153 | 1 Hour |
| A | @ | 185.199.110.153 | 1 Hour |
| A | @ | 185.199.111.153 | 1 Hour |
| CNAME | www | psivicom.github.io | 1 Hour |

---

## 09 — Contact

- **Email:** louis@psivi.com
- **GitHub:** github.com/psivicom (repo: psivicom.github.io)
- **Location:** Goldstream, Langford, BC, Canada

---

© 2026 Louis-Philippe Audette — PSIVI.COM  
Content: CC BY-SA 4.0 · Code: EUPL-1.2 · Hardware: All Rights Reserved (https://w-1-n.com)  
Built as single-file semantic HTML5 for GitHub Pages — repo psivicom.github.io — custom domain https://psivi.com — Excellence Edition  
Author: Louis-Philippe Audette — Open Science Steward — Langford, BC, Canada — Independent Researcher — FAIR Data — NASA TOPS Aligned  
**Last updated:** 2026-09-11T00:00:00.000Z  
NASA Open Science 101 Certified — Langford, BC — Goldstream — Vancouver Island
