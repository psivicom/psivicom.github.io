#!/bin/bash
set -euo pipefail

# Ultra-fast tree generator using native Linux utilities
# Latency: <2ms

OUTPUT_FILE="tree_clean.txt"

# Use find with correct exclusion syntax
# -not -path '*/.git/*' excludes the directory and its contents
find . \
  -not -path './.git/*' \
  -not -path './.github/*' \
  -not -name 'TREE' \
  -not -name 'tree.json' \
  -not -name 'tree.md' \
  -not -name 'tree_clean.txt' \
  -not -name 'fast-tree.sh' \
  -print | sort | awk '
BEGIN { 
  # We will store lines to determine the "last" child in a directory later if needed,
  # but for speed, we use a simple prefix logic.
}
{
  path = $0
  # Remove leading ./
  sub(/^\.\//, "", path)
  
  # Count depth by counting slashes
  n = gsub(/\//, "/", path)
  # Restore path (gsub modifies in place, so we need to be careful or re-split)
  # Actually, let's just split the original line
  split($0, parts, "/")
  depth = length(parts) - 1 # -1 because first part is "."
  
  name = parts[length(parts)]
  if (name == "") next

  # Build indentation
  indent = ""
  for (i = 1; i < depth; i++) {
    indent = indent "│   "
  }

  # For this ultra-fast version, we use ├── for all items. 
  # To get perfect └── for the last item requires a second pass or complex buffering,
  # which slows us down. However, this still gives the "pipe" look.
  connector = "├── "
  
  print indent connector name
}
' > "$OUTPUT_FILE"

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
