# Domain-Separated Licensing Framework — Open Science & Commercial Compliance

This repository implements a strict, domain-separated licensing model designed for global open-science compliance (NASA, CSA, ESA, Horizon Europe, UNESCO) while explicitly protecting proprietary hardware intellectual property.

| Content Type | License | File Location | SPDX Identifier | Rationale & Compliance |
|---|---|---|---|---|
| **All software, code, scripts, Jekyll config, workflows, codemeta** | **EUPL 1.2** | `/LICENSE-EUPL-1.2.txt` | `EUPL-1.2` | The official open-source license of the European Commission and ESA. Provides strong copyleft protection against closed-source hijacking, while maintaining explicit compatibility with other major licenses (e.g., Apache-2.0, GPL), ensuring smooth legal approval by NASA and CSA. |
| **All documentation, papers, text, datasets, CSV, JSON, photos, images, videos, figures** | **CC BY-SA 4.0** | `/LICENSE-CC-BY-SA-4.0.md` | `CC-BY-SA-4.0` | Mandates explicit attribution and ensures derivative works remain open (ShareAlike). Aligns with NASA SPD-41, ESA Open Science Policy, CSA Open Science, and Horizon Europe MGA Art.14, while preventing proprietary enclosure of open research data. |
| **Hardware designs, patents, schematics, and physical implementations** | **All Rights Reserved** | N/A (See [w-1-n.com](https://w-1-n.com)) | N/A | Strictly proprietary. This repository contains *architectural theory only*. Future open-hardware releases, if any, will be governed by the CERN Open Hardware Licence (CERN-OHL) framework. |

---

### How to apply — for contributors

Add the following header to the top of each file you create or modify:

**Code files (`.sh`, `.yml`, `.json`, `.js`, `.py`, `.html`):**
```text
# Copyright 2026 Louis-Philippe Audette
# SPDX-License-Identifier: EUPL-1.2
# Licensed under the EUPL 1.2 — see /LICENSE-EUPL-1.2.txt
