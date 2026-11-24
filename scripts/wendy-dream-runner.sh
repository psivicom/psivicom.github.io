#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# [AXIOM_9] Banned Timestamps in Dreams.
# We use the Manifest Hash to identify the dream state, not chronological time.
MANIFEST_HASH=$(sha256sum .wendy_manifest.gmi 2>/dev/null | cut -d' ' -f1 | head -c8 || echo "default")
BRANCH_NAME="wendy/dream-autonomous-${MANIFEST_HASH}"

log() {
  echo "[WENDY-AUTOMATOR] $1"
}

error_exit() {
  log "FATAL: $1"
  exit 1
}

log "Initializing autonomous dream push..."
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  error_exit "Not a git repository. Cannot push dream."
fi

# Check if this exact dream has already been processed
git fetch origin '+refs/heads/*:refs/remotes/origin/*' || true
if git ls-remote --exit-code --heads origin "$BRANCH_NAME" > /dev/null 2>&1; then
  log "Dream branch $BRANCH_NAME already exists. Temporal Sabotage prevented. Exiting."
  exit 0
fi

if git log origin/main --grep="feat(wendy): autonomous dream materialization ${MANIFEST_HASH}" -n 1 > /dev/null 2>&1; then
  log "Manifest already crystallized. Resting."
  exit 0
fi

git config --local user.name "WENDY Autonomous Agent"
git config --local user.email "wendy@psivi.com"

log "Creating branch: ${BRANCH_NAME}"
git checkout -b "${BRANCH_NAME}" || error_exit "Failed to create branch."

log "Staging generated source files..."
git add src/ || error_exit "Failed to stage src/ directory."

if git diff --staged --quiet; then
  log "No semantic changes detected. Aborting push."
  git checkout main
  git branch -D "${BRANCH_NAME}"
  exit 0
fi

log "Committing dream to repository..."
# NO TIMESTAMP IN COMMIT MESSAGE [AXIOM_9]
git commit -m "feat(wendy): autonomous dream materialization ${MANIFEST_HASH}" || error_exit "Commit failed."

log "Pushing to origin..."
git push -u origin "${BRANCH_NAME}" || error_exit "Push failed."

log "Autonomous push completed successfully."
