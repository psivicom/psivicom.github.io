#!/usr/bin/env bash
# safe-push.sh - Universal race-safe git push for all WENDY workflows
# SPDX-License-Identifier: EUPL-1.2
#
# Usage: source scripts/safe-push.sh && safe_push "commit message" [files...]
#
# Handles race conditions where another workflow pushed between checkout and push.

set -e

safe_push() {
  local commit_msg="${1:-chore: auto-commit}"
  shift || true
  local files=("$@")
  
  local max_attempts=3
  local attempt=1
  
  # Stage files (or use pre-staged)
  if [ ${#files[@]} -gt 0 ]; then
    git add "${files[@]}"
  fi
  
  # Check if there's anything to commit
  if git diff --cached --quiet; then
    echo "✅ Nothing to commit"
    return 0
  fi
  
  # Commit
  git commit -m "$commit_msg"
  
  # Race-safe push with retry
  while [ $attempt -le $max_attempts ]; do
    echo "📤 Push attempt $attempt/$max_attempts..."
    
    if git push origin main 2>&1; then
      echo "✅ Push succeeded on attempt $attempt"
      return 0
    fi
    
    echo "⚠️ Push rejected (race condition). Rebasing..."
    if ! git pull --rebase --autostash origin main; then
      echo "❌ Rebase conflict. Aborting."
      git rebase --abort 2>/dev/null || true
      return 1
    fi
    
    attempt=$((attempt + 1))
    sleep $((attempt * 2))  # Exponential backoff: 4s, 6s, 8s
  done
  
  echo "❌ Push failed after $max_attempts attempts"
  return 1
}

# Export so sourced workflows can use it
export -f safe_push
