<!--
  Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | CC BY-SA 4.0
-->
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

[2026-09-13T22:53:38.611Z] Aether Vanguard qwen deposited pheromone. Status: NOMINAL.

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

> **Institutional Compliance & Security:** This research software and data pipeline is fully compliant with the NIST Secure Software Development Framework (SP 800-218). It utilizes a domain-separated open-source architecture (EUPL 1.2 / CC BY-SA 4.0) to guarantee zero proprietary "black box" lock-in, with all AI-assisted workflows bound by strict, auditable human-in-the-loop provenance protocols. See [docs/NIST-SSDF-COMPLIANCE-MAPPING.md](docs/NIST-SSDF-COMPLIANCE-MAPPING.md) for full technical and legal verification.

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

## 04 — Domain-Separated License<br>
      — NASA + Space Partners Compliant

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

- [NIST SSDF Compliance Mapping](docs/NIST-SSDF-COMPLIANCE-MAPPING.md) — Technical and legal verification of NIST SP 800-218 alignment, preventing proprietary "black box" lock-in.
---

## 06 — Repository Structure <br>
      — Interconnected

<!-- AUTO_TREE_START -->
<!-- Last updated: 2026-09-18T08:12:59.089Z | Hash: 05f261bbb3914c20a352e22f356e2e272bb1ffe73bfc73afb6a31c07f593b901 -->

