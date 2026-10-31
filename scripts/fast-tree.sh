#!/bin/bash
set -euo pipefail

# Ultra-fast tree generator using native Linux utilities
OUTPUT_FILE="tree_clean.txt"

# Create a temporary awk script to handle the drawing logic safely
cat > /tmp/draw_tree.awk << 'AWKEOF'
BEGIN { FS="/" }
{
  # Remove leading ./
  sub(/^\.\//, "", $0)
  if ($0 == "") next

  # Split path to get depth and name
  n = split($0, parts, "/")
  name = parts[n]
  depth = n - 1

  # Build indentation
  indent = ""
  for (i = 1; i < depth; i++) {
    indent = indent "│   "
  }

  print indent "├── " name
}
AWKEOF

# Find files, sort them, and draw the tree
find . \
  -not -path './.git/*' \
  -not -path './.github/*' \
  -not -name 'TREE' \
  -not -name 'tree.json' \
  -not -name 'tree.md' \
  -not -name 'tree_clean.txt' \
  -not -name 'fast-tree.sh' \
  -not -name 'draw_tree.awk' \
  -print | sort | awk -f /tmp/draw_tree.awk > "$OUTPUT_FILE"

# 1. Markdown
printf '```text\n' > tree.md
cat "$OUTPUT_FILE" >> tree.md
printf '```\n' >> tree.md

# 2. Plain
cp "$OUTPUT_FILE" TREE

# 3. JSON
printf '[\n' > tree.json
awk '{printf "  \"%s\",\n", $0}' "$OUTPUT_FILE" | sed '$ s/,$//' >> tree.json
printf ']\n' >> tree.json

echo "Tree generated successfully."
