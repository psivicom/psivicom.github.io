# PSIVI.COM — Open Science Hub

**FAIR-compliant research infrastructure for environmental sensing and edge AI**

---

## Overview

PSIVI.COM is an open science platform focused on reproducible research methods and infrastructure. The core mission is to make environmental sensing research findable, accessible, interoperable, and reusable under FAIR principles.

This repository contains the documentation, code, and data workflows for multiple interconnected research aspects. All code and data follow open licensing standards. Hardware designs remain proprietary to protect intellectual property while maintaining open software and data layers.

**Primary Location:** Goldstream, Langford BC, Canada  
**License Model:** Code = EUPL 1.2 | Data/Docs = CC BY-SA 4.0 | Hardware = Proprietary

---

## Research Aspects

### Space AI & Earth Observation
- RADARSAT Constellation Mission (RCM) SAR processing for soil moisture and land cover classification
- NASA Earthdata integration: MODIS, VIIRS, Landsat 8/9, SMAP, GPM for phenology and climate context
- SAR-Optical fusion workflows for environmental change detection and monitoring
- Focus area: Coastal rainforest edge and Garry oak meadow fragments in the Goldstream watershed

### Pollinator Ecology Field Research
- Goldstream Pollinator Forage Atlas: Weekly transects mapping bloom sequences versus RADARSAT soil moisture anomalies
- Hive health monitoring systems for Langford apiaries including weight, temperature, and acoustic logging
- Focus species: Apis mellifera honeybees and native Bombus bumblebee populations in the Saanich Inlet corridor

### Edge AI — Pico Mesh Infrastructure
- Raspberry Pi Pico W multistatic mesh network for distributed on-device inference
- WiFi Channel State Information (CSI) sensing for passive environmental monitoring without cameras or cloud transmission
- Technical specifications: <1ms latency, through-wall detection up to 5 meters, sub-inch spatial accuracy with 4-6 node deployment
- Focus: Privacy-first edge computing architecture for environmental data collection

---

## Open Science Compliance

This project follows NASA’s Open Science Data Management Plan (OSDMP) template and implements all 15 FAIR sub-principles:

- **Findable**: All datasets and code have persistent identifiers and comprehensive metadata
- **Accessible**: Open licenses with clear usage terms and persistent access
- **Interoperable**: Standard data formats and controlled vocabularies throughout
- **Reusable**: Pinned environments, versioned datasets, and documented methods for full reproducibility

Complete FAIR mapping available in `/docs/FAIR-mapping.md`

---

## Repository Structure

/
├── /docs          - Documentation, methodology, and FAIR mapping
├── /licenses      - EUPL 1.2 and CC BY-SA 4.0 license files
├── /src           - Source code for space AI and edge AI components
├── /data          - Processed datasets (raw data available upon request)
├── /hardware      - Proprietary CAD/PCB designs - NOT OPEN SOURCE
├── /notebooks     - Reproducible Jupyter notebooks and analysis workflows
└── http://index.html     - GitHub Pages landing site

---

---

## Contributing

Contributions, bug reports, and feature requests are welcome. Please open an issue or submit a pull request following the guidelines in `/docs/contributing.md`.

All contributions must comply with the EUPL-1.2 license for code and CC BY-SA 4.0 for documentation and data.

---

## Citation

If you use this work in your research, please cite:

http://PSIVI.COM Open Science Hub (2024-2026). 
FAIR-compliant infrastructure for environmental sensing and edge AI. 
https://psivi.com

---

## License

**Software:** EUPL-1.2 — European Union Public License 1.2  
**Data & Documentation:** CC BY-SA 4.0 — Creative Commons Attribution-ShareAlike 4.0  
**Hardware Designs:** Proprietary — All rights reserved

Full license texts available in the `/licenses/` directory.
- Full FAIR compliance doc
# FAIR 15 Sub-Principles Mapping

## F1 - Findable
All datasets and code are assigned persistent identifiers via Zenodo DOI integration. Metadata is published in standard schema.org and Dublin Core formats.

## F2 - Accessible  
All open content is accessible via HTTPS with no authentication barriers. Metadata remains accessible even when data is embargoed.

## F3 - Interoperable
Standard formats used: GeoTIFF for raster data, CSV for tabular data, NetCDF for multi-dimensional data, JSON-LD for metadata.

## F4 - Reusable
Clear licensing via EUPL-1.2 for code and CC BY-SA 4.0 for data. Provenance is documented in all workflows.

## A1 - Accessible
Data is retrievable by identifier using standard protocols. Authentication required only for proprietary hardware documentation.

## A1.1 - Protocol
HTTP/HTTPS protocols used for all public content. API endpoints follow REST standards.

## A1.2 - Authorization
Authorization framework documented in `/docs/auth.md` for restricted data access.

## A2 - Metadata Persistence
Metadata persists beyond data lifecycle. Archived in institutional repository with 10-year retention.

## I1 - Formal Language
Data uses formal, accessible, shared, and broadly applicable languages for knowledge representation.

## I2 - Vocabularies
Standard vocabularies used: CF Conventions for climate data, Darwin Core for biodiversity data.

## I3 - References
All external data includes qualified references to source datasets and publications.

## R1 - Rich Metadata
Metadata includes detailed provenance, methodology, and processing steps.

## R1.1 - License
Explicit license information included in all dataset metadata headers.

## R1.2 - Provenance
Complete processing lineage documented from raw data to final analysis products.

## R1.3 - Standards
Community standards followed for domain-specific metadata in Earth observation and ecology.

---

## Implementation Notes

All workflows use conda environment files with pinned package versions. Data processing scripts include version control hashes for full reproducibility.
You can copy these three files directly into your repo root and  folder. The site will render correctly on GitHub Pages without any additional setup.