```
psivicom.github.io/
├── .github/
│   └── workflows/
│       ├── README.md
│       ├── critic-agent.yml
│       ├── docs.yml
│       ├── fix-all-timestamps.yml
│       ├── forage-agent.yml
│       ├── intelligence-agent.yml
│       ├── license-agent.yml
│       ├── lidar-agent.yml
│       ├── literature-ingest.yml
│       ├── mesh-governor.yml
│       ├── mesh-status.yml
│       ├── mesh.yml
│       ├── mesh_evolution.yml
│       ├── neuroplasticity.yml
│       ├── normalize-archive-names.yml
│       ├── rfc-compliance.yml
│       ├── rfc1001-compliance.yml
│       ├── seed-mesh.yml
│       ├── synthesizer-agent.yml
│       ├── timestamp-check.yml
│       ├── update-tree.yml
│       └── volunteer-mesh.yml
├── LICENSES/
│   ├── COPYRIGHT.md
│   ├── LICENSE-CC-BY-SA-4.0.md
│   ├── LICENSE-EUPL-1.2.md
│   └── README.md
├── _techreports/
│   └── YYYY-MM-DD-templatezenodo.md
├── archive/
│   ├── 2026-00-11/
│   │   ├── A_POLICY.md
│   │   └── A_REUSE.toml
│   ├── 2026-08-29/
│   │   └── A2026-08-29T2240Z_README.md
│   ├── 2026-08-30/
│   │   └── A2026-08-30T2240Z_README2.md
│   ├── 2026-09-05/
│   │   └── A2026-09-05T0000Z_A_index.html
│   ├── 2026-09-07/
│   │   ├── A2_CONTRIBUTING.md
│   │   ├── A3_POLICY.md
│   │   ├── A5_CONTRIBUTING.md
│   │   ├── A5_POLICY.md
│   │   ├── A_CONTRIBUTING.md
│   │   ├── A_POLICY.md
│   │   └── README.md
│   ├── 2026-09-08/
│   │   ├── A2_README.md
│   │   ├── A_0912_osdmp.md
│   │   ├── A_DATA_MANAGEMENT.md
│   │   ├── A_FAIR_CHECKLIST.md
│   │   ├── A_GITHUB-ACTIONS-GUIDE.md
│   │   ├── A_INTEROPERABILITY.md
│   │   ├── A_Installation-Guide-Repository-Tree.md
│   │   ├── A_LICENSE_COMPLIANCE.md
│   │   ├── A_README.md
│   │   ├── A_osdmp.md
│   │   └── A_template.html
│   ├── 2026-09-10/
│   │   └── A_update-tree.yml
│   ├── 2026-09-11/
│   │   ├── A_AUTHORS.md
│   │   ├── A_CHANGELOG.md
│   │   ├── A_CITATION.cff
│   │   ├── A_CONTRIBUTING.md
│   │   ├── A_NOTICE
│   │   ├── A_README.md
│   │   ├── A_SECURITY.md
│   │   ├── A_SECURITY_PLAN.md
│   │   ├── A_TRUST_AND_PROVENANCE.md
│   │   ├── A_codemeta.json
│   │   ├── A_config.yml
│   │   ├── A_index.html
│   │   ├── A_licensesREADMe.md
│   │   └── AdataREADME.md
│   ├── 2026-09-12/
│   │   ├── A2_README.md
│   │   ├── A2_codemeta.json
│   │   ├── A3_.zenodo.json
│   │   ├── A3_CITATION.cff
│   │   ├── A_.zenodo.json
│   │   ├── A_0912B_index.html
│   │   ├── A_0912_index.html
│   │   ├── A_main.go
│   │   └── A_oldTREE_update_tree.py
│   ├── 2026-09-13/
│   │   └── index.html
│   ├── 2026-09-16/
│   │   ├── A2_critic_agent.py
│   │   ├── A2_forage_agent.py
│   │   ├── A4_forage_agent.py
│   │   ├── A5_forage_agent.py
│   │   ├── A6_literature_agent.py
│   │   ├── A_3_index.html
│   │   ├── A_forage_agent.py
│   │   ├── A_intelligence_agent.py
│   │   └── A_vector_mesh.py
│   ├── 2026-09-17/
│   │   ├── A_backup_index,html
│   │   ├── A_mesh-Ai.html
│   │   └── A_mesh-ai.html
│   ├── deprecated/
│   │   ├── deprecated-LICENSE_COMPLIANCE2.md
│   │   ├── deprecated-teamai.html
│   │   ├── deprecated-teamai.md
│   │   ├── deprecated_AI-MORAL-Evolution.md
│   │   ├── deprecated_APACHE-2.0.txt
│   │   ├── deprecated_LICENSE
│   │   ├── deprecated_LICENSE-CC-BY-4.0.txt
│   │   ├── deprecated_NOTICE
│   │   └── deprecated_licenseREADME.md
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
├── config/
│   ├── aether-vanguard.psvc
│   └── mesh_topology.yaml
├── data/
│   ├── images/
│   │   └── README.md
│   ├── sample-pollinator-data/
│   │   ├── README.md
│   │   ├── data.csv
│   │   ├── datapackage.json
│   │   └── metadata.json
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
│   ├── SPACE_RESEARCH/
│   │   ├── exploreopenspaceresearch.html
│   │   └── unifiedopenspacehub.html
│   ├── WEBSITE_PLAN/
│   │   ├── README.md
│   │   └── mistral-AI-website-plan.md
│   ├── DATA_MANAGEMENT.md
│   ├── FAIR-mapping.md
│   ├── FAIR_CHECKLIST.md
│   ├── GITHUB-ACTIONS-GUIDE.md
│   ├── INTEROPERABILITY.md
│   ├── LICENSE_COMPLIANCE.md
│   ├── NIST-SSDF-COMPLIANCE-MAPPING.md
│   ├── OPEN_SCIENCE_POLICY.md
│   ├── README.md
│   ├── establish-RFC-guide.md
│   ├── establish-identity-guide.md
│   ├── installation-guide-repository-tree.md
│   ├── make-psvc-guide.md
│   ├── osdmp.html
│   ├── osdmp.md
│   ├── rfc1001.txt
│   └── template.html
├── maps/
│   └── forage_forecast.png
├── reports/
│   ├── pico_containers/
│   │   ├── state_0_55b8f4d3e01f.psvc
│   │   ├── state_0_6a236f59a9aa.psvc
│   │   ├── state_0_8e8202755302.psvc
│   │   ├── state_0_f816755d4086.psvc
│   │   ├── state_1_1683fb8d99e1.psvc
│   │   ├── state_1_c2d691e7b81c.psvc
│   │   ├── state_1_e6bbae07a097.psvc
│   │   ├── state_2_301afa57070e.psvc
│   │   ├── state_2_9d3839e18eed.psvc
│   │   └── state_2_c53c5acaffaf.psvc
│   ├── vector_memory/
│   │   ├── 2e034fc1b1be.json
│   │   ├── 2e034fc1b1be.npy
│   │   ├── 2fd673a34e0d.json
│   │   ├── 2fd673a34e0d.npy
│   │   ├── 32c50e6b93c2.json
│   │   ├── 32c50e6b93c2.npy
│   │   ├── 3fe04d4954d1.json
│   │   ├── 3fe04d4954d1.npy
│   │   ├── 5f8ef627117b.json
│   │   ├── 5f8ef627117b.npy
│   │   ├── 79aa021d242f.json
│   │   ├── 79aa021d242f.npy
│   │   ├── 976a1ba42d85.json
│   │   └── 976a1ba42d85.npy
│   ├── volunteer_contributions/
│   │   ├── 2026-09-17_external_volunteer_49b5fced.json
│   │   └── 2026-09-18_external_volunteer_df3588cb.json
│   ├── 2026-09-16_memory.json
│   ├── 2026-09-16_synthesizer_memory.json
│   ├── 2026-09-17_synthesizer_memory.json
│   ├── ai_audit.md
│   ├── forage_log.md
│   ├── governor_log.md
│   ├── license_audit.md
│   ├── mesh_status.txt
│   ├── synthesis_2026-09-16.md
│   └── synthesis_2026-09-17.md
├── scripts/
│   ├── update-tree/
│   │   └── main.go
│   └── fix_archive_names.py
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   └── vector_pixelizer.py
│   ├── nodes/
│   │   ├── __init__.py
│   │   └── pico_worker.py
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── mesh_brain.py
│   │   └── psvc_provisioner.py
│   └── __init__.py
├── tests/
│   ├── __init__.py
│   └── test_pixelizer_fidelity.py
├── tools/
│   └── fix_timestamps.py
├── .gitignore
├── .zenodo.json
├── AI-COLLABORATION-PROTOCOL.md
├── AUTHORS.md
├── CHANGELOG.md
├── CITATION.cff
├── CNAME
├── CODEOWNERS
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── DATA_LICENSE_MANIFEST.json
├── DISCLAIMER.md
├── Dockerfile
├── LICENSE
├── NOTICE
├── OPEN_SCIENCE_POLICY.md
├── POLICY.md
├── PROVENANCE.json
├── README.md
├── REUSE.toml
├── RFC.md
├── SECURITY.md
├── SECURITY_PLAN.md
├── TEAM-AI.md
├── TRUST_AND_PROVENANCE
├── VOLUNTEER_GUIDE.md
├── VOLUNTEER_PROTOCOL.md
├── _config.yml
├── agent_config.yaml
├── codemeta.json
├── consolidator_agent.py
├── critic_agent.py
├── docker-compose.yml
├── forage_agent.py
├── generate_api.py
├── how-psvc-works.html
├── how-psvc-works2.html
├── index.html
├── intelligence_agent.py
├── license_agent.py
├── lidar_agent.py
├── literature_agent.py
├── mesh-ai.html
├── mesh.go
├── mesh_governor.py
├── mesh_router.py
├── mesh_state.json
├── open-science-guide.html
├── pico_containers.py
├── pico_mesh.py
├── psvc_cli.py
├── psvc_reference.py
├── requirements.txt
├── robots.txt
├── seed_mesh.py
├── sitemap.xml
├── synthesizer_agent.py
├── test_rfc1001_compliance.py
├── vector_mesh.py
├── volunteer_node.py
├── volunteer_worker.py
└── vram_mesh.py
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
