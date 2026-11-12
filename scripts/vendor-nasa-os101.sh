#!/usr/bin/env bash
# Pin → fetch → verify → install → publish NASA TOPS Open Science 101 v1.0.0
# Source of truth: Zenodo (CERN) version DOI 10.5281/zenodo.10161527 — CC BY 4.0
set -euo pipefail
IFS=$'\n\t'

readonly REC_ID="10161527"
readonly DOI="10.5281/zenodo.${REC_ID}"
readonly API="https://zenodo.org/api/records/${REC_ID}"
readonly ZIP_NAME="open-science-101-v-1-0-0.zip"
readonly PIN_MD5="ecde9587a3c95be40eb0eb3cfa083ea5"
readonly PIN_SIZE="23311809"
readonly DEST="nasa-open-science"
readonly PROV=".provenance/nasa-os101"

WORKDIR="$(mktemp -d)"; trap 'rm -rf "$WORKDIR"' EXIT

zulu_ms() {
  local t; t="$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ 2>/dev/null || true)"
  [[ -z "$t" || "$t" == *3N* ]] && t="$(python3 -c 'from datetime import datetime,timezone
n=datetime.now(timezone.utc);print(n.strftime("%Y-%m-%dT%H:%M:%S.")+f"{n.microsecond//1000:03d}Z")')"
  printf '%s' "$t"
}
log()   { printf '[%s] %s\n' "$(zulu_ms)" "$*"; }
fatal() { printf '[%s] FATAL: %s\n' "$(zulu_ms)" "$*" >&2; exit 1; }

if command -v sha256sum >/dev/null; then SHA=(sha256sum); else SHA=(shasum -a 256); fi
if command -v md5sum    >/dev/null; then MD5=(md5sum);    else MD5=(md5 -q);      fi
hash_of() { "${SHA[@]}" "$1" | awk '{print $1}'; }
md5_of()  { local h; h="$("${MD5[@]}" "$1")"; printf '%s' "${h%% *}"; }

DO_HTML=0; DO_COMMIT=0; FORCE=0; VERIFY=0
for arg in "$@"; do
  case "$arg" in
    --html) DO_HTML=1 ;; --commit) DO_COMMIT=1 ;;
    --force) FORCE=1 ;;  --verify) VERIFY=1 ;;
    *) fatal "unknown flag: $arg" ;;
  esac
done

[[ -d .git ]] || fatal "run from the repository root (no .git here)"

if (( VERIFY )); then
  [[ -f "$PROV/manifest.sha256" ]] || fatal "no manifest at $PROV/manifest.sha256"
  log "Verifying vendored payload integrity"
  ( cd "$DEST" && "${SHA[@]}" --check --quiet "$(cd .. && pwd)/$PROV/manifest.sha256" ) \
    || fatal "PROVENANCE DRIFT — vendored files modified or missing"
  log "✅ OK — all upstream files match the pinned manifest"
  exit 0
fi

for dep in curl awk find sort python3; do
  command -v "$dep" >/dev/null || fatal "missing dependency: $dep"
done

fetch() {
  local url="$1" out="$2" i
  for i in 1 2 3 4 5; do
    if curl --fail --location --silent --show-error \
            --connect-timeout 20 --max-time 1800 -o "$out" "$url"; then return 0; fi
    log "WARN: fetch attempt ${i}/5 failed — retrying"
    rm -f "$out"; sleep $(( i * 5 ))
  done
  return 1
}

log "Querying Zenodo API ${API}"
fetch "$API" "$WORKDIR/record.json" || fatal "metadata fetch failed"
api_key="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["files"][0]["key"])' "$WORKDIR/record.json")"
api_md5="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["files"][0]["checksum"].replace("md5:",""))' "$WORKDIR/record.json")"
api_size="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["files"][0]["size"])' "$WORKDIR/record.json")"
api_url="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["files"][0]["links"]["self"])' "$WORKDIR/record.json")"

