# Changelog — Excellence Edition

## Timestamps Template for keeping records 
## of committed changes to keep compliance — 
## Here is a Copy to use for new entries:

```
### YYYY-MM-DDTHH:MM:SS.sssZ - author - scope
- Added WORD: NAME ( stack -- effect ) DEF: : NAME ... ; TEST: ...
- Changed: ...
- Fixed: ...
- Removed: ...
```

Rules:
- Always Zulu (Z) to the milliseconds
  YYYY-MM-DDTHH:MM:SS.sssZ
- One entry per commit
- Link to WORD definition
- Include TEST


## 1.1.0 — 2026-08-29T00:00:00.000Z — Excellence — Apache-2.0 + CC-BY-4.0 Interconnected

- Migrated code license from MIT to **Apache-2.0** per author request — full Apache 2.0 text in LICENSE and LICENSES/APACHE-2.0.txt
- Kept **CC-BY-4.0** for all docs, data, datasets, photos, images, videos, figures — LICENSES/CC-BY-4.0.txt
- Added LICENSES/README.md explaining dual model for NASA/ESA/CSA/JAXA/Horizon Europe/UNESCO — interconnected with README, docs/LICENSE_COMPLIANCE.md
- Added NOTICE file with attributions
- Rewrote README.md with dual license table, repository structure diagram, no orphan files
- Rewrote CITATION.cff to state dual license message, links to docs
- Expanded codemeta.json with hasPart linking code vs data licenses, relatedLink to compliance doc
- Expanded _config.yml with license metadata, defaults for data vs code
- Added docs/LICENSE_COMPLIANCE.md (new), docs/DATA_MANAGEMENT.md (new), docs/INTEROPERABILITY.md (new)
- Added data/ with README, sample-pollinator-data/data.csv (CC-BY-4.0), datapackage.json (Frictionless), metadata.json (schema.org)
- Added data/images/README.md for media CC-BY-4.0
- Added .github/workflows/fair-check.yml (Apache-2.0) to validate FAIR files
- Added CODEOWNERS, .gitattributes, .github/FUNDING.yml
- All files cross-linked — fixes "files with no connections and little contents"

## 1.0.0 — 2026-08-28T00:00:00.000Z — Initial FAIR
- Initial OSDMP, README, MIT + CC-BY-4.0

# Changelog — PSIVI.COM

All notable changes to this project will be documented in this file.
Timestamps in NASA Open Science Standard: YYYY-MM-DDTHH:MM:SSZ

### 2026-09-01T19:24:11.000Z - reviewed by Louis-Philippe Audette
- Added WORD: AVG10 ( -- avg ) DEF: : AVG10 10 0 DO I + LOOP 10 / ; TEST: 10 AVG10 .s EXPECTS 4.5
- Fixed: README.md Last updated: 2026-05-11T00:00:00.000Z
- Docs: Migrated all timestamps to RFC3339 Zulu + milliseconds 


