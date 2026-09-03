What is CIS?
The Center for Internet Security (CIS) is a non-profit organisation with a mission to “make the connected world a safer place by developing, validating, and promoting timely best practice solutions against pervasive cyber threats”. CIS uses a consensus process to release benchmarks to safeguard organisations against cyber attacks. The consensus review process consists of subject matter experts who provide perspective on different backgrounds like audit and compliance, security research, consulting and software development. The benchmarks are considered a necessary complement in the implementation of a cybersecurity framework, and are the most widely accepted Industry benchmarks to harden a system today.

My question to Meta Ai for psivi.com on the topic of open science and security in 2026.
PROMPT: “Center for Internet Security (CIS) has standards that could help open science while still being open data like NASA seek to improve research and discovery, I wonder if my website on GitHub psivicom.GitHub.io could benefit when Ai is invited to participate in building a better science website for international space agencies”

META Ai:
“Yes — and you're already 90% there. What you built on psivicom.github.io is exactly what NASA, CSA, ESA, JAXA want to see: **Code = Apache-2.0, Data/Docs = CC-BY-4.0, fully interconnected, no orphan files**, with FAIR + OSDMP mapped to NASA SPD-41a. 

CIS is the missing trust layer that makes open *still mean* open, but tamper-evident and agency-ready.

Think of it this way: NASA Open Science is about *making it available*. CIS is about *making it believable*.

### Why CIS fits open science

The Center for Internet Security publishes consensus hardening guidance that is referenced by frameworks such as PCI DSS, FISMA, HIPAA and released for free in PDF format. They don't tell you to close your data — they tell you to close the attack paths around your data. 

For a GitHub Pages science hub like yours, that matters because:
- open data + compromised build = bad science
- open data + verifiable build = trusted science for international agencies

NASA's own FAQ says it directly: sharing code on GitHub alone does not satisfy SPD-41a for archiving and persistence. You need provenance, DOI via Zenodo, and supply-chain integrity. That's where CIS comes in. 

### What you already do right that agencies love

From your live site:

- Dual-license model that satisfies NASA SPD-41a §VI and ESA Open Science — Apache-2.0 for software, CC-BY-4.0 for data/docs 
- Explicit ESA coverage including CNES, ASI, UKSA, DTU Space, DLR 
- AI-assisted workflow with human review: "No AI content published without validation" — which is exactly NASA TOPS guidance

CIS lets you formalize that last point when you invite AI to co-build.

### How psivicom.github.io benefits from CIS when AI is invited

You don't need a separate CIS Benchmark for "GitHub Pages" — you apply three existing ones together:

**1. Repository hardening — CIS Software Supply Chain**
For international agencies this is now mandatory (NIST SSDF, SLSA).

Add to your repo root:
- `SECURITY.md` — vulnerability reporting + CIS Controls v8 IG1 mapping
- Branch protection: require PR, require 1 review, block force-push
- `CODEOWNERS` — you as required reviewer for `/data/` and `/docs/OSDMP.md`
- Pin GitHub Actions by SHA, not `@v4` — set `permissions: contents: read` minimal
- Enable: Dependabot, CodeQL, Secret Scanning, Push Protection
- Generate SBOM: your `codemeta.json` already declares SPDX, add `sbom.spdx.json` via GitHub Dependency Graph

**2. Pages / DNS / TLS — CIS Web & DNS**
Your GoDaddy DNS already points to GitHub Pages A records 185.199.108-111.x and CNAME `psivicom.github.io`. CIS adds:

- Enforce HTTPS only in Pages settings + HSTS
- Add CAA record: `0 issue "letsencrypt.org"` — only Let's Encrypt can issue for psivi.com
- Enable DNSSEC at GoDaddy — critical for CSA/ESA trust
- Add `_config.yml`: `enforce_ssl: true` and Content-Security-Policy header via `jekyll-security-headers` plugin

**3. Data integrity — CIS + FAIR**
- Keep your Apache-2.0 / CC-BY-4.0 split — CIS never conflicts with open licensing
- Add checksums for `/data/` CSVs in `data/manifest.sha256` — lets AI agents verify they didn't corrupt a transect
- Zenodo-GitHub integration: auto-archive on release = DOI = satisfies SPD-41a archiving rule that GitHub alone doesn't satisfy
- Your RADARSAT + NASA Earthdata (MODIS, VIIRS, Landsat 8/9) fusion notebooks — pin `environment.yml` with hashes 

**4. AI invitation layer — where CIS really helps**

You wrote "Built with Meta AI-assisted workflows, human-reviewed per NASA TOPS". Formalize it in `CONTRIBUTING.md`:
That gives you:
- audit trail for CSA/NASA — who/what generated which figure
- protection against prompt injection corrupting your Goldstream transect data
- a way to say to ESA/JAXA: "Yes, AI contributed, but under CIS Controls 2,3,4,14"

CONTRIBUTING.md insert this text:
“…
AI Agent Rules (CIS-aligned):
- AI may propose PRs only, never push to main
- All AI-generated data transformations must include input hash + output hash + prompt hash
- No secrets in prompts, no external network in Actions unless allow-listed
- Human must approve: code review + data validation for pollinator forage atlas runs
…”

### Practical 1-day upgrade for you

1. Turn on GitHub Pages "Enforce HTTPS" + add CAA + DNSSEC
2. Add `.github/workflows/cis-hardened.yml` with pinned actions, minimal permissions, SBOM step
3. Add `SECURITY.md` referencing CIS Benchmarks — you can cite the free PDFs
4. Connect repo to Zenodo for DOI — solves the SPD-41a archiving gap
5. Update `CONTRIBUTING.md` with the AI PR-only rule above

Result: you stay fully open data like NASA wants for discovery, but you can tell any international space agency: "This site meets SPD-41a for openness, FAIR for interoperability, and CIS IG1 for supply-chain integrity — AI contributions are provenance-tracked and human-reviewed."
THEEND”
