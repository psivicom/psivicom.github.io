#!/bin/bash
set -euo pipefail

OUTPUT_FILE="tree_clean.txt"

# Create the awk script for drawing
cat > /tmp/draw_tree.awk << 'AWKEOF'
BEGIN { FS="/" }
{
  sub(/^\.\//, "", $0)
  if ($0 == "") next

  n = split($0, parts, "/")
  name = parts[n]
  depth = n - 1

  indent = ""
  for (i = 1; i < depth; i++) {
    indent = indent "│   "
  }

  # We will append color codes later in the bash loop
  print indent "├── " name
}
AWKEOF

# Generate the raw structure first
find . \
  -not -path './.git/*' \
  -not -path './.github/*' \
  -not -name 'TREE' \
  -not -name 'tree.json' \
  -not -name 'tree.md' \
  -not -name 'tree_clean.txt' \
  -not -name 'fast-tree.sh' \
  -not -name 'draw_tree.awk' \
  -print | sort | awk -f /tmp/draw_tree.awk > /tmp/raw_tree.txt

# Now add colors by checking each path against the filesystem
> "$OUTPUT_FILE"
while IFS= read -r line; do
  # Extract the path from the tree line (remove indentation and connector)
  path=$(echo "$line" | sed 's/^[^a-zA-Z0-9_./-]*//')
  
  if [ -d "$path" ]; then
    # Blue for directories: \033[34m
    echo -e "${line/├── /├── \033[34m}\033[0m" >> "$OUTPUT_FILE"
  elif [ -x "$path" ]; then
    # Green for executables: \033[32m
    echo -e "${line/├── /├── \033[32m}\033[0m" >> "$OUTPUT_FILE"
  else
    # White/Grey for files: \033[37m
    echo -e "${line/├── /├── \033[37m}\033[0m" >> "$OUTPUT_FILE"
  fi
done < /tmp/raw_tree.txt

# 1. Markdown (supports ANSI colors in many viewers)
printf '```text\n' > tree.md
cat "$OUTPUT_FILE" >> tree.md
printf '```\n' >> tree.md

# 2. Plain (with colors)
cp "$OUTPUT_FILE" TREE

# 3. JSON (clean names only, no colors)
printf '[\n' > tree.json
awk '{
  # Strip ANSI codes and tree characters for JSON
  gsub(/\033\[[0-9;]*m/, "", $0)
  sub(/^[^a-zA-Z0-9_./-]*/, "", $0)
  if ($0 != "") printf "  \"%s\",\n", $0
}' "$OUTPUT_FILE" | sed '$ s/,$//' >> tree.json
printf ']\n' >> tree.json

echo "Colored tree generated."
