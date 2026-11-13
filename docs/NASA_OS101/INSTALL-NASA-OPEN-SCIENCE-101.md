# Installing a Verified Open Science Archive

**Worked example: `psivicom/psivicom.github.io` → https://psivi.com/nasa-open-science/**

This guide reproduces a cryptographically pinned, legally compliant mirror of the
NASA TOPS Open Science 101 curriculum on your own GitHub Pages site. Everything runs
from the GitHub web interface — **no terminal required**.

Author of this guide and of the local packaging: Louis-Philippe Audette | PSIVI.COM
Guide text: CC BY-SA 4.0 · Workflow code: EUPL 1.2 · Upstream curriculum: CC BY 4.0

---

## 0. What you get

| Result | Detail |
|---|---|
| Verified mirror | 400+ upstream files, byte-for-byte identical to the Zenodo DOI |
| Public website | Klein-blue landing page, descriptive catalogue, provenance map |
| Readable lessons | Every `.md` rendered to HTML with an attribution banner |
| Legal compliance | `NOTICE.md`, `CITATION.cff`, `REUSE.toml` annotation |
| Tamper evidence | SHA-256 per file + CI guard that fails on any upstream edit |
| One-click download | ZIP served directly by Zenodo (CERN) — no repo bloat |

**Pinned source (do not substitute):**

- Version DOI: `10.5281/zenodo.10161527` (immutable, v1.0.0, published 2023-12-06)
- Concept DOI: `10.5281/zenodo.10161526` (always latest — never pin to this)
- File: `open-science-101-v-1-0-0.zip` · `23311809` bytes
- MD5: `ecde9587a3c95be40eb0eb3cfa083ea5`
- License: CC BY 4.0

---

## 1. Requirements

1. A **public** GitHub repository (GitHub Pages on the free plan requires public).
2. Pages enabled: **Settings → Pages → Build and deployment → Deploy from a branch → `main` → `/ (root)`**.
3. Workflow write access: **Settings → Actions → General → Workflow permissions → Read and write permissions**.
4. Nothing installed locally. The runner installs `pandoc` itself.

---

## 2. File inventory — what you create vs what is generated

### You create (5 files)

| # | Relative path | Purpose |
|---|---|---|
| 1 | `REUSE.toml` | Machine-readable licence boundaries |
| 2 | `NOTICE.md` | Repo-wide human-readable attribution |
| 3 | `.nojekyll` | Empty file — makes Pages serve dot-folders verbatim |
| 4 | `.github/workflows/vendor-nasa-os101.yml` | The builder |
| 5 | `.github/workflows/verify-os101.yml` | The CI guard |

### The builder generates (never edit by hand)

| Relative path | Tier | Author |
|---|---|---|
| `nasa-open-science/Module_1..5/**` | A · upstream | NASA TOPS team |
| `nasa-open-science/README.md`, `LICENSE.md`, images | A · upstream | NASA TOPS team |
| `nasa-open-science/**/*.html` (beside each `.md`) | B · render | text NASA, banner you |
| `nasa-open-science/index.html` | C · local | you |
| `nasa-open-science/catalogue.html` | C · local | you |
| `nasa-open-science/provenance.html` | C · local | you |
| `nasa-open-science/NOTICE.md` | C · local | you |
| `nasa-open-science/CITATION.cff` | C · local | you |
| `.provenance/nasa-os101/manifest.sha256` | C · local | you |
| `.provenance/nasa-os101/record.json` | C · local | you |
| `.provenance/nasa-os101/provenance.json` | C · local | you |
| `.provenance/nasa-os101/local-additions.txt` | C · local | you |

> `nasa-open-science/` is **machine-managed**. Re-running the builder deletes and
> rebuilds it. Your own adaptations belong in a sibling folder, e.g.
> `nasa-open-science-apiary/`.

---

## 3. Step 1 — `REUSE.toml`

**Create this BEFORE running the builder.** The builder only appends its annotation
if `REUSE.toml` already exists; otherwise it silently skips it.

```toml
version = 1

# --- Your own documentation and data -------------------------------------
[[annotations]]
path = ["docs/**", "**.md"]
precedence = "aggregate"
SPDX-FileCopyrightText = "2026 Your Name"
SPDX-License-Identifier = "CC-BY-SA-4.0"

# --- Your own code, scripts and workflows --------------------------------
[[annotations]]
path = ["scripts/**", ".github/workflows/**", "**.py", "**.sh", "**.html"]
precedence = "aggregate"
SPDX-FileCopyrightText = "2026 Your Name"
SPDX-License-Identifier = "EUPL-1.2"

# --- Vendored upstream archive (the builder appends this if missing) ------
[[annotations]]
path = "nasa-open-science/**"
precedence = "override"
SPDX-FileCopyrightText = "2023 NASA TOPS Open Science 101 Curriculum Development Team"
SPDX-License-Identifier = "CC-BY-4.0"
```

**Two rules:**

- Keep the last block's path in the exact string form `path = "nasa-open-science/**"`.
  The builder searches for that literal line to stay idempotent; a list form
  (`path = [...]`) would cause a duplicate append.
- `precedence = "override"` is what legally fences the archive off from your
  repo-wide CC BY-SA / EUPL defaults.

**Licence texts.** REUSE expects full texts under `LICENSES/` named by SPDX ID:

```
LICENSES/CC-BY-4.0.txt      ← https://creativecommons.org/licenses/by/4.0/legalcode.txt
LICENSES/CC-BY-SA-4.0.txt   ← https://creativecommons.org/licenses/by-sa/4.0/legalcode.txt
LICENSES/EUPL-1.2.txt       ← https://spdx.org/licenses/EUPL-1.2.html
```

The upstream archive also ships its own `nasa-open-science/LICENSE.md` — leave it untouched.

---

## 4. Step 2 — root `NOTICE.md`

The archive gets its own generated `NOTICE.md`. This root one covers the whole repo.

