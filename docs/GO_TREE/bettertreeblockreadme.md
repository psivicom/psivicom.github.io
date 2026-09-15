<!--
  Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | CC BY-SA 4.0
-->
One important fix: don’t put the tree block inside a fenced code block in your real README template unless you want it displayed as literal text. The actual marker region should just contain the raw generated tree content.

Use this instead:

<!-- TREE:START -->
psivicom.github.io/
- README.md
- TREE.md
<!-- TREE:END -->
