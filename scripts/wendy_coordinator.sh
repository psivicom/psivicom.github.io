#!/usr/bin/env bash
# wendy_coordinator.sh - Shared coordination for all WENDY workflows
# SPDX-License-Identifier: EUPL-1.2

set -euo pipefail

STATE_FILE=".wendy_state.json"
LOCK_FILE=".wendy_lock"

# Acquire lock (prevent concurrent workflow conflicts)
acquire_lock() {
  local max_wait=60
  local waited=0
  
  while [ -f "$LOCK_FILE" ] && [ $waited -lt $max_wait ]; do
    echo "⏳ Waiting for lock (another workflow running)..."
    sleep 5
    waited=$((waited + 5))
  done
  
  if [ -f "$LOCK_FILE" ]; then
    echo "❌ Lock timeout. Skipping this run."
    exit 0
  fi
  
  echo "$$" > "$LOCK_FILE"
  trap 'rm -f "$LOCK_FILE"' EXIT
  echo "🔒 Lock acquired"
}

# Update state file
update_state() {
  local workflow="$1"
  local status="$2"
  local details="${3:-}"
  
  # Ensure state file exists
  if [ ! -f "$STATE_FILE" ]; then
    echo '{"last_heartbeat":"","workflows":{},"learned_patterns":{},"pending_actions":[]}' > "$STATE_FILE"
  fi
  
  # Update with jq if available, otherwise use python
  if command -v jq &> /dev/null; then
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")
    jq --arg wf "$workflow" \
       --arg st "$status" \
       --arg ts "$timestamp" \
       --arg dt "$details" \
       '.last_heartbeat = $ts | .workflows[$wf] = {"last_run": $ts, "status": $st, "details": $dt}' \
       "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
  elif command -v python3 &> /dev/null; then
    python3 << EOF
import json, sys
from datetime import datetime, timezone

with open("$STATE_FILE", 'r') as f:
    state = json.load(f)

timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
state["last_heartbeat"] = timestamp
state["workflows"]["$workflow"] = {
    "last_run": timestamp,
    "status": "$status",
    "details": "$details"
}

with open("$STATE_FILE", 'w') as f:
    json.dump(state, f, indent=2)
EOF
  else
    echo "⚠️ No jq or python3 available. Cannot update state."
  fi
}

# Check if action is needed (idempotency)
needs_action() {
  local action_type="$1"
  
  if [ ! -f "$STATE_FILE" ]; then
    return 0  # No state = needs action
  fi
  
  # Check pending actions
  if command -v jq &> /dev/null; then
    local pending=$(jq -r ".pending_actions[] | select(.type == \"$action_type\") | .type" "$STATE_FILE" 2>/dev/null || echo "")
    if [ -n "$pending" ]; then
      return 0  # Action pending
    fi
  fi
  
  return 1  # No action needed
}

# Race-safe push (universal)
safe_push() {
  local commit_msg="$1"
  local max_attempts=3
  local attempt=1
  
  git add -A
  
  if git diff --staged --quiet; then
    echo "✅ Nothing to commit"
    return 0
  fi
  
  git commit -m "$commit_msg [skip ci]"
  
  while [ $attempt -le $max_attempts ]; do
    echo "📤 Push attempt $attempt/$max_attempts..."
    if git push origin main 2>&1; then
      echo "✅ Push succeeded"
      return 0
    fi
    echo "⚠️ Push rejected. Rebasing..."
    git pull --rebase --autostash origin main || {
      echo "❌ Rebase failed"
      git rebase --abort
      return 1
    }
    attempt=$((attempt + 1))
    sleep $((attempt * 2))
  done
  
  echo "❌ Push failed after $max_attempts attempts"
  return 1
}

# Export functions
export -f acquire_lock update_state needs_action safe_push
export STATE_FILE LOCK_FILE
