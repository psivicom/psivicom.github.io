# Data Management Plan (DMP) — Excellence Edition

**Architect & Principal Investigator:** Louis-Philippe Audette  
**Affiliation:** Independent Researcher, Goldstream, Langford, BC, Canada  
**Last Updated:** 2026-09-11T00:00:00.000Z  

---

## 1. Overview

This Data Management Plan (DMP) outlines the lifecycle, formatting, and licensing of all research data generated, processed, or hosted within the PSIVI.COM Open Science Hub. All data management practices are designed to strictly adhere to the **FAIR Principles** (Findable, Accessible, Interoperable, Reusable) and the open-science mandates of NASA, ESA, and CSA.

## 2. Data Licensing

- **Primary License:** All datasets, data dictionaries, metadata files, and associated documentation are licensed under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**.
- **Attribution Requirement:** Any reuse, redistribution, or derivative work must explicitly credit **Louis-Philippe Audette** (The Audette Clause) and retain the CC BY-SA 4.0 license to ensure derivative research remains open.
- **Exclusions:** This license applies *only* to data and documentation. Source code is governed by EUPL 1.2. Hardware schematics and physical IP are **All Rights Reserved** (see [w-1-n.com](https://w-1-n.com)).

## 3. Data Types & Sources

1. **Field Observations:** Pollinator monitoring, hive health metrics, and forage mapping data (Goldstream Watershed, Langford, BC).
2. **Earth Observation Data:** Processed derivatives and fusion outputs from RADARSAT Constellation Mission (RCM) SAR, Sentinel-2, and NASA Earthdata (MODIS, VIIRS, Landsat 8/9, SMAP, GPM).
3. **Telemetry & Logs:** Synthetic or anonymized MoE cluster telemetry, anomaly logs, and Tokens-Per-Watt metrics for architectural validation.

## 4. File Formats & Interoperability

To ensure long-term accessibility and machine-readability, data is stored in open, non-proprietary formats:
- **Tabular Data:** `.csv` (Comma-Separated Values) with accompanying `datapackage.json` or `metadata.json` dictionaries.
- **Configuration & Metadata:** `.yml`, `.json` (UTF-8 encoded).
- **Documentation:** `.md` (Markdown).
- **Geospatial:** Standardized formats compatible with GDAL/xarray workflows (e.g., GeoTIFF, NetCDF, where applicable).

## 5. Data Lifecycle & Archival

1. **Collection & Processing:** Data is collected, cleaned, and processed using version-controlled, open-source scripts (licensed under EUPL 1.2).
2. **Validation:** Data undergoes automated and human review to ensure quality, FAIR compliance, and adherence to the Open Science Policy.
3. **Archival:** Finalized datasets and major research milestones are deposited in **Zenodo** and/or the **Open Science Framework (OSF)** to receive a permanent, citable **DOI**.
4. **Access:** All archived data is openly accessible by default, with no embargo periods, unless specific privacy or security constraints apply (e.g., precise GPS coordinates of sensitive ecological sites, which may be intentionally blurred).

## 6. Compliance Cross-Reference

- For overarching research policies, see: [OPEN_SCIENCE_POLICY.md](OPEN_SCIENCE_POLICY.md)
- For licensing legalities, see: [LICENSE_COMPLIANCE.md](LICENSE_COMPLIANCE.md)
- For FAIR validation checklists, see: [FAIR_CHECKLIST.md](FAIR_CHECKLIST.md)