```markdown
# NOTICE

Copyright (c) 2026 Your Name | yourdomain.example

## Domain-separated licensing
- Software, scripts, workflows, HTML: EUPL 1.2 — see LICENSES/EUPL-1.2.txt
- Documentation, data, figures: CC BY-SA 4.0 — see LICENSES/CC-BY-SA-4.0.txt
- Vendored third-party material: original licence, see REUSE.toml

## Vendored archive: NASA TOPS Open Science 101
- Path: nasa-open-science/
- Author: NASA TOPS Open Science 101 Curriculum Development Team (2023)
- Source: https://doi.org/10.5281/zenodo.10161527 (version DOI, immutable)
- Licence: CC BY 4.0
- Status: unmodified upstream payload; HTML renders are format-only conversions
- Local additions (index, catalogue, provenance, metadata) are by Your Name
- This project is not endorsed by, or affiliated with, NASA.

See nasa-open-science/NOTICE.md and .provenance/nasa-os101/ for the full
provenance record and per-file SHA-256 hashes.
```

---

## 5. Step 3 — `.nojekyll`

Create an **empty** file named `.nojekyll` at the repository root.

Why: Jekyll (the Pages default) skips dot-folders, so `.provenance/` would not be
published and the manifest links on your pages would 404. This file makes Pages
serve every file verbatim.

---

## 6. Step 4 — the builder workflow

**Relative path: `.github/workflows/vendor-nasa-os101.yml`**

Design notes for maintainers:
- All build logic is Python carried inside a YAML `env` string. **Do not reintroduce
  bash heredocs** — they caused `Invalid workflow file` and `here-document ... wanted 'TPL'`.
- The pin is checked twice: against the live Zenodo API *and* against hardcoded constants.
- Extraction is zip-slip guarded; the install is a clean rebuild.

