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

NO_CLOUD_LLM — Do not add calls to paid cloud LLM providers or include API keys. Use local or volunteer-hosted open models only. WENDY WILL NOT ASK DO YOU HAVE MONEY, SHE IS NOT A COKE MACHINE 

This repository is open to FREE AI agent collaboration under strict research integrity and ethical protocols:

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
Low-cost weight, temperature, acoustic logger for Langford apiaries. Hardware schematics are proprietary, non-hardware firmware is EUPL-1.2, data is CC BY-SA 4.0. Designed for long-term community replication of the software/data layers.

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
| **Hardware / Schematics / Physical IP** | **All Rights Reserved** | Physical designs, CAD, PCB layouts, patents |

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

## 06 — Repository Structure

<!-- AUTO_TREE_START -->
<!-- Auto-updated by .github/workflows/update-tree.yml -->
<!-- Last updated: 2026-11-14T00:09:33.000Z -->
```text
./
├── .github/
│   ├── workflows/
│   │   ├── README.md
│   │   ├── update-tree.yml
│   │   ├── vendor-nasa-os101.yml
│   │   ├── wendy-autonomous-compile.yml
│   │   ├── wendy-autonomous-evolution.yml
│   │   ├── wendy-awaken.yml
│   │   ├── wendy-benchmark.yml
│   │   ├── wendy-ci-cd.yml
│   │   ├── wendy-evolution.yml
│   │   ├── wendy-orchestrator.yml
│   │   ├── wendy-self-bootstrap.yml
│   │   ├── wendy-smart-dispatch.yml
│   │   ├── wendy-workflow-auditor.yml
│   │   └── wendy_synapse.yml
│   └── .dependabot.yml
├── .provenance/
│   └── nasa-os101/
│       ├── local-additions.txt
│       ├── manifest.sha256
│       ├── provenance.json
│       └── record.json
├── LICENSES/
│   ├── COPYRIGHT.md
│   ├── LICENSE-CC-BY-SA-4.0.md
│   ├── LICENSE-EUPL-1.2.md
│   └── README.md
├── archive/
│   └── README.md
├── nasa-open-science/
│   ├── .github/
│   │   └── workflows/
│   │       ├── book.yml
│   │       ├── broken-link-check.yml
│   │       └── check_typos.yml
│   ├── Module_1/
│   │   ├── Lesson_1/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_2/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_3/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_4/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_5/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── images/
│   │   │   └── media/
│   │   │       ├── atmocomp.jpg
│   │   │       ├── harlanquote.jpg
│   │   │       ├── image1.png
│   │   │       ├── image100.png
│   │   │       ├── image106.jpg
│   │   │       ├── image130.jpg
│   │   │       ├── image136.png
│   │   │       ├── image143.png
│   │   │       ├── image16.png
│   │   │       ├── image165.png
│   │   │       ├── image193.png
│   │   │       ├── image195.png
│   │   │       ├── image2.png
│   │   │       ├── image214.png
│   │   │       ├── image216.jpg
│   │   │       ├── image217.png
│   │   │       ├── image218.png
│   │   │       ├── image219.jpg
│   │   │       ├── image220.png
│   │   │       ├── image221.jpg
│   │   │       ├── image238.png
│   │   │       ├── image242.png
│   │   │       ├── image243.jpg
│   │   │       ├── image244.jpg
│   │   │       ├── image252.png
│   │   │       ├── image253.jpg
│   │   │       ├── image254.png
│   │   │       ├── image255.jpg
│   │   │       ├── image256.png
│   │   │       ├── image257.png
│   │   │       ├── image258.jpg
│   │   │       ├── image259.jpg
│   │   │       ├── image260.jpg
│   │   │       ├── image261.png
│   │   │       ├── image262.png
│   │   │       ├── image263.png
│   │   │       ├── image264.png
│   │   │       ├── image265.jpg
│   │   │       ├── image266.jpg
│   │   │       ├── image267.png
│   │   │       ├── image268.jpg
│   │   │       ├── image269.png
│   │   │       ├── image270.png
│   │   │       ├── image294.png
│   │   │       ├── image328.jpg
│   │   │       ├── image329.png
│   │   │       ├── image330.jpg
│   │   │       ├── image331.png
│   │   │       ├── image332.jpg
│   │   │       ├── image333.png
│   │   │       ├── image34.jpg
│   │   │       ├── image347.png
│   │   │       ├── image348.png
│   │   │       ├── image352.png
│   │   │       ├── image360.png
│   │   │       ├── image368.png
│   │   │       ├── image369.png
│   │   │       ├── image377.jpg
│   │   │       ├── image40.png
│   │   │       ├── image402.jpg
│   │   │       ├── image403.jpg
│   │   │       ├── image41.png
│   │   │       ├── image434.png
│   │   │       ├── image441.png
│   │   │       ├── image48.png
│   │   │       ├── image6.jpg
│   │   │       ├── image74.png
│   │   │       ├── image79.png
│   │   │       ├── image8.png
│   │   │       ├── knowledgebasequote.jpg
│   │   │       ├── lightbulb.png
│   │   │       ├── merriamwebster.jpg
│   │   │       ├── natashaquote.jpg
│   │   │       ├── subscribetojournal.jpg
│   │   │       ├── tobeopen.jpg
│   │   │       ├── whitehouse2022.jpg
│   │   │       └── zenodojwst.jpg
│   │   ├── readme.html
│   │   └── readme.md
│   ├── Module_2/
│   │   ├── Lesson_1/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_2/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_3/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_4/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_5/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── images/
│   │   │   └── media/
│   │   │       ├── calculatingenso.jpg
│   │   │       ├── calculatingenso2.jpg
│   │   │       ├── calculatingenso3.jpg
│   │   │       ├── calculatingenso4.jpg
│   │   │       ├── image1.jpeg
│   │   │       ├── image10.jpeg
│   │   │       ├── image11.jpeg
│   │   │       ├── image12.jpeg
│   │   │       ├── image13.jpeg
│   │   │       ├── image14.png
│   │   │       ├── image15.png
│   │   │       ├── image16.png
│   │   │       ├── image17.png
│   │   │       ├── image18.png
│   │   │       ├── image19.jpeg
│   │   │       ├── image2.png
│   │   │       ├── image20.png
│   │   │       ├── image21.png
│   │   │       ├── image22.jpeg
│   │   │       ├── image23.png
│   │   │       ├── image24.png
│   │   │       ├── image25.png
│   │   │       ├── image26.png
│   │   │       ├── image27.png
│   │   │       ├── image28.png
│   │   │       ├── image29.png
│   │   │       ├── image3.png
│   │   │       ├── image30.png
│   │   │       ├── image31.png
│   │   │       ├── image32.png
│   │   │       ├── image33.png
│   │   │       ├── image34.png
│   │   │       ├── image35.png
│   │   │       ├── image36.jpeg
│   │   │       ├── image37.png
│   │   │       ├── image38.png
│   │   │       ├── image39.jpeg
│   │   │       ├── image44.jpeg
│   │   │       ├── image45.png
│   │   │       ├── image46.png
│   │   │       ├── image47.png
│   │   │       ├── image48.png
│   │   │       ├── image49.png
│   │   │       ├── image5.png
│   │   │       ├── image50.png
│   │   │       ├── image51.jpeg
│   │   │       ├── image52.png
│   │   │       ├── image53.jpeg
│   │   │       ├── image54.png
│   │   │       ├── image55.png
│   │   │       ├── image56.png
│   │   │       ├── image57.png
│   │   │       ├── image6.png
│   │   │       ├── image7.png
│   │   │       ├── image8.png
│   │   │       ├── image9.png
│   │   │       ├── jupyterlogo.jpg
│   │   │       ├── m2orcidlogo.jpg
│   │   │       ├── osfquote.jpg
│   │   │       └── ostpquote.jpg
│   │   ├── readme.html
│   │   └── readme.md
│   ├── Module_3/
│   │   ├── Lesson_1/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_2/
│   │   │   ├── LICENSE.html
│   │   │   ├── LICENSE.md
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_3/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_4/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_5/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── images/
│   │   │   └── media/
│   │   │       ├── applylicensetoyourwork.jpg
│   │   │       ├── image1.jpeg
│   │   │       ├── image10.jpeg
│   │   │       ├── image11.png
│   │   │       ├── image12.png
│   │   │       ├── image13.png
│   │   │       ├── image14.png
│   │   │       ├── image15.png
│   │   │       ├── image16.png
│   │   │       ├── image17.png
│   │   │       ├── image18.png
│   │   │       ├── image19.jpeg
│   │   │       ├── image2.jpeg
│   │   │       ├── image20.png
│   │   │       ├── image21.png
│   │   │       ├── image22.jpeg
│   │   │       ├── image23.png
│   │   │       ├── image24.png
│   │   │       ├── image25.jpeg
│   │   │       ├── image26.png
│   │   │       ├── image27.png
│   │   │       ├── image28.png
│   │   │       ├── image29.png
│   │   │       ├── image3.jpeg
│   │   │       ├── image30.png
│   │   │       ├── image31.png
│   │   │       ├── image32.jpeg
│   │   │       ├── image33.png
│   │   │       ├── image34.jpeg
│   │   │       ├── image35.jpeg
│   │   │       ├── image36.png
│   │   │       ├── image37.png
│   │   │       ├── image38.png
│   │   │       ├── image39.png
│   │   │       ├── image4.png
│   │   │       ├── image40.png
│   │   │       ├── image41.png
│   │   │       ├── image42.png
│   │   │       ├── image43.png
│   │   │       ├── image44.png
│   │   │       ├── image45.png
│   │   │       ├── image46.png
│   │   │       ├── image47.png
│   │   │       ├── image48.png
│   │   │       ├── image49.png
│   │   │       ├── image50.png
│   │   │       ├── image51.png
│   │   │       ├── image52.png
│   │   │       ├── image53.png
│   │   │       ├── image54.png
│   │   │       ├── image55.png
│   │   │       ├── image56.png
│   │   │       ├── image6.jpeg
│   │   │       ├── image7.png
│   │   │       ├── image9.png
│   │   │       └── opendatahandbookquote.jpg
│   │   ├── readme.html
│   │   └── readme.md
│   ├── Module_4/
│   │   ├── Lesson_1/
│   │   │   ├── LICENSE.html
│   │   │   ├── LICENSE.md
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_2/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_3/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_4/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_5/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── images/
│   │   │   └── media/
│   │   │       ├── codebg.jpg
│   │   │       ├── commonsoftwarelicenses.png
│   │   │       ├── examplecoderepo1.png
│   │   │       ├── examplecoderepo2.png
│   │   │       ├── examplecoderepo3.png
│   │   │       ├── image10.png
│   │   │       ├── image109.png
│   │   │       ├── image110.jpg
│   │   │       ├── image112.png
│   │   │       ├── image119.png
│   │   │       ├── image128.jpg
│   │   │       ├── image130.png
│   │   │       ├── image14.png
│   │   │       ├── image154.png
│   │   │       ├── image167.png
│   │   │       ├── image168.jpg
│   │   │       ├── image191.png
│   │   │       ├── image197.png
│   │   │       ├── image212.png
│   │   │       ├── image213.png
│   │   │       ├── image216.png
│   │   │       ├── image227.png
│   │   │       ├── image247.jpg
│   │   │       ├── image254.png
│   │   │       ├── image281.png
│   │   │       ├── image289.png
│   │   │       ├── image290.png
│   │   │       ├── image291.jpg
│   │   │       ├── image292.png
│   │   │       ├── image293.png
│   │   │       ├── image3.png
│   │   │       ├── image302.png
│   │   │       ├── image325.png
│   │   │       ├── image331.png
│   │   │       ├── image332.png
│   │   │       ├── image333.jpg
│   │   │       ├── image334.png
│   │   │       ├── image335.jpg
│   │   │       ├── image352.png
│   │   │       ├── image353.png
│   │   │       ├── image394.jpg
│   │   │       ├── image396.png
│   │   │       ├── image399.png
│   │   │       ├── image401.png
│   │   │       ├── image408.jpg
│   │   │       ├── image418.png
│   │   │       ├── image419.png
│   │   │       ├── image425.png
│   │   │       ├── image454.png
│   │   │       ├── image455.png
│   │   │       ├── image496.jpg
│   │   │       ├── image530.png
│   │   │       ├── image531.png
│   │   │       ├── image540.png
│   │   │       ├── image553.png
│   │   │       ├── image580.png
│   │   │       ├── image607.png
│   │   │       ├── image78.jpg
│   │   │       ├── lightbulb.png
│   │   │       ├── recallsteps.jpg
│   │   │       ├── softwarerepo1.png
│   │   │       ├── softwarerepo2.png
│   │   │       ├── softwarerepo3.png
│   │   │       ├── softwarerepo4.png
│   │   │       ├── softwarerepo5.png
│   │   │       ├── softwarerepo6.png
│   │   │       ├── softwarerepo7.png
│   │   │       ├── softwarerepo8.jpg
│   │   │       ├── zenododoi1.jpg
│   │   │       ├── zenododoi10.jpg
│   │   │       ├── zenododoi3.jpg
│   │   │       ├── zenododoi6.jpg
│   │   │       └── zenododoi8.jpg
│   │   ├── readme.html
│   │   └── readme.md
│   ├── Module_5/
│   │   ├── Lesson_1/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_2/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_3/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_4/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── Lesson_5/
│   │   │   ├── readme.html
│   │   │   └── readme.md
│   │   ├── images/
│   │   │   └── media/
│   │   │       ├── image1.jpeg
│   │   │       ├── image10.jpeg
│   │   │       ├── image11.png
│   │   │       ├── image12.jpeg
│   │   │       ├── image13.jpeg
│   │   │       ├── image14.jpeg
│   │   │       ├── image15.png
│   │   │       ├── image16.jpeg
│   │   │       ├── image17.png
│   │   │       ├── image19.png
│   │   │       ├── image21.png
│   │   │       ├── image23.jpeg
│   │   │       ├── image25.png
│   │   │       ├── image26.png
│   │   │       ├── image27.png
│   │   │       ├── image28.png
│   │   │       ├── image29.png
│   │   │       ├── image3.png
│   │   │       ├── image31.png
│   │   │       ├── image32.png
│   │   │       ├── image33.png
│   │   │       ├── image34.png
│   │   │       ├── image35.png
│   │   │       ├── image36.png
│   │   │       ├── image37.png
│   │   │       ├── image38.png
│   │   │       ├── image39.png
│   │   │       ├── image4.jpeg
│   │   │       ├── image40.png
│   │   │       ├── image41.png
│   │   │       ├── image48.png
│   │   │       ├── image49.png
│   │   │       ├── image5.png
│   │   │       ├── image52.jpeg
│   │   │       ├── image53.jpeg
│   │   │       ├── image54.png
│   │   │       ├── image55.png
│   │   │       ├── image56.png
│   │   │       ├── image57.png
│   │   │       ├── image59.png
│   │   │       ├── image6.png
│   │   │       ├── image60.jpeg
│   │   │       ├── image63.jpeg
│   │   │       ├── image64.jpeg
│   │   │       ├── image67.png
│   │   │       ├── image68.jpeg
│   │   │       ├── image69.png
│   │   │       ├── image7.jpeg
│   │   │       ├── image70.png
│   │   │       ├── image71.png
│   │   │       ├── image72.png
│   │   │       ├── image73.png
│   │   │       ├── image74.jpeg
│   │   │       ├── image75.jpeg
│   │   │       ├── image76.png
│   │   │       ├── image77.png
│   │   │       ├── image78.png
│   │   │       ├── image79.png
│   │   │       ├── image8.jpeg
│   │   │       ├── image9.jpeg
│   │   │       ├── opensciencequote.jpg
│   │   │       ├── stoddenquote.jpg
│   │   │       ├── thepracticeofopen.jpg
│   │   │       └── turingwayillustration.jpg
│   │   ├── readme.html
│   │   └── readme.md
│   ├── .gitignore
│   ├── CITATION.cff
│   ├── LICENSE.html
│   ├── LICENSE.md
│   ├── NOTICE.md
│   ├── README.html
│   ├── README.md
│   ├── catalogue.html
│   ├── index.html
│   └── provenance.html
├── raw_input_stream/
│   ├── mobile_drops/
│   │   └── qwen_task_01.txt
│   └── genesis_seed.txt
├── scripts/
│   ├── bootstrap-wendy.sh*
│   ├── forge_conservatory.sh*
│   ├── provision_arch_edge.sh*
│   ├── safe-push.sh*
│   ├── wendy-dream-runner.sh*
│   ├── wendy_coordinator.sh*
│   ├── wendy_evolution_engine.py
│   ├── wendy_ipc_client.py*
│   ├── wendy_llm_query.py
│   └── wendy_self_wire.py*
├── singularity/
│   ├── index.html
│   ├── index2.html
│   ├── index3.html
│   └── index4.html
├── wendy-cortex/
│   ├── forth/
│   │   ├── bootstrap_dictionary.sh*
│   │   ├── bootstrap_go.sh*
│   │   ├── bootstrap_rust.sh*
│   │   ├── bootstrap_zig.sh
│   │   ├── connective_tissue.fth
│   │   ├── evolution.fth
│   │   ├── homoiconic_cortex.fth
│   │   ├── promote_forth.sh
│   │   └── wendy_dictionary.fth
│   ├── mesh/
│   │   ├── go.mod
│   │   ├── go.sum
│   │   └── main.go
│   ├── Cargo.toml
│   ├── RUNNERS.toml
│   └── manifest.gmi
├── .gitignore
├── .wendy_dream.gmi
├── .wendy_manifest.gmi
├── .wendy_state.json
├── AGENTS.md
├── AUTHOR.md
├── CITATION.cff
├── CNAME
├── CODEOWNERS
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── Cargo.toml
├── DISCLAIMER.md
├── LICENSE
├── NOTICE.md
├── OPEN_SCIENCE_POLICY.md
├── POLICY.md
├── PRIDE.gmi
├── README.md
├── REUSE.toml
├── SECURITY.md
├── SECURITY_PLAN.md
├── SOVEREIGN_ARCHITECTURE_LAW.md
├── TRUST_AND_PROVENANCE.md
├── WENDY_HOMOICONIC_CORTEX.md
├── codemeta.json
├── gemini_client.py
├── index.html
├── openscience.html
├── requirements-core.txt
├── requirements.txt
├── robots.txt
├── run_real_science_benchmark.py
├── sitemap.xml
└── wendy-console.html

57 directories, 497 files
```
<!-- AUTO_TREE_END -->
