gitignore


# .gitignore
.tree.hash
*.zip

One fix: don’t ignore .tree.hash if you want it committed. If it should live in the repo, remove it from .gitignore and keep only:

gitignore


*.zip