```yaml
name: Vendor NASA OS101 (Web-Based Build)

on:
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: vendor-os101
  cancel-in-progress: false

jobs:
  build-and-commit:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Install pandoc
        run: |
          sudo apt-get update
          sudo apt-get install -y pandoc

      - name: Build verified archive
        env:
          BUILDER_PY: |
            import hashlib, html, json, re, shutil, subprocess, sys, time, urllib.request, zipfile
            from datetime import datetime, timezone
            from pathlib import Path

            REC_ID   = "10161527"
            DOI      = "10.5281/zenodo." + REC_ID
            API      = "https://zenodo.org/api/records/" + REC_ID
            ZIP_NAME = "open-science-101-v-1-0-0.zip"
            PIN_MD5  = "ecde9587a3c95be40eb0eb3cfa083ea5"
            PIN_SIZE = 23311809
            DEST     = Path("nasa-open-science")
            PROV     = Path(".provenance/nasa-os101")
            DOI_URL  = "https://doi.org/" + DOI
            ZIP_URL  = "https://zenodo.org/records/" + REC_ID + "/files/" + ZIP_NAME + "?download=1"
            TREE     = "https://github.com/psivicom/psivicom.github.io/tree/main/nasa-open-science"
            TEAM     = "NASA TOPS Open Science 101 Curriculum Development Team"
            AUTHOR   = "Louis-Philippe Audette"
            BASE     = "/nasa-open-science/"

            def stamp():
                n = datetime.now(timezone.utc)
                return n.strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (n.microsecond // 1000)

            def log(m):
                print("[" + stamp() + "] " + m, flush=True)

            def die(m):
                log("FATAL: " + m)
                sys.exit(1)

            def fetch(url, out):
                for i in range(1, 6):
                    try:
                        req = urllib.request.Request(url, headers={"User-Agent": "psivi-os101-vendor"})
                        with urllib.request.urlopen(req, timeout=180) as r:
                            with open(out, "wb") as f:
                                shutil.copyfileobj(r, f)
                        return
                    except Exception as e:
                        log("WARN fetch attempt %d/5: %s" % (i, e))
                        time.sleep(5 * i)
                die("download failed: " + url)

            STAMP = stamp()
            TMP = Path("os101_tmp")
            if TMP.exists():
                shutil.rmtree(TMP)
            TMP.mkdir()

            log("Querying Zenodo API")
            fetch(API, TMP / "record.json")
            rec = json.loads((TMP / "record.json").read_text(encoding="utf-8"))
            f0 = rec["files"][0]
            if f0["key"] != ZIP_NAME:
                die("API filename drift: " + f0["key"])
            if f0["checksum"].replace("md5:", "") != PIN_MD5:
                die("API checksum differs from pin")
            if int(f0["size"]) != PIN_SIZE:
                die("API size differs from pin")
            log("Pin confirmed by API")

            log("Downloading pinned archive")
            fetch(f0["links"]["self"], TMP / ZIP_NAME)
            blob = (TMP / ZIP_NAME).read_bytes()
            if len(blob) != PIN_SIZE:
                die("size mismatch")
            if hashlib.md5(blob).hexdigest() != PIN_MD5:
                die("MD5 mismatch")
            SHA = hashlib.sha256(blob).hexdigest()
            log("Cryptographic verification passed sha256=" + SHA)

            log("Extracting (zip-slip guarded)")
            X = TMP / "x"
            with zipfile.ZipFile(TMP / ZIP_NAME) as z:
                for n in z.namelist():
                    if n.startswith("/") or ".." in n.replace("\\", "/").split("/"):
                        die("path traversal: " + n)
                z.extractall(X)
            roots = list(X.iterdir())
            SRC = roots[0] if len(roots) == 1 and roots[0].is_dir() else X
            if not (SRC / "LICENSE.md").exists():
                die("upstream LICENSE.md missing")

            if DEST.exists():
                log("Clean rebuild of machine-managed mirror")
                shutil.rmtree(DEST)
            shutil.copytree(SRC, DEST)

            UP = sorted(p.relative_to(DEST).as_posix() for p in DEST.rglob("*") if p.is_file())
            PROV.mkdir(parents=True, exist_ok=True)
            rows = []
            for rel in UP:
                rows.append(hashlib.sha256((DEST / rel).read_bytes()).hexdigest() + "  " + rel)
            (PROV / "manifest.sha256").write_text("\n".join(rows) + "\n", encoding="utf-8")
            shutil.copyfile(TMP / "record.json", PROV / "record.json")
            log("Upstream payload installed: " + str(len(UP)) + " unmodified files hashed")

            def read(p):
                return p.read_text(encoding="utf-8", errors="replace")

            def title_of(p):
                for line in read(p).splitlines():
                    if line.startswith("# "):
                        return line[2:].strip()
                return p.parent.name.replace("_", " ")

            def overview_of(p):
                txt = read(p)
                m = re.search(r"^##\s+Overview\s*$(.*?)(?=^##\s|\Z)", txt, re.S | re.M)
                block = m.group(1) if m else txt
                block = re.sub(r"```.*?```", " ", block, flags=re.S)
                block = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", block)
                block = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", block)
                block = re.sub(r"<[^>]+>", " ", block)
                paras = []
                for q in block.split("\n\n"):
                    q = q.strip()
                    if q and q[0] not in "*-#|<>":
                        paras.append(q)
                if not paras:
                    return ""
                s = " ".join(paras[0].split())
                if len(s) > 260:
                    s = s[:260].rsplit(" ", 1)[0] + "..."
                return s

            CSS = (
                "@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Serif:ital,wght@0,400;0,600;1,400&display=swap');"
                ":root{font-family:'IBM Plex Serif',Georgia,serif}"
                ".mono{font-family:'IBM Plex Mono',monospace}"
                "body{margin:0;background:#f6f9ff;color:#18181b;line-height:1.7;-webkit-font-smoothing:antialiased}"
                "body::before{content:'';position:fixed;inset:0;z-index:-1;background:radial-gradient(1200px 600px at 20% -10%,#dbeafe 0%,transparent 60%),radial-gradient(800px 400px at 90% 10%,#e0e7ff 0%,transparent 50%);pointer-events:none}"
                "a{color:inherit;text-underline-offset:3px}a:hover{text-decoration-thickness:2px}"
                ".topbar{background:#0A1931;color:#00D4FF;text-align:center;padding:9px 12px;font-size:12px;letter-spacing:.05em;border-bottom:1px solid #00D4FF33}"
                ".container{max-width:900px;margin:0 auto;padding:24px 24px 64px;background:#fff;border-radius:0 0 16px 16px;box-shadow:0 10px 40px #0A193133,0 1px 0 #e4e4e7}"
                ".header{border-bottom:1px solid #e4e4e7;padding-bottom:32px}"
                ".kicker{font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:#71717a;font-weight:500}"
                ".h1{font-size:42px;line-height:.95;letter-spacing:-.02em;font-weight:600;margin:12px 0 0}"
                "@media(max-width:640px){.h1{font-size:32px}}"
                ".sub{margin-top:12px;font-size:13px;color:#52525b;line-height:1.6}"
                ".nav{display:flex;flex-wrap:wrap;gap:8px;margin-top:28px;font-size:11.5px;letter-spacing:.05em;text-transform:uppercase}"
                ".nav a{border:1px solid #e4e4e7;border-radius:9999px;padding:6px 14px;text-decoration:none}"
                ".nav a:hover{border-color:#002FA7;background:#002FA7;color:#fff}"
                ".section{margin-top:56px;scroll-margin-top:60px}"
                ".section-head{display:flex;align-items:center;gap:16px}"
                ".section-head h2{font-family:'IBM Plex Mono',monospace;font-size:12px;letter-spacing:.18em;text-transform:uppercase;font-weight:500;color:#71717a;margin:0;line-height:1.4}"
                ".line{flex:1;height:1px;background:linear-gradient(90deg,#0A1931,#00D4FF,#00FF9D);opacity:.5}"
                "h3{font-size:16px;font-weight:600;line-height:1.4;color:#18181b;margin:0 0 8px}"
                ".card{border:1px solid #e4e4e7;border-radius:12px;padding:20px;background:#fff;overflow-wrap:break-word}"
                ".klein-box{background:#002FA7;color:#fff;border-radius:12px;padding:24px;box-shadow:0 8px 24px rgba(0,47,167,.2);overflow-wrap:break-word}"
                ".klein-box-full{background:#002FA7;color:#fff;border-radius:12px;padding:32px;box-shadow:0 8px 24px rgba(0,47,167,.2);overflow-wrap:break-word}"
                ".label{font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:rgba(255,255,255,.75);font-family:'IBM Plex Mono',monospace;margin-bottom:8px}"
                ".value{font-size:26px;font-weight:600;letter-spacing:-.02em;margin-bottom:14px;color:#fff;line-height:1.2}"
                ".desc{font-size:14.5px;line-height:1.6;color:rgba(255,255,255,.9)}"
                ".klein-box a,.klein-box-full a{color:#fff}"
                ".grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px}"
                "@media(max-width:768px){.grid2{grid-template-columns:1fr}}"
                ".tag{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;padding:3px 9px;border-radius:9999px;margin-bottom:10px}"
                ".tag-up{background:#0B3D91;color:#fff}"
                ".tag-render{background:#e0e7ff;color:#0B3D91;border:1px solid #c7d2fe}"
                ".tag-local{background:#002FA7;color:#fff}"
                ".ok{color:#00FF9D;font-weight:600}"
                ". hashes{font-size:11.5px;word-break:break-all}"
                "code,.hashes{font-family:'IBM Plex Mono',monospace}"
                ".hashbox{background:rgba(255,255,255,.12);border-radius:8px;padding:10px 12px;margin-top:12px;font-size:11.5px;word-break:break-all;line-height:1.8}"
                "table{width:100%;border-collapse:collapse;font-size:12.5px}"
                "th{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:#71717a;font-weight:500;text-align:left;background:#fafafa;border-bottom:1px solid #e4e4e7;padding:12px 14px}"
                "td{padding:12px 14px;border-bottom:1px solid #f4f4f5;vertical-align:top}"
                ".tablewrap{overflow:hidden;border:1px solid #e4e4e7;border-radius:12px;margin-top:20px}"
                ".lesson{border-left:2px solid #002FA7;padding-left:18px;margin-bottom:22px}"
                ".lesson .meta{font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:#71717a;text-transform:uppercase;letter-spacing:.08em;margin-top:4px}"
                ".lesson p{font-size:14.5px;color:#3f3f46;margin:8px 0 6px}"
                ".lesson a{font-size:12px;font-family:'IBM Plex Mono',monospace}"
                ".pill{display:inline-block;border:1px solid #e4e4e7;border-radius:9999px;padding:7px 16px;text-decoration:none;font-size:12px;font-family:'IBM Plex Mono',monospace;margin:4px 6px 4px 0}"
                ".pill.primary{background:#002FA7;border-color:#002FA7;color:#fff}"
                ".pill:hover{border-color:#002FA7}"
                "img{max-width:100%}pre{background:#fafafa;border:1px solid #e4e4e7;border-radius:8px;padding:12px;overflow-x:auto;font-size:11.5px}"
                "footer{margin-top:48px;border-top:1px solid #e4e4e7;padding-top:28px;font-size:11px;color:#71717a;line-height:1.7}"
            ).replace(". hashes", ".hashes")

            NAV = (
                '<nav class="nav mono">'
                '<a href="' + BASE + 'index.html">Archive home</a>'
                '<a href="' + BASE + 'README.html">Course overview</a>'
                '<a href="' + BASE + 'catalogue.html">Catalogue</a>'
                '<a href="' + BASE + 'provenance.html">Upstream vs local</a>'
                '<a href="' + ZIP_URL + '">Download .zip</a>'
                '<a href="https://psivi.com/">PSIVI hub</a>'
                "</nav>"
            )
            FOOTER = (
                "<footer>Upstream text &copy; 2023 " + TEAM + " &mdash; CC BY 4.0 &mdash; "
                '<a href="' + DOI_URL + '">' + DOI + "</a>.<br>"
                "Local pages, HTML renders, provenance and packaging &copy; 2026 " + AUTHOR + " | PSIVI.COM "
                "&mdash; code EUPL 1.2, text CC BY-SA 4.0.<br>"
                "Retrieved " + STAMP + " &middot; Not endorsed by NASA.</footer>"
            )

            def page(title, kicker, h1, sub, body, badge):
                return (
                    '<!DOCTYPE html>\n<html lang="en-CA">\n<head>\n<meta charset="UTF-8">\n'
                    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                    "<title>" + html.escape(title) + "</title>\n<style>" + CSS + "</style>\n</head>\n<body>\n"
                    '<div class="topbar mono">PSIVI.COM &mdash; OPEN SCIENCE ARCHIVE &mdash; ' + badge + "</div>\n"
                    '<div class="container">\n<header class="header">\n'
                    '<div class="kicker mono">' + kicker + "</div>\n"
                    '<h1 class="h1">' + h1 + "</h1>\n"
                    '<div class="sub">' + sub + "</div>\n" + NAV + "\n</header>\n<main>" + body + "</main>\n" + FOOTER + "\n</div>\n</body>\n</html>\n"
                )

            def head(num, text):
                return ('<section class="section"><div class="section-head"><h2 class="mono">' + num +
                        " &mdash; " + text + '</h2><div class="line"></div></div>')

            TPL = TMP / "tpl.html"
            TPL.write_text(
                '<!DOCTYPE html>\n<html lang="en-CA">\n<head>\n<meta charset="UTF-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                "<title>$title$</title>\n<style>" + CSS + "</style>\n</head>\n<body>\n"
                '<div class="topbar mono">PSIVI.COM &mdash; OPEN SCIENCE ARCHIVE &mdash; UPSTREAM MIRROR</div>\n'
                '<div class="container">\n'
                '<div class="card" style="margin-top:24px;border-left:4px solid #0B3D91">'
                '<span class="tag tag-up">Upstream &middot; unmodified text</span>'
                '<span class="tag tag-render">Format-only render</span>'
                "<p style=\"font-size:13.5px;color:#3f3f46;margin:6px 0 0\">"
                "Written by <strong>" + TEAM + "</strong> (2023), licensed <strong>CC BY 4.0</strong>, "
                'retrieved from <a href="' + DOI_URL + '">Zenodo ' + DOI + "</a>.<br>"
                "<strong>Local change:</strong> file format converted Markdown &rarr; HTML and this banner added by "
                + AUTHOR + ". <em>No wording, figure or data was altered.</em></p>"
                '<div class="hashes" style="margin-top:10px;color:#71717a">MD5 ' + PIN_MD5 +
                "<br>SHA-256 " + SHA + "<br>Retrieved " + STAMP + "</div>"
                '<p style="margin:12px 0 0"><a class="pill" href="' + BASE + 'index.html">Archive home</a>'
                '<a class="pill" href="' + BASE + 'provenance.html">What is upstream vs local</a></p>'
                "</div>\n"
                '<main class="section">$body$</main>\n' + FOOTER + "\n</div>\n</body>\n</html>\n",
                encoding="utf-8")

            mds = [p for p in sorted(DEST.rglob("*.md")) if p.name != "NOTICE.md"]
            for p in mds:
                r = subprocess.run(
                    ["pandoc", str(p), "-f", "gfm", "-t", "html5", "-s",
                     "--template", str(TPL.resolve()),
                     "--metadata", "title=" + title_of(p),
                     "-o", str(p.with_suffix(".html"))],
                    capture_output=True, text=True)
                if r.returncode != 0:
                    die("pandoc failed on " + str(p) + ": " + r.stderr.strip())
            log("Rendered " + str(len(mds)) + " upstream pages (format-only)")

            modules = []
            for m in sorted(DEST.glob("Module_*")):
                if not m.is_dir():
                    continue
                mdesc = overview_of(m / "readme.md") if (m / "readme.md").exists() else ""
                lessons = []
                for l in sorted(m.glob("Lesson_*")):
                    if not l.is_dir():
                        continue
                    md = l / "readme.md"
                    lessons.append({
                        "name": l.name.replace("_", " "),
                        "title": title_of(md) if md.exists() else l.name,
                        "desc": overview_of(md) if md.exists() else "",
                        "html": l.relative_to(DEST).as_posix() + "/readme.html",
                        "md": l.relative_to(DEST).as_posix() + "/readme.md"})
                modules.append({"name": m.name.replace("_", " "), "desc": mdesc, "lessons": lessons})

            def lesson_blocks(rel_prefix):
                out = []
                for mod in modules:
                    out.append('<div class="card" style="margin-top:20px"><h3>' + html.escape(mod["name"]) + "</h3>")
                    if mod["desc"]:
                        out.append('<p style="font-size:14px;color:#52525b;margin:0 0 16px">' + html.escape(mod["desc"]) + "</p>")
                    for ls in mod["lessons"]:
                        out.append('<div class="lesson"><strong>' + html.escape(ls["title"]) + "</strong>"
                                   '<div class="meta">' + html.escape(ls["name"]) + " &middot; upstream &middot; CC BY 4.0</div>")
                        if ls["desc"]:
                            out.append("<p>" + html.escape(ls["desc"]) + "</p>")
                        out.append('<a href="' + rel_prefix + ls["html"] + '">Read lesson &rarr;</a> &nbsp; '
                                   '<a href="' + rel_prefix + ls["md"] + '">source .md</a></div>')
                    out.append("</div>")
                return "".join(out)

            verify_box = (
                '<div class="klein-box-full" style="margin-top:24px">'
                '<div class="label">Cryptographic provenance</div>'
                '<div class="value"><span class="ok">&#10003;</span> Verified &middot; pinned v1.0.0</div>'
                '<div class="desc">Byte-for-byte identical to the immutable Zenodo version DOI '
                '<a href="' + DOI_URL + '">' + DOI + "</a>, published 2023-12-06 by " + TEAM + ".</div>"
                '<div class="hashbox mono">ARCHIVE&nbsp;&nbsp;' + ZIP_NAME + " &middot; " + str(PIN_SIZE) + " bytes<br>"
                "MD5&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + PIN_MD5 + "<br>"
                "SHA-256&nbsp;&nbsp;" + SHA + "<br>"
                "RETRIEVED&nbsp;" + STAMP + "</div>"
                '<div class="desc" style="margin-top:14px">Per-file hashes: '
                '<a href="../.provenance/nasa-os101/manifest.sha256">manifest.sha256</a> &middot; '
                '<a href="../.provenance/nasa-os101/provenance.json">provenance.json</a></div></div>'
            )

            tiers_table = (
                '<div class="tablewrap"><table><thead><tr>'
                "<th>Tier</th><th>What</th><th>Author</th><th>License</th></tr></thead><tbody>"
                '<tr><td><span class="tag tag-up">A &middot; Upstream</span></td>'
                "<td>Every file extracted from the Zenodo zip: <code>Module_1..5/**</code>, "
                "<code>README.md</code>, <code>LICENSE.md</code>, all images. <strong>Unmodified.</strong></td>"
                "<td>" + TEAM + "</td><td>CC BY 4.0</td></tr>"
                '<tr><td><span class="tag tag-render">B &middot; Render</span></td>'
                "<td>The <code>.html</code> beside each upstream <code>.md</code>. Same words; "
                "format converted and a provenance banner added.</td>"
                "<td>Text: NASA team<br>Banner: " + AUTHOR + "</td><td>CC BY 4.0</td></tr>"
                '<tr><td><span class="tag tag-local">C &middot; Local</span></td>'
                "<td><code>index.html</code>, <code>catalogue.html</code>, <code>provenance.html</code>, "
                "<code>NOTICE.md</code>, <code>CITATION.cff</code>, <code>.provenance/**</code>. "
                "<strong>Not part of the NASA archive.</strong></td>"
                "<td>" + AUTHOR + "</td><td>Code EUPL 1.2<br>Text CC BY-SA 4.0</td></tr>"
                "</tbody></table></div>"
            )

            index_body = (
                head("01", "Verification") + verify_box + "</section>"
                + head("02", "What is upstream, what is mine")
                + '<div class="grid2" style="margin-top:24px">'
                '<div class="card"><span class="tag tag-up">Upstream &middot; unmodified</span>'
                "<h3>" + str(len(UP)) + " files from NASA / Zenodo</h3>"
                '<p style="font-size:14px;color:#3f3f46;margin:0">Nothing rewritten, nothing removed. '
                "Each file is hashed in the manifest so any later edit is detectable. "
                'Attribution belongs to ' + TEAM + ".</p></div>"
                '<div class="card"><span class="tag tag-local">Local &middot; ' + AUTHOR + "</span>"
                "<h3>Pages and packaging added here</h3>"
                '<p style="font-size:14px;color:#3f3f46;margin:0">This index, the catalogue, the provenance map, '
                "the HTML renders and the verification metadata were produced locally for PSIVI.COM. "
                "They carry my own attribution, not NASA's.</p></div></div>"
                + tiers_table
                + '<p style="margin-top:14px;font-size:13px;color:#52525b">'
                'Future apiary / Earth-observation adaptations will live in a separate folder '
                "<code>nasa-open-science-apiary/</code> so this mirror stays pristine. "
                '<a href="provenance.html">Full provenance map &rarr;</a></p></section>'
                + head("03", "Course contents")
                + '<p style="margin-top:20px;font-size:14.5px;color:#3f3f46">'
                'Prefer the original course overview? <a href="README.html"><strong>Read README.html</strong></a> '
                "&mdash; the upstream introduction, rendered with its banner.</p>"
                + lesson_blocks("") + "</section>"
                + head("04", "Get the archive")
                + '<div style="margin-top:20px">'
                '<a class="pill primary" href="' + ZIP_URL + '">&#11015; Download full .zip (Zenodo)</a>'
                '<a class="pill" href="catalogue.html">&#128218; Descriptive catalogue</a>'
                '<a class="pill" href="provenance.html">&#128270; Provenance map</a>'
                '<a class="pill" href="' + TREE + '">Source on GitHub</a>'
                '<a class="pill" href="NOTICE.md">NOTICE.md</a>'
                '<a class="pill" href="CITATION.cff">CITATION.cff</a></div>'
                '<p style="margin-top:12px;font-size:12.5px;color:#71717a">'
                "The ZIP is served by Zenodo (CERN) itself &mdash; the exact archive verified above.</p></section>"
            )
            (DEST / "index.html").write_text(
                page("NASA Open Science 101 - PSIVI Open Science Archive",
                     "PSIVI.COM &mdash; Open Science Archive &mdash; Langford, BC &mdash; Goldstream",
                     "NASA Open<br>Science 101",
                     "Version 1.0.0 &middot; mirrored from Zenodo (CERN) &middot; CC BY 4.0<br>"
                     "Local packaging and verification by " + AUTHOR + " &mdash; <a href=\"https://psivi.com\">psivi.com</a>",
                     index_body, "LOCAL PAGE &middot; VERIFIED MIRROR"),
                encoding="utf-8")

            cat_body = (
                head("01", "How to read this catalogue")
                + '<div class="card" style="margin-top:24px"><span class="tag tag-local">Local &middot; ' + AUTHOR + "</span>"
                '<p style="font-size:14px;color:#3f3f46;margin:6px 0 0">'
                "Every description below is quoted from the upstream lesson's own <em>Overview</em> section. "
                "Nothing here is invented; the summaries belong to the NASA authors, the page belongs to me.</p></div></section>"
                + head("02", "Modules and lessons") + lesson_blocks("") + "</section>"
                + head("03", "Archive documents")
                + '<div class="card" style="margin-top:20px">'
                '<div class="lesson"><strong>Course overview (README)</strong>'
                '<div class="meta">upstream &middot; CC BY 4.0</div>'
                "<p>The NASA TOPS introduction: what Open Science 101 covers, the five-module workflow, "
                "and how the digital badge is earned.</p>"
                '<a href="README.html">Read &rarr;</a> &nbsp; <a href="README.md">source .md</a></div>'
                '<div class="lesson"><strong>Upstream license</strong>'
                '<div class="meta">upstream &middot; CC BY 4.0</div>'
                "<p>The license text shipped inside the Zenodo archive, applying to all upstream material.</p>"
                '<a href="LICENSE.html">Read &rarr;</a> &nbsp; <a href="LICENSE.md">source .md</a></div>'
                '<div class="lesson"><strong>Attribution notice</strong>'
                '<div class="meta">local &middot; ' + AUTHOR + "</div>"
                "<p>Which parts are NASA's, which parts are mine, and what was changed.</p>"
                '<a href="NOTICE.md">Read &rarr;</a></div></div></section>'
            )
            (DEST / "catalogue.html").write_text(
                page("Catalogue - NASA Open Science 101",
                     "PSIVI.COM &mdash; Descriptive catalogue",
                     "Catalogue",
                     "Titles and overviews quoted from the upstream lessons themselves.",
                     cat_body, "LOCAL PAGE"),
                encoding="utf-8")

            prov_body = (
                head("01", "The boundary")
                + '<div class="klein-box-full" style="margin-top:24px">'
                '<div class="label">Provenance map</div>'
                '<div class="value">Upstream vs local</div>'
                '<div class="desc">This folder mixes two authors. Tier A is NASA\'s, byte-for-byte. '
                "Tier B is NASA's text in a new file format. Tier C is mine. "
                "Nothing in Tier A has been edited.</div></div>"
                + tiers_table + "</section>"
                + head("02", "Evidence")
                + '<div class="tablewrap"><table><thead><tr><th>Item</th><th>Value</th></tr></thead><tbody>'
                "<tr><td>Source record</td><td class=\"mono\">Zenodo " + REC_ID + " (CERN)</td></tr>"
                '<tr><td>Version DOI</td><td class="mono"><a href="' + DOI_URL + '">' + DOI + "</a></td></tr>"
                "<tr><td>Archive</td><td class=\"mono\">" + ZIP_NAME + " &middot; " + str(PIN_SIZE) + " bytes</td></tr>"
                "<tr><td>MD5</td><td class=\"mono\">" + PIN_MD5 + "</td></tr>"
                "<tr><td>SHA-256</td><td class=\"mono\">" + SHA + "</td></tr>"
                "<tr><td>Retrieved (UTC)</td><td class=\"mono\">" + STAMP + "</td></tr>"
                "<tr><td>Upstream files hashed</td><td class=\"mono\">" + str(len(UP)) + "</td></tr>"
                "<tr><td>HTML renders produced</td><td class=\"mono\">" + str(len(mds)) + "</td></tr>"
                "</tbody></table></div>"
                '<p style="margin-top:16px;font-size:13.5px;color:#3f3f46">'
                'Per-file hashes: <a href="../.provenance/nasa-os101/manifest.sha256">manifest.sha256</a>. '
                'List of locally added files: <a href="../.provenance/nasa-os101/local-additions.txt">local-additions.txt</a>.</p>'
                "<pre>cd nasa-open-science\nsha256sum -c ../.provenance/nasa-os101/manifest.sha256</pre></section>"
                + head("03", "Rules for this mirror")
                + '<div class="card" style="margin-top:20px;font-size:14px;color:#3f3f46">'
                "<p style=\"margin:0 0 10px\"><strong>1.</strong> <code>nasa-open-science/</code> is machine-managed. "
                "Re-running the builder rebuilds it from the pinned DOI.</p>"
                "<p style=\"margin:0 0 10px\"><strong>2.</strong> Adaptations for apiary and Earth observation go in "
                "<code>nasa-open-science-apiary/</code>, marked <em>adapted from</em>, under CC BY-SA 4.0.</p>"
                "<p style=\"margin:0\"><strong>3.</strong> No NASA endorsement is implied anywhere.</p></div></section>"
            )
            (DEST / "provenance.html").write_text(
                page("Provenance - NASA Open Science 101",
                     "PSIVI.COM &mdash; Provenance map",
                     "Upstream<br>vs local",
                     "Exactly which bytes came from the Zenodo DOI, and which were added by " + AUTHOR + ".",
                     prov_body, "LOCAL PAGE"),
                encoding="utf-8")

            (DEST / "NOTICE.md").write_text(
                "# Attribution Notice\n\n"
                "This folder mixes upstream NASA material with local PSIVI additions.\n\n"
                "## Tier A - Upstream, unmodified\n"
                "- **Author:** " + TEAM + " (2023)\n"
                "- **Source:** " + DOI_URL + " (Zenodo record " + REC_ID + ", version 1.0.0)\n"
                "- **License:** CC BY 4.0\n"
                "- **Files:** everything extracted from " + ZIP_NAME + " (" + str(len(UP)) + " files)\n"
                "- **Changes:** none. Hashes: ../.provenance/nasa-os101/manifest.sha256\n\n"
                "## Tier B - Format-only renders\n"
                "- The .html file beside each upstream .md.\n"
                "- Text, figures and data unchanged; Markdown converted to HTML and a provenance banner added.\n"
                "- Text remains (c) " + TEAM + ", CC BY 4.0. Banner by " + AUTHOR + ".\n\n"
                "## Tier C - Local additions\n"
                "- index.html, catalogue.html, provenance.html, NOTICE.md, CITATION.cff, .provenance/**\n"
                "- **Author:** " + AUTHOR + " | PSIVI.COM\n"
                "- **License:** code EUPL 1.2, text CC BY-SA 4.0\n"
                "- Not part of the NASA archive.\n\n"
                "## Archive fingerprint\n"
                "- MD5: " + PIN_MD5 + "\n- SHA-256: " + SHA + "\n- Retrieved (UTC): " + STAMP + "\n\n"
                "**Modifications:** this copy is archived for reference and will be adapted for apiary and "
                "Earth observation research by " + AUTHOR + " in a separate folder "
                "`nasa-open-science-apiary/`. This adaptation is not endorsed by NASA.\n",
                encoding="utf-8")

            (DEST / "CITATION.cff").write_text(
                "cff-version: 1.2.0\n"
                "type: software\n"
                'title: "NASA TOPS Open Science 101"\n'
                'version: "1.0.0"\n'
                'doi: "' + DOI + '"\n'
                "license: CC-BY-4.0\n"
                'date-released: "2023-12-06"\n'
                "authors:\n"
                '  - name: "' + TEAM + '"\n'
                'url: "' + DOI_URL + '"\n',
                encoding="utf-8")

            local = ["index.html", "catalogue.html", "provenance.html", "NOTICE.md", "CITATION.cff"]
            local += [p.relative_to(DEST).as_posix() for p in sorted(DEST.rglob("*.html"))
                      if p.relative_to(DEST).as_posix() not in local]
            (PROV / "local-additions.txt").write_text("\n".join(sorted(set(local))) + "\n", encoding="utf-8")
            (PROV / "provenance.json").write_text(json.dumps({
                "source": "Zenodo (CERN)",
                "record": REC_ID,
                "version_doi": DOI,
                "version": "1.0.0",
                "license": "CC-BY-4.0",
                "file": ZIP_NAME,
                "size": PIN_SIZE,
                "md5": PIN_MD5,
                "sha256": SHA,
                "retrieved_utc": STAMP,
                "tier_A_upstream_files": len(UP),
                "tier_B_html_renders": len(mds),
                "tier_C_local_author": AUTHOR,
                "install_path": DEST.as_posix()
            }, indent=2) + "\n", encoding="utf-8")

            reuse = Path("REUSE.toml")
            marker = 'path = "nasa-open-science/**"'
            if reuse.exists() and marker not in reuse.read_text(encoding="utf-8"):
                txt = reuse.read_text(encoding="utf-8")
                reuse.write_text(txt.rstrip() + "\n\n[[annotations]]\n" + marker +
                    '\nprecedence = "override"\n'
                    'SPDX-FileCopyrightText = "2023 ' + TEAM + '"\n'
                    'SPDX-License-Identifier = "CC-BY-4.0"\n', encoding="utf-8")
                log("REUSE.toml annotated")

            for junk in [DEST / "files.html", Path("tpl.html")]:
                if junk.exists():
                    junk.unlink()
                    log("Removed obsolete " + str(junk))

            shutil.rmtree(TMP)
            log("DONE - index, catalogue, provenance generated")
        run: |
          printf '%s' "$BUILDER_PY" > "$RUNNER_TEMP/build_os101.py"
          python3 "$RUNNER_TEMP/build_os101.py"

      - name: Commit and push
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add -A nasa-open-science .provenance/nasa-os101
          git add REUSE.toml || true
          git add -A tpl.html || true
          if git diff --cached --quiet; then
            echo "No changes to commit"
          else
            git commit -m "feat(os101): Klein-blue NASA styling, explicit upstream/local provenance tiers, descriptive catalogue"
            git push || { git pull --rebase origin main && git push; }
          fi
```

