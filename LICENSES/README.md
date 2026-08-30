# Dual License — Excellence Compliance for NASA + Space Partners

This repository implements the NASA-recommended dual-licensing model required by SPD-41a, NASA TOPS, CSA, ESA, Horizon Europe, UNESCO.

| Content Type | License | File | SPDX | Why |
|---|---|---|---|---|
| **All software, code, scripts, Jekyll config, workflows, codemeta** | Apache-2.0 | /LICENSE + LICENSES/APACHE-2.0.txt | Apache-2.0 | NASA TOPS lists Apache-2.0 as compliant permissive license; includes explicit patent grant Clause 3, preferred by ESA for flight software |
| **All documentation, OSDMP, papers, text, datasets, CSV, JSON, photos, images, videos, figures, blog posts** | CC-BY-4.0 | LICENSES/CC-BY-4.0.txt | CC-BY-4.0 | NASA SPD-41a requires open data with CC-BY-4.0 / CC0; ESA Open Science Policy, CSA Open Science, Horizon Europe MGA Art.14, UNESCO 41 C/22 all require CC-BY-4.0 for non-code |

### How to apply — for contributors

Add header to each file:

**Code files (.yml, .json, .js, .py, .html):**
```
// Copyright 2026 Louis-Philippe Audette
// SPDX-License-Identifier: Apache-2.0
// Licensed under Apache-2.0 — see /LICENSE
```

**Data/docs/media (.md, .csv, .json data, .jpg, .png, .mp4):**
```
Copyright 2026 Louis-Philippe Audette
SPDX-License-Identifier: CC-BY-4.0
Licensed under CC-BY-4.0 — see LICENSES/CC-BY-4.0.txt
Attribution: https://psivi.com
```

### Compliance matrix — verified

- NASA TOPS / SPD-41a §VI.A: Software: OSI-approved (Apache-2.0) ✓ Data: CC-BY-4.0 ✓
- CSA: Open Science Policy: Apache-2.0 + CC-BY-4.0 ✓
- ESA Open Science Policy: Allows Apache-2.0 for code, CC-BY-4.0 for data/products ✓ (covers CNES-FR, ASI-IT, UKSA-UK, DTU Space-DK, DLR-DE)
- JAXA Open Science: Apache-2.0 + CC-BY-4.0 accepted
- Horizon Europe MGA Art.14 & 17: Code must be open source (Apache-2.0 OK), data CC-BY-4.0 / CC0 required ✓
- UNESCO 41 C/22: Open licenses required ✓

### For reuse — what you must do

1. Keep /LICENSE and /LICENSES/ folders
2. Give attribution: "Louis-Philippe Audette — psivi.com — psivicom.github.io"
3. Include link to licenses
4. State changes if modified

Contact: https://psivi.com
