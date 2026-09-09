from pathlib import Path

IGNORE = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "TREE.md"}

def walk(path, prefix="", seen=None):
    if seen is None:
        seen = set()

    real = path.resolve()
    if real in seen:
        return []
    seen.add(real)

    items = sorted(
        [p for p in path.iterdir() if p.name not in IGNORE and not p.is_symlink()]
    )

    lines = []
    for i, item in enumerate(items):
        connector = "└── " if i == len(items) - 1 else "├── "
        lines.append(prefix + connector + item.name)

        if item.is_dir():
            extension = "    " if i == len(items) - 1 else "│   "
            lines.extend(walk(item, prefix + extension, seen))
    return lines

root = Path(".")
output = ["```text", f"{root.name}/"]
output.extend(walk(root))
output.append("```")

Path("TREE.md").write_text("\n".join(output) + "\n", encoding="utf-8")
print("TREE.md updated")
