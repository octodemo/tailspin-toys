#!/bin/bash

# start-app.sh — start the Flask backend and Astro dev server for local development.
# Assumes the environment has been provisioned by scripts/setup-env.sh.

set -u

GREEN='\033[0;32m'
NC='\033[0m'

INITIAL_DIR=$(pwd)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if ! "$SCRIPT_DIR/setup-env.sh" --check app; then
  exit 1
fi

# shellcheck source=/dev/null
source "$PROJECT_ROOT/venv/bin/activate"

# Skip Astro's anonymous telemetry to avoid a writable-config-dir requirement
# (the file write fails in sandboxed environments).
export ASTRO_TELEMETRY_DISABLED=1

echo "Starting API (Flask) server..."
cd "$PROJECT_ROOT/server" || {
    echo "Error: server directory not found"
    cd "$INITIAL_DIR"
    exit 1
}
export FLASK_DEBUG=1
export FLASK_PORT=5100

python3 app.py &
SERVER_PID=$!

echo "Starting client (Astro)..."
cd "$PROJECT_ROOT/client" || {
    echo "Error: client directory not found"
    cd "$INITIAL_DIR"
    exit 1
}
npm run dev -- --no-clearScreen &
CLIENT_PID=$!

sleep 5

echo -e "\n${GREEN}Server (Flask) running at: http://localhost:5100${NC}"
echo -e "${GREEN}Client (Astro) server running at: http://localhost:4321${NC}\n"
echo "Ctl-C to stop the servers"

cleanup() {
    echo "Shutting down servers..."

    kill -TERM $SERVER_PID 2>/dev/null
    kill -TERM $CLIENT_PID 2>/dev/null

    sleep 2

    if ps -p $SERVER_PID > /dev/null 2>&1; then
        pkill -P $SERVER_PID 2>/dev/null
        kill -9 $SERVER_PID 2>/dev/null
    fi

    if ps -p $CLIENT_PID > /dev/null 2>&1; then
        pkill -P $CLIENT_PID 2>/dev/null
        kill -9 $CLIENT_PID 2>/dev/null
    fi

    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        deactivate
    fi

    cd "$INITIAL_DIR"
    exit 0
}

trap cleanup SIGINT SIGTERM SIGQUIT EXIT

wait
