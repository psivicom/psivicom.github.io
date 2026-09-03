# PSIVI.COM — CIS Hardening Pack — README

This pack adds CIS IG1 hardening to your existing Excellence Edition site without changing your open licenses.

## What you get
- SECURITY.md — NASA SPD-41a + CIS Controls v8 IG1 mapping, AI provenance policy
- .github/workflows/cis-hardened-pages.yml — SHA-pinned, minimal permissions, SBOM, CodeQL, dependency-review, Harden-Runner
- .github/dependabot.yml — weekly bundler + github-actions updates (auto-updates SHA pins)
- .github/CODEOWNERS — protects /data/, /docs/OSDMP.md, LICENSES/, SECURITY.md
- CONTRIBUTING.md — AI-invited workflow with provenance template
- scripts/generate-manifest.sh — creates data/manifest.sha256 for FAIR integrity

## Install (2 minutes)

1. Copy into your local clone of psivicom.github.io:
```
cp -r psivi-cis-harden/.github your-repo/
cp psivi-cis-harden/SECURITY.md your-repo/
cp psivi-cis-harden/CONTRIBUTING.md your-repo/
mkdir -p your-repo/scripts && cp psivi-cis-harden/scripts/* your-repo/scripts/
```

2. Enable in GitHub Settings:
- Settings → General → Pull Requests → Require PR before merging
- Settings → Branches → Add rule for `main`: Require pull request (1 review), Require status checks (build, codeql), Block force pushes
- Settings → Code security → Enable: Dependency graph, Dependabot alerts, Dependabot security updates, Secret scanning, Push protection, Private vulnerability reporting
- Settings → Pages → Enforce HTTPS

3. GoDaddy DNS → Add CAA:
Type: CAA, Host: @, Value: 0 issue "letsencrypt.org", TTL: 1 Hour
Enable DNSSEC.

4. First run:
```
chmod +x scripts/generate-manifest.sh
./scripts/generate-manifest.sh
git add data/manifest.sha256 SECURITY.md .github/ CONTRIBUTING.md scripts/
git commit -m "feat(security): add CIS IG1 hardening pack for NASA Open Science FAIR"
git push
```

5. Enable Zenodo-GitHub: login to Zenodo → GitHub → enable psivicom.github.io → Create Release v1.0.0 → DOI auto-generated → paste DOI into CITATION.cff and codemeta.json

## Why this helps international agencies

- NASA, CSA, ESA, JAXA all require: open code Apache-2.0 + open data CC-BY-4.0 + OSDMP + DOI. You already have it.
- CIS adds: verifiable build, no tampering, audit log. Agencies can trust your Goldstream pollinator data and RADARSAT fusion notebooks are reproducible.
- AI invitation: you can now say "AI may contribute PRs with provenance hashes, human-reviewed per NASA TOPS and CIS Control 14" — exactly what ESA Open Science Policy wants for AI transparency.

Questions: louis@psivi.com or open issue with tag data-request

# Added /docs/SECURITY_PLAN/psivi-cis-harden/
ToDo: README.md, CONTRIBUTING.md,SECURITY.md, /scripts/generate-manifest.sh
package files suggested by Meta Ai to harden psivi.com with open science and CIS harden security with space agencies 