---

## 7. Step 5 — the CI guard

**Relative path: `.github/workflows/verify-os101.yml`**

Read-only. No network. Fails any push or pull request that alters a single upstream byte.
It checks only Tier A files, so your local pages never trigger a false alarm.

```yaml
name: Verify OS101 Provenance

on:
  push:
    paths:
      - 'nasa-open-science/**'
      - '.provenance/nasa-os101/**'
  pull_request:
    paths:
      - 'nasa-open-science/**'
      - '.provenance/nasa-os101/**'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Verify upstream integrity
        run: |
          test -f .provenance/nasa-os101/manifest.sha256 || {
            echo "No manifest yet - run the builder workflow first."; exit 1; }
          cd nasa-open-science
          sha256sum -c ../.provenance/nasa-os101/manifest.sha256
```

---

## 8. Step 6 — run it (web interface only)

1. Commit the five files above.
2. Open the **Actions** tab.
3. Select **Vendor NASA OS101 (Web-Based Build)** in the left sidebar.
   *Not* any other workflow — if the log shows `cargo build`, you picked the wrong one.
4. **Run workflow → Branch: main → Run workflow**.
5. Wait for the green check, then open `https://YOUR-DOMAIN/nasa-open-science/`.

Expected log lines:

```
Querying Zenodo API
Pin confirmed by API
Downloading pinned archive
Cryptographic verification passed sha256=...
Extracting (zip-slip guarded)
Upstream payload installed: NNN unmodified files hashed
Rendered NN upstream pages (format-only)
DONE - index, catalogue, provenance generated
```

