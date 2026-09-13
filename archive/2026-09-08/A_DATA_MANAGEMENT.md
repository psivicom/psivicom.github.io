# Data Management — CC-BY-4.0 — Excellence

**License:** This doc CC-BY-4.0 — see LICENSES/CC-BY-4.0.txt
**Code that manages data:** Apache-2.0 — see LICENSE
**Related:** docs/OSDMP.md, data/README.md, LICENSES/README.md, docs/LICENSE_COMPLIANCE.md

All datasets, photos, images, videos, figures in this repo are **CC-BY-4.0** per NASA SPD-41a and ESA Open Science.

### Data lifecycle

1. **Collection:** Example pollinator data — data/sample-pollinator-data/data.csv — CC-BY-4.0, with consent, no personal data
2. **Processing:** Scripts would be Apache-2.0 (code) — data remains CC-BY-4.0
3. **Documentation:** datapackage.json (Frictionless) + metadata.json (schema.org) — both CC-BY-4.0
4. **Storage:** GitHub + Zenodo archive — see .zenodo.json
5. **Sharing:** CC-BY-4.0 with attribution to Louis-Philippe Audette — https://psivi.com
6. **Preservation:** 10+ years — Zenodo, OSF, psivi.com mirror

### Data types and licenses

| Path | Type | License | Why |
|---|---|---|---|
| data/sample-pollinator-data/data.csv | Dataset CSV | CC-BY-4.0 | Open data must be CC-BY-4.0 per NASA |
| data/sample-pollinator-data/datapackage.json | Metadata | CC-BY-4.0 | Frictionless metadata |
| data/sample-pollinator-data/metadata.json | Metadata | CC-BY-4.0 | schema.org |
| data/images/* | Photos, images, videos, figures | CC-BY-4.0 | NASA requires CC-BY-4.0 for media — see data/images/README.md |
| docs/*.md | Documentation | CC-BY-4.0 | Docs are CC-BY-4.0 |

All data files include SPDX header: `SPDX-License-Identifier: CC-BY-4.0`

### Attribution

When reusing data/media: Cite "Louis-Philippe Audette — psivi.com — psivicom.github.io — CC-BY-4.0" and include link to LICENSES/CC-BY-4.0.txt — see data/README.md

See also: docs/OSDMP.md §1, LICENSES/README.md
