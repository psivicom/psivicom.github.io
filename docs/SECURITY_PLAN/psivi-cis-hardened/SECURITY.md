# Security Policy — PSIVI.COM Open Science Hub

**Owner:** Louis-Philippe Audette — Goldstream, Langford, BC
**Site:** https://psivi.com / https://psivicom.github.io
**Contact:** louis@psivi.com
**Last Updated:** 2026-09-03
**Status:** Excellence Edition — NASA TOPS / SPD-41a + CIS IG1 aligned

## Our Philosophy: Open Data, Hardened Build

Open science means data and code are open (Apache-2.0 for code, CC-BY-4.0 for data/docs).
It does NOT mean the build pipeline is open to tampering. This policy implements CIS Controls v8 IG1 and CIS Benchmark principles to make the openness verifiable.

We follow:
- NASA SPD-41a & SMD Open Science Guidance — open code, open data, OSDMP, DOI archiving via Zenodo
- CIS Controls v8 IG1 — foundational cyber hygiene for open science
- CIS Benchmarks — free consensus hardening guidance (GitHub, TLS, DNS)
- NIST SSDF & SLSA L2 — secure development and supply-chain provenance

## Supported Versions

| Component | Version | Supported | Notes |
|---|---|---|---|
| psivicom.github.io main | latest commit on main | YES | Protected branch, PR-only |
| Jekyll site | 4.3.x via github-pages gem | YES | Pinned in Gemfile.lock |
| Data (CSV, images) | v2024+ | YES | Checksum in data/manifest.sha256 |
| Hardware (Open Hive Logger) | v1.0 | YES | Schematics CC-BY-4.0 |

## Reporting a Vulnerability

Do NOT open a public issue for security vulnerabilities.

1. Email: louis@psivi.com with subject [SECURITY] psivi.com
2. Or GitHub: Security tab -> Report a vulnerability (private)
3. Include: affected file/commit, reproduction, impact on data integrity

We will acknowledge within 72h. Credit given if desired.

For non-security data access: open an issue with tag data-request.

## CIS Controls Mapping

| CIS Control v8 | How we implement |
|---|---|
| 1. Inventory & 2. Software | codemeta.json, CITATION.cff, Gemfile.lock, SBOM sbom.spdx.json |
| 3. Data Protection | Dual-license Apache-2.0 / CC-BY-4.0 satisfies NASA/ESA/CSA; checksums in manifest |
| 4. Secure Config | Actions pinned by SHA, permissions: contents: read minimal, branch protection |
| 5. Account Mgmt | 2FA required, CODEOWNERS requires review for /data/ /docs/OSDMP.md |
| 7. Vuln Mgmt | Dependabot bundler + github-actions, CodeQL, secret scanning + push protection |
| 8. Audit Log | GitHub audit log + Actions logs, AI contributions logged with prompt hash |
| 13. Network | Pages enforces TLS 1.2+, HSTS; DNS CAA restricts to letsencrypt.org; DNSSEC |
| 14. Awareness | AI-assisted workflows human-reviewed per NASA TOPS |

## AI-Assisted Open Science — Human-Reviewed

This repo is built with Meta AI-assisted workflows, human-reviewed per NASA TOPS guidance. No AI content published without validation.

When AI is invited to participate (for international space agencies):

1. PR-only: AI agents may ONLY open Pull Requests, never push to main
2. Provenance: Every AI-generated file must include in PR: Input hash, Prompt hash / model version, Output hash, Validation step by human
3. Minimal privilege: Actions use persist-credentials: false, no secrets exposed
4. No hallucinated field data for Goldstream Pollinator Forage Atlas or Garry Oak phenology
5. Review gate: CODEOWNERS = @psivicom must approve changes to /data/, /docs/OSDMP.md, LICENSES/

## Hardening Checklist

- Branch protection: Require PR, 1 review, block force push
- CODEOWNERS for sensitive paths
- Dependabot for bundler + github-actions (weekly)
- CodeQL + secret scanning
- Actions pinned by SHA
- Permissions hardened: contents: read, pages: write, id-token: write
- Pages: Enforce HTTPS
- DNS: CAA 0 issue letsencrypt.org + DNSSEC + TTL 1h
- SBOM on release
- Data integrity: data/manifest.sha256 + Zenodo DOI
- SECURITY.md cross-linked (no orphan files)

## SPD-41a Note

Per NASA FAQ: GitHub alone does not satisfy archiving + persistent identifier. We enable Zenodo-GitHub integration -> Release gets DOI, linked in CITATION.cff.

## References

- CIS Benchmarks are free consensus hardening guidance
- NASA SPD-41a Scientific Information Policy
- ESA Open Science Policy, CSA Open Science, JAXA Open Science, UNESCO 41 C/22

License: docs CC-BY-4.0, code snippets Apache-2.0. See LICENSES/README.md