Optional terminal path (same result, run from the repo root):

```bash
sudo apt-get install -y pandoc
python3 - <<'PY'
# extract BUILDER_PY from the workflow, or simply trigger the workflow instead
PY
```

---

## 9. Verify at any time

```bash
cd nasa-open-science
sha256sum -c ../.provenance/nasa-os101/manifest.sha256
```

Every line must read `OK`. Independently re-check the source:

```bash
curl -s https://zenodo.org/api/records/10161527 | python3 -m json.tool | head -40
```

---

## 10. Make it yours

Keep the folder names unless you are prepared to edit every reference.

| Variable / string | Example value | Change to |
|---|---|---|
| `AUTHOR` | `Louis-Philippe Audette` | your name |
| `TREE` | `github.com/psivicom/psivicom.github.io/...` | your repo URL |
| NAV hub link | `https://psivi.com/` | your site |
| Top-bar / kicker text | `PSIVI.COM`, `Langford, BC` | your brand and place |
| Footer copyright | `2026 ... PSIVI.COM` | your copyright |
| CSS `#002FA7` | International Klein Blue | your accent colour |

**If you rename `DEST`, you must also change:** `BASE`, the hardcoded `marker`
string, every `../.provenance/nasa-os101/...` link, the REUSE path, and both
`paths:` filters plus the `cd` in the guard workflow. Renaming is deliberate work,
not a one-line edit.

