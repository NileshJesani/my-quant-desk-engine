#!/usr/bin/env bash
set -e

# Directory of this script (src/data_ingestion)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Project root is two levels up: src/data_ingestion -> src -> root
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

LOG_FILE="/var/log/myquantdesk-daily.log"

log_msg() {
  echo "[$(date -Iseconds)] $1" | tee -a "$LOG_FILE"
}

log_msg "=== Starting daily Fyers token refresh ==="

# 1) Refresh access token inside the app container
log_msg "Running fyers_auth_token.py --token in container"
docker compose exec -T app python fyers_auth_token.py --token
log_msg "fyers_auth_token.py --token completed in container"

# 2) Rebuild & restart containers so app sees updated .env
log_msg "Running docker compose up -d --build"
docker compose up -d --build
log_msg "docker compose up -d --build completed"

log_msg "=== Daily Fyers token refresh finished ==="