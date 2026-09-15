<!--
  Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | CC BY-SA 4.0
-->
gitignore


# .gitignore
.tree.hash
*.zip

One fix: don’t ignore .tree.hash if you want it committed. If it should live in the repo, remove it from .gitignore and keep only:

gitignore


*.zip
