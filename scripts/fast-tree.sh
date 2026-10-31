#!/bin/bash
set -euo pipefail

OUTPUT_FILE="tree_clean.txt"

# Create the awk script for drawing pipes
cat > /tmp/draw_tree.awk << 'AWKEOF'
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
}
AWKEOF

# Generate raw structure
find . \
  -not -path './.git/*' \
  -not -path './.github/*' \
  -not -name 'TREE' \
  -not -name 'tree.json' \
  -not -name 'tree.md' \
  -not -name 'tree_clean.txt' \
  -not -name 'tree_snippet.html' \
  -not -name 'fast-tree.sh' \
  -print | sort | awk -f /tmp/draw_tree.awk > /tmp/raw_tree.txt

# Add colors and generate HTML snippet
> "$OUTPUT_FILE"
> tree_snippet.html

while IFS= read -r line; do
  path=$(echo "$line" | sed 's/^[^a-zA-Z0-9_./-]*//')
  
  # Determine color class
  if [ -d "$path" ]; then
    styled_line="<span style=\"color:#569cd6\">${line}</span>" # Blue for dirs
  elif [ -x "$path" ]; then
    styled_line="<span style=\"color:#6a9955\">${line}</span>" # Green for executables
  else
    styled_line="<span style=\"color:#d4d4d4\">${line}</span>" # White/Grey for files
  fi
  
  echo "$styled_line" >> tree_snippet.html
  echo "$line" >> "$OUTPUT_FILE"
done < /tmp/raw_tree.txt

# Markdown (using ANSI codes for terminal viewers)
printf '```text\n' > tree.md
cat "$OUTPUT_FILE" >> tree.md
printf '```\n' >> tree.md

# Plain
cp "$OUTPUT_FILE" TREE

# JSON
printf '[\n' > tree.json
awk '{gsub(/\033\[[0-9;]*m/, ""); sub(/^[^a-zA-Z0-9_./-]*/, ""); if($0!="") printf "  \"%s\",\n", $0}' "$OUTPUT_FILE" | sed '$ s/,$//' >> tree.json
printf ']\n' >> tree.json
