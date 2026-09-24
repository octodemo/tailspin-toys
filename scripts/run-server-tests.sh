#!/bin/bash

# run-server-tests.sh — run the Flask backend unit tests.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if ! "$SCRIPT_DIR/setup-env.sh" --check server; then
  exit 1
fi

# shellcheck source=/dev/null
source "$PROJECT_ROOT/venv/bin/activate"

cd "$PROJECT_ROOT/server" || exit 1
echo "Running server tests..."
python3 -m unittest discover -s tests -p "*.py"
