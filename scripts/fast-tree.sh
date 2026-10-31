#!/bin/bash
set -euo pipefail

# Use the tree command (fastest possible)
tree -I '.git|archive|data|docs|src|reports|wendy-go|config|assets|maps|logs|tests|tools|_techreports|dist|js|fast-tree.sh|tree.md|tree_snippet.html' \
  --charset utf-8 -F --dirsfirst > /tmp/raw_tree.txt

# Convert to Markdown
{
  echo '```'
  cat /tmp/raw_tree.txt
  echo '```'
} > tree.md

# Convert to HTML with Klein Blue background and smart coloring
{
  echo '<div style="font-family:monospace; line-height:1.5; background:#002FA7; color:#ffffff; padding:24px; border-radius:12px;">'
  while IFS= read -r line; do
    # Detect type and assign color
    if [[ "$line" == */ ]]; then
      color="#80BFFF"  # Directory
    elif [[ "$line" == *.sh* || "$line" == *.go* || "$line" == *.py* ]]; then
      color="#80FF80"  # Script
    else
      color="#ffffff"  # File
    fi
    echo "<span style=\"color:$color\">$line</span><br>"
  done < /tmp/raw_tree.txt
  echo '</div>'
} > tree_snippet.html

# Inject into files (same as above)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
awk -v content="$(cat tree.md)" -v ts="$TIMESTAMP" '
  /<!-- AUTO_TREE_START -->/ {
    print "<!-- AUTO_TREE_START -->"
    print "<!-- Last updated: " ts " -->"
    print content
    print "<!-- AUTO_TREE_END -->"
    skip = 1
    next
  }
  /<!-- AUTO_TREE_END -->/ { skip = 0; next }
  !skip { print }
' README.md > README.md.tmp && mv README.md.tmp README.md

awk -v content="$(cat tree_snippet.html)" -v ts="$TIMESTAMP" '
  /<!-- AUTO_TREE_START -->/ {
    print "<!-- AUTO_TREE_START -->"
    print "<!-- Last updated: " ts " -->"
    print content
    print "<!-- AUTO_TREE_END -->"
    skip = 1
    next
  }
  /<!-- AUTO_TREE_END -->/ { skip = 0; next }
  !skip { print }
' index.html > index.html.tmp && mv index.html.tmp index.html

rm -f /tmp/raw_tree.txt
echo "✅ Tree generated (using tree command)"
