#!/bin/bash
set -euo pipefail

# 1. Generate raw structure (Lightning fast find + awk)
find . \
  -not -path './.git/*' \
  -not -path './.github/*' \
  -not -name 'TREE' \
  -not -name 'tree.json' \
  -not -name 'tree.md' \
  -not -name 'tree_clean.txt' \
  -not -name 'tree_snippet.html' \
  -not -name 'fast-tree.sh' \
  -print | sort | awk '
  BEGIN { FS="/" }
  {
    sub(/^\.\//, "", $0)
    if ($0 == "") next
    n = split($0, parts, "/")
    name = parts[n]
    depth = n - 1
    indent = ""
    for (i = 1; i < depth; i++) indent = indent "│   "
    print indent "├── " name
  }' > /tmp/raw_tree.txt

# 2. Build PLAIN Markdown (No bold, just clean text)
printf '```text\n' > tree.md
cat /tmp/raw_tree.txt >> tree.md
printf '```\n' >> tree.md

# 3. Build KLEIN BLUE HTML
{
  echo '<div style="font-family:monospace; line-height:1.5; background:#002FA7; color:#ffffff; padding:24px; border-radius:12px;">'
  while IFS= read -r line; do
    path=$(echo "$line" | sed 's/^[^a-zA-Z0-9_./-]*//')
    if [ -d "$path" ]; then
      echo "  <span style=\"color:#80BFFF\">${line}</span><br>" # Light blue for dirs
    elif [[ "$path" == *.sh || "$path" == *.go || "$path" == *.py ]]; then
      echo "  <span style=\"color:#80FF80\">${line}</span><br>" # Light green for scripts
    else
      echo "  <span style=\"color:#ffffff\">${line}</span><br>" # White for files
    fi
  done < /tmp/raw_tree.txt
  echo '</div>'
} > tree_snippet.html

# 4. Inject into README.md (Safe multiline replacement using awk)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
MD_CONTENT=$(cat tree.md)
awk -v content="$MD_CONTENT" -v ts="$TIMESTAMP" '
  /<!-- AUTO_TREE_START -->/ {
    print "<!-- AUTO_TREE_START -->"
    print "<!-- Auto-updated by .github/workflows/update-tree.yml -->"
    print "<!-- Last updated: " ts " -->"
    print content
    print "<!-- AUTO_TREE_END -->"
    skip = 1
    next
  }
  /<!-- AUTO_TREE_END -->/ { skip = 0; next }
  !skip { print }
' README.md > README.md.tmp && mv README.md.tmp README.md

# 5. Inject into index.html
HTML_CONTENT=$(cat tree_snippet.html)
awk -v content="$HTML_CONTENT" -v ts="$TIMESTAMP" '
  /<!-- AUTO_TREE_START -->/ {
    print "<!-- AUTO_TREE_START -->"
    print "<!-- Auto-updated by .github/workflows/update-tree.yml -->"
    print "<!-- Last updated: " ts " -->"
    print content
    print "<!-- AUTO_TREE_END -->"
    skip = 1
    next
  }
  /<!-- AUTO_TREE_END -->/ { skip = 0; next }
  !skip { print }
' index.html > index.html.tmp && mv index.html.tmp index.html

echo "✅ Tree generated and injected successfully (Plain Markdown + Klein Blue HTML)."