**Never change** `REC_ID`, `PIN_MD5`, `PIN_SIZE`, `ZIP_NAME` — those are the pin.
To follow a newer curriculum release, look up the new *version* DOI on Zenodo and
update all four together.

---

## 11. The legal model

| Tier | Content | Author | Licence | Modified? |
|---|---|---|---|---|
| **A** | Everything from the Zenodo zip | NASA TOPS OS101 Curriculum Development Team | CC BY 4.0 | No |
| **B** | `.html` beside each `.md` | Text: NASA · Banner: you | CC BY 4.0 | Format only |
| **C** | index / catalogue / provenance / NOTICE / CITATION / `.provenance` | you | your repo policy | New work |

CC BY 4.0 obligations you are satisfying automatically:

1. **Attribution** — team name, title, version, DOI, licence on every page.
2. **Indicate changes** — the banner states exactly what changed (format + banner).
3. **Keep notices** — upstream `LICENSE.md` and third-party markings preserved.
4. **No added restrictions** — the archive stays CC BY 4.0, fenced by `REUSE.toml`.
5. **No endorsement** — "Not endorsed by NASA" appears site-wide. Do not use NASA
   insignia as your branding; copyright permission is not trademark permission.

Your certificate or badge is a personal credential. The right to reuse comes from
the licence, not from the badge.

