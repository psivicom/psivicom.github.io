#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

ZULU_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")
# Git branch names cannot contain colons. Replace them with hyphens.
BRANCH_SAFE_TIME=$(echo "$ZULU_TIME" | tr ':' '-')
BRANCH_NAME="wendy/dream-autonomous-${BRANCH_SAFE_TIME}"

log() {
    echo "[${ZULU_TIME}] [WENDY-AUTOMATOR] $1"
}

error_exit() {
    log "FATAL: $1"
    exit 1
}

log "Initializing autonomous Git push..."

if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    error_exit "Not a git repository. Cannot push dream."
fi

git config --local user.name "WENDY Autonomous Agent"
git config --local user.email "wendy@psivi.com"

log "Creating branch: ${BRANCH_NAME}"
git checkout -b "${BRANCH_NAME}" || error_exit "Failed to create branch."

log "Staging generated source files..."
git add src/ || error_exit "Failed to stage src/ directory."

if git diff --staged --quiet; then
    log "No changes detected. Aborting push."
    git checkout main
    git branch -D "${BRANCH_NAME}"
    exit 0
fi

log "Committing dream to repository..."
git commit -m "feat(wendy): autonomous dream generation at ${ZULU_TIME}" || error_exit "Commit failed."

log "Pushing to origin..."
git push -u origin "${BRANCH_NAME}" || error_exit "Push failed."

log "Autonomous push completed successfully."
