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
  -not -name 'tree.html' \
  -not -name 'fast-tree.sh' \
  -print | sort | awk -f /tmp/draw_tree.awk > /tmp/raw_tree.txt

# Add colors
> "$OUTPUT_FILE"
while IFS= read -r line; do
  path=$(echo "$line" | sed 's/^[^a-zA-Z0-9_./-]*//')
  if [ -d "$path" ]; then
    echo -e "${line/├── /├── \033[34m}\033[0m" >> "$OUTPUT_FILE" # Blue
  elif [ -x "$path" ]; then
    echo -e "${line/├── /├── \033[32m}\033[0m" >> "$OUTPUT_FILE" # Green
  else
    echo -e "${line/├── /├── \033[37m}\033[0m" >> "$OUTPUT_FILE" # White
  fi
done < /tmp/raw_tree.txt

# Generate tree.html snippet (ANSI -> HTML spans)
sed 's/\x1b\[34m/<span style="color:#569cd6">/g; s/\x1b\[32m/<span style="color:#6a9955">/g; s/\x1b\[37m/<span style="color:#d4d4d4">/g; s/\x1b\[0m/<\/span>/g' "$OUTPUT_FILE" > tree.html

# Markdown
printf '```text\n' > tree.md
cat "$OUTPUT_FILE" >> tree.md
printf '```\n' >> tree.md

# Plain
cp "$OUTPUT_FILE" TREE

# JSON
printf '[\n' > tree.json
awk '{gsub(/\033\[[0-9;]*m/, ""); sub(/^[^a-zA-Z0-9_./-]*/, ""); if($0!="") printf "  \"%s\",\n", $0}' "$OUTPUT_FILE" | sed '$ s/,$//' >> tree.json
printf ']\n' >> tree.json