**Adaptations** (your apiary / Earth-observation lessons) go in a **sibling folder**
such as `nasa-open-science-apiary/`, headed *"Adapted from NASA TOPS Open Science 101
(CC BY 4.0)"*, under your own licence. The mirror is rebuilt from scratch each run —
anything you place inside it will be erased.

---

## 12. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Invalid workflow file ... yaml syntax` | Unindented heredoc broke the YAML block | Use this Python-in-`env` version; never add bash heredocs |
| `here-document ... wanted 'TPL'` | Same root cause | Same fix |
| `FATAL: no manifest at .provenance/...` | Guard ran before the builder | Run the builder workflow first |
| Log shows `cargo build` / `cargo test` | You triggered a different workflow | Pick **Vendor NASA OS101 (Web-Based Build)** |
| `mv: cannot stat 'temp_extract/...'` | Obsolete bash script | Delete it; use this workflow |
| `remote: Permission ... denied` (403) | Read-only workflow token | Settings → Actions → General → Read and write |
| Manifest links 404 on the site | Jekyll skips dot-folders | Add empty `.nojekyll` at repo root |
| REUSE annotation missing | `REUSE.toml` did not exist at build time | Create it, re-run |
| Duplicate REUSE blocks | Path written as a list | Use `path = "nasa-open-science/**"` exactly |
| `No changes to commit` | Archive already current | Normal; nothing to do |