[[ "$api_key"  == "$ZIP_NAME" ]] || fatal "API filename drift: $api_key"
[[ "$api_md5"  == "$PIN_MD5"  ]] || fatal "API checksum differs from pin — refusing"
[[ "$api_size" == "$PIN_SIZE" ]] || fatal "API size differs from pin — refusing"
log "Pin confirmed by API: ${api_key} · ${api_size} bytes · md5:${api_md5}"

log "Downloading pinned archive"
fetch "$api_url" "$WORKDIR/$ZIP_NAME" || fatal "archive download failed"
actual_size="$(wc -c < "$WORKDIR/$ZIP_NAME" | tr -d ' ')"
[[ "$actual_size" == "$PIN_SIZE" ]] || fatal "size mismatch: got $actual_size"
actual_md5="$(md5_of "$WORKDIR/$ZIP_NAME")"
[[ "$actual_md5" == "$PIN_MD5" ]] || fatal "MD5 MISMATCH: got $actual_md5"
ZIP_SHA="$(hash_of "$WORKDIR/$ZIP_NAME")"
log "Verified · md5:${actual_md5} · sha256:${ZIP_SHA}"

if command -v unzip >/dev/null; then
  unzip -Z1 "$WORKDIR/$ZIP_NAME" > "$WORKDIR/entries.txt"
else
  python3 -c 'import zipfile,sys;[print(n) for n in zipfile.ZipFile(sys.argv[1]).namelist()]' "$WORKDIR/$ZIP_NAME" > "$WORKDIR/entries.txt"
fi
grep -Eq '(^/|(^|/)\.\.(/|$))' "$WORKDIR/entries.txt" && fatal "path traversal in archive — aborting"

if command -v unzip >/dev/null; then unzip -q "$WORKDIR/$ZIP_NAME" -d "$WORKDIR/x"
else python3 -m zipfile -e "$WORKDIR/$ZIP_NAME" "$WORKDIR/x"; fi

