One important fix: don’t put the tree block inside a fenced code block in your real README template unless you want it displayed as literal text. The actual marker region should just contain the raw generated tree content.

Use this instead:

<!-- TREE:START -->
psivicom.github.io/
- README.md
- TREE.md
<!-- TREE:END -->
