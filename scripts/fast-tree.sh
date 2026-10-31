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

# Prepare files
> "$OUTPUT_FILE"
> tree_snippet.html
> tree.md

printf '```text\n' >> tree.md

while IFS= read -r line; do
  path=$(echo "$line" | sed 's/^[^a-zA-Z0-9_./-]*//')
  
  # 1. For HTML (Colors)
  if [ -d "$path" ]; then
    echo "<span style=\"color:#569cd6\">${line}</span>" >> tree_snippet.html # Blue
  elif [ -x "$path" ]; then
    echo "<span style=\"color:#6a9955\">${line}</span>" >> tree_snippet.html # Green
  else
    echo "<span style=\"color:#d4d4d4\">${line}</span>" >> tree_snippet.html # White
  fi
  
  # 2. For Markdown (Bold for folders)
  if [ -d "$path" ]; then
    echo "**${line}**" >> tree.md
  else
    echo "${line}" >> tree.md
  fi

  # 3. For Plain/JSON
  echo "$line" >> "$OUTPUT_FILE"
  
done < /tmp/raw_tree.txt

printf '```\n' >> tree.md

# JSON
printf '[\n' > tree.json
awk '{gsub(/\033\[[0-9;]*m/, ""); sub(/^[^a-zA-Z0-9_./-]*/, ""); if($0!="") printf "  \"%s\",\n", $0}' "$OUTPUT_FILE" | sed '$ s/,$//' >> tree.json
printf ']\n' >> tree.json