mapfile -t roots < <(find "$WORKDIR/x" -mindepth 1 -maxdepth 1 -type d)
[[ ${#roots[@]} -eq 1 ]] || fatal "unexpected archive layout (${#roots[@]} roots)"
[[ -f "${roots[0]}/LICENSE.md" ]] || fatal "upstream LICENSE.md missing — aborting"

if [[ -e "$DEST" ]]; then
  (( FORCE )) || fatal "$DEST exists — re-run with --force to replace"
  mv "$DEST" "${DEST}.previous"
  log "Existing tree preserved at ${DEST}.previous"
fi
mkdir -p "$DEST" "$PROV"
cp -a "${roots[0]}/." "$DEST/"
log "Installed upstream payload → $DEST/"

( cd "$DEST" && find . -type f -print0 | LC_ALL=C sort -z | xargs -0 "${SHA[@]}" ) > "$PROV/manifest.sha256"
cp "$WORKDIR/record.json" "$PROV/record.json"

STAMP="$(zulu_ms)"
cat > "$DEST/NOTICE.md" <<EOF
# Attribution Notice

NASA TOPS Open Science 101 Curriculum, Version 1.0.0.

- **Authors:** NASA TOPS Open Science 101 Curriculum Development Team (2023)
- **Source (version DOI, immutable):** https://doi.org/${DOI}
- **License:** CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/
- **Retrieved (UTC):** ${STAMP}
- **Archive:** ${ZIP_NAME} · ${PIN_SIZE} bytes
- **MD5:** ${PIN_MD5}
- **SHA-256:** ${ZIP_SHA}

Upstream files are unmodified and remain under CC BY 4.0 (see LICENSE.md).
Individually marked third-party material retains its own license.

**Modifications:** archived for reference; forthcoming adaptations for apiary
and Earth-observation research by Louis-Philippe Audette are new derivative
files under this repository's CC BY-SA 4.0 policy, marked "adapted from".
This adaptation is not endorsed by NASA.
EOF

cat > "$PROV/provenance.json" <<EOF
{
  "source": "Zenodo (CERN)",
  "record": "${REC_ID}",
  "version_doi": "${DOI}",
  "version": "1.0.0",
  "license": "CC-BY-4.0",
  "file": "${ZIP_NAME}",
  "size": ${PIN_SIZE},
  "md5": "${PIN_MD5}",
  "sha256": "${ZIP_SHA}",
  "retrieved_utc": "${STAMP}",
  "install_path": "${DEST}"
}
EOF

if [[ -f REUSE.toml ]] && ! grep -q "^path = \"${DEST}/\*\*\"" REUSE.toml; then
  cat >> REUSE.toml <<EOF

[[annotations]]
path = "${DEST}/**"
precedence = "override"
SPDX-FileCopyrightText = "2023 NASA TOPS Open Science 101 Curriculum Development Team"
SPDX-License-Identifier = "CC-BY-4.0"
EOF
  log "REUSE.toml annotated"
fi

if (( DO_HTML )); then
  ext="md"
  if command -v pandoc >/dev/null; then
    ext="html"
    cat > "$WORKDIR/tpl.html" <<TPL
<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>\$title\$ — NASA Open Science 101 · PSIVI</title>
<style>
body{max-width:52rem;margin:2rem auto;padding:0 1rem;background:#0d1117;color:#e6edf3;font:16px/1.65 system-ui,sans-serif}
a{color:#7ee787}img{max-width:100%}table{border-collapse:collapse}td,th{border:1px solid #30363d;padding:.4rem}
.trust-banner{margin:2rem 0 1.5rem;padding:1rem 1.25rem;border:1px solid #238636;border-radius:10px;background:linear-gradient(135deg,#0d2818 0%,#161b22 100%);display:flex;align-items:center;gap:1rem;font-size:.9rem}
.trust-banner .seal{font-size:2rem;filter:drop-shadow(0 0 8px #2ea043)}
.trust-banner .meta{flex:1}
.trust-banner .meta strong{color:#7ee787;display:block;margin-bottom:.25rem}
.trust-banner .meta code{background:#0d1117;padding:.1rem .4rem;border-radius:4px;font-size:.8rem;color:#8b949e}
.trust-banner .verified{color:#3fb950;font-weight:600}
footer{margin-top:3rem;border-top:1px solid #30363d;padding-top:1rem;font-size:.85rem;color:#8b949e}
</style></head><body>
<div class="trust-banner">
  <div class="seal">🛡️</div>
  <div class="meta">
    <strong>✅ Verified · Cryptographically Pinned</strong>
    <span class="verified">Source: <a href="https://doi.org/10.5281/zenodo.10161527">Zenodo v1.0.0</a> · License: CC BY 4.0</span><br>
    <code>MD5: ${PIN_MD5}</code> · <code>SHA-256: ${ZIP_SHA}</code><br>
    <code>Timestamp: ${STAMP}</code>
  </div>
</div>
\$body\$
<footer><p>🔐 This page is part of the NASA TOPS Open Science 101 archive, retrieved <strong>${STAMP}</strong> from the immutable Zenodo version DOI <a href="https://doi.org/10.5281/zenodo.10161527">10.5281/zenodo.10161527</a>. Integrity verified against MD5 + SHA-256 checksums. Not endorsed by NASA.</p></footer>
</body></html>
TPL
    log "Rendering Markdown → HTML5"
    ( cd "$DEST" && find . -name '*.md' -print0 | while IFS= read -r -d '' md; do
        pandoc "$md" -f gfm -t html5 -s --template="$WORKDIR/tpl.html" \
          --metadata title="$(basename "$(dirname "$md")")" -o "${md%.md}.html" \
          || fatal "pandoc failed: $md"
      done )
  else
    log "WARN: pandoc absent — index will link Markdown (GitHub renders it)"
  fi

  {
    cat <<HEAD
<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NASA Open Science 101 — PSIVI Open Science Hub</title>
<style>
body{max-width:60rem;margin:2rem auto;padding:0 1rem;background:#0d1117;color:#e6edf3;font:16px/1.6 system-ui,sans-serif}
a{color:#7ee787;text-decoration:none}a:hover{text-decoration:underline}
h1{border-bottom:1px solid #30363d;padding-bottom:.5rem}
.trust-seal{margin:2rem 0;padding:1.5rem;border:2px solid #238636;border-radius:12px;background:linear-gradient(135deg,#0d2818 0%,#161b22 100%);text-align:center}
.trust-seal .big-seal{font-size:4rem;margin-bottom:.5rem;filter:drop-shadow(0 0 12px #2ea043)}
.trust-seal h2{color:#3fb950;margin:0 0 .5rem;font-size:1.3rem}
.trust-seal .verified-line{color:#7ee787;font-weight:600;margin:.5rem 0}
.trust-seal code{background:#0d1117;padding:.2rem .5rem;border-radius:4px;font-size:.85rem;color:#8b949e;display:inline-block;margin:.2rem}
.card{border:1px solid #30363d;border-radius:8px;padding:1rem;margin:1rem 0;background:#161b22}
li{margin:.25rem 0}
footer{margin-top:3rem;border-top:1px solid #30363d;padding-top:1rem;font-size:.85rem;color:#8b949e}
</style></head><body>
<h1>NASA Open Science 101 <small>v1.0.0</small></h1>
<div class="trust-seal">
  <div class="big-seal">🛡️✅</div>
  <h2>Verified · Cryptographically Pinned · Publicly Auditable</h2>
  <div class="verified-line">Source: <a href="https://doi.org/10.5281/zenodo.10161527">Zenodo v1.0.0</a> · License: CC BY 4.0</div>
  <div><code>MD5: ${PIN_MD5}</code> <code>SHA-256: ${ZIP_SHA}</code></div>
  <div><code>Retrieved: ${STAMP}</code></div>
  <p style="margin-top:1rem;font-size:.9rem;color:#8b949e">This archive is immutable. Any visitor can independently verify the checksums against the Zenodo API. Provenance manifest: <a href="../.provenance/nasa-os101/manifest.sha256">manifest.sha256</a></p>
</div>
<p>Archived from the immutable Zenodo version DOI <a href="https://doi.org/10.5281/zenodo.10161527">10.5281/zenodo.10161527</a>, checksum-verified. <a href="NOTICE.md">Attribution &amp; provenance</a>.</p>
HEAD
    for m in "$DEST"/Module_*; do
      [[ -d "$m" ]] || continue
      printf '<div class="card"><h2>%s</h2><ul>\n' "$(basename "$m" | tr '_' ' ')"
      for l in "$m"/Lesson_*; do
        [[ -d "$l" ]] || continue
        tgt="${l#"$DEST"/}/readme.$ext"
        printf '<li><a href="%s">%s</a></li>\n' "$tgt" "$(basename "$l" | tr '_' ' ')"
      done
      printf '</ul></div>\n'
    done
    printf '<footer>🔐 Retrieved %s · MD5 %s · SHA-256 %s · Not endorsed by NASA.</footer></body></html>\n' "$STAMP" "$PIN_MD5" "$ZIP_SHA"
  } > "$DEST/index.html"
  log "Public index → $DEST/index.html"
fi

( cd "$DEST" && "${SHA[@]}" --check --quiet "$(cd .. && pwd)/$PROV/manifest.sha256" ) || fatal "post-install verification failed"
log "Post-install verification passed"

if (( DO_COMMIT )); then
  git add "$DEST" "$PROV"
  [[ -f REUSE.toml ]] && git add REUSE.toml
  git commit -m "vendor: NASA TOPS OS101 v1.0.0 (CC BY 4.0), pinned ${DOI}, md5 ${PIN_MD5}" \
    && log "Committed. Next: git push"
fi

log "DONE — public at https://psivi.com/${DEST}/"