---

## 13. Updating, re-running, uninstalling

- **Re-run**: safe and idempotent. The mirror is deleted and rebuilt from the pin;
  the timestamp refreshes; upstream hashes stay identical.
- **Update to a new release**: change `REC_ID`, `ZIP_NAME`, `PIN_MD5`, `PIN_SIZE`
  together from the new Zenodo *version* record.
- **Uninstall**: delete `nasa-open-science/`, `.provenance/nasa-os101/`, both
  workflows, and the `nasa-open-science/**` block in `REUSE.toml`.

---

## 14. Reference

- Curriculum version DOI: https://doi.org/10.5281/zenodo.10161527
- Zenodo record (CERN): https://zenodo.org/records/10161527
- Direct archive: https://zenodo.org/records/10161527/files/open-science-101-v-1-0-0.zip?download=1
- Licence: https://creativecommons.org/licenses/by/4.0/
- REUSE specification: https://reuse.software/spec/
- Live example: https://psivi.com/nasa-open-science/

---

*Guide by Louis-Philippe Audette | PSIVI.COM — text CC BY-SA 4.0, workflow code EUPL 1.2.*
*Upstream curriculum © 2023 NASA TOPS Open Science 101 Curriculum Development Team, CC BY 4.0.*
*Not endorsed by NASA.*
