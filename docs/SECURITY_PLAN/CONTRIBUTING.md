# Contributing — AI-Invited Open Science for International Agencies

Welcome! This site is built for NASA Open Science FAIR + CSA / ESA / JAXA.
We invite AI assistance, but under CIS-hardened, human-reviewed rules per NASA TOPS.

## Dual License Reminder (Excellence Edition)
- **Code** (.js, .py, .yml, .rb, .html, workflows): Apache-2.0
- **Data/Docs/Media** (.md, .csv, .jpg, .png): CC-BY-4.0
See LICENSES/README.md. No orphan files — all cross-reference each other.

## How to Contribute (Human or AI)

1. Fork → create branch `feat/your-topic`
2. Run data integrity check: `sha256sum -c data/manifest.sha256` if manifest exists
3. Open PR — fill provenance template below

### AI Agent Provenance Template (required for AI PRs)

Every AI-assisted PR MUST include:

```
AI-Model: Meta AI / Muse / etc + version
Prompt-Hash: sha256:xxxx
Input-Hash: sha256 of source data (e.g., data/forage.csv)
Output-Hash: sha256 of generated file
Validation: Human reviewed by @psivicom — checked field transect logs vs generated chart
CIS Controls: 3,4,7,14 applied
NASA TOPS: Human validation, reproducibility note
FAIR: F1,F2,A1,I1,R1.1 mapped in docs/OSDMP.md
```

Rules:
- AI may ONLY open PRs, never push to main (branch protection enforces)
- AI may NOT generate synthetic field observations for Goldstream Pollinator Forage Atlas or Garry Oak meadow phenology
- AI may generate: code, tests, docs, visualizations, Jekyll plugins, schema mappings
- No secrets in prompts, no `curl | bash`, no external network fetch in build unless allow-listed

### For Pollinator Ecology / Earth Observation Contributions

- RADARSAT RCM / Sentinel-2 / NASA HLS workflows: pin GDAL, xarray versions, add hashes
- Include DOI or Earthdata search link for any new NASA/CSA dataset used
- Update `data/manifest.sha256` after data changes:
  `find data -type f -not -name manifest.sha256 -exec sha256sum {} \; | sort > data/manifest.sha256`

### DNS / Pages Hardening (GoDaddy → GitHub Pages)

Current: A @ → 185.199.108.153, .109, .110, .111 + CNAME www → psivicom.github.io, TTL 1h

Add for CIS:
- CAA record: Type CAA, Name @, Value `0 issue "letsencrypt.org"`, TTL 1h
- Enable DNSSEC in GoDaddy → DNS Management
- Enforce HTTPS in GitHub repo Settings → Pages

### Security

See SECURITY.md — report vulnerabilities privately to louis@psivi.com
For data requests: open issue with tag `data-request`

Goldstream, Langford BC — Built for NASA Open Science FAIR + world space agencies
