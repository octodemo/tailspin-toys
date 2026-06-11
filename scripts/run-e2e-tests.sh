#!/bin/bash

# run-e2e-tests.sh — run the Playwright end-to-end tests.
# Playwright's webServer config starts both the Flask backend and the Astro
# dev server, so all backend prerequisites must be in place too.

set -u

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if ! "$SCRIPT_DIR/setup-env.sh" --check e2e; then
  exit 1
fi

cd "$PROJECT_ROOT/client" || exit 1

echo -e "${BLUE}Starting Tailspin Toys E2E Tests${NC}"
echo -e "${GREEN}Starting servers...${NC}"
echo -e "  • Flask API server: http://localhost:5100"
echo -e "  • Astro client server: http://localhost:4321"
echo ""
echo -e "${BLUE}Running tests:${NC}"

npm run test:e2e
TEST_EXIT_CODE=$?

echo ""
echo -e "${BLUE}E2E tests completed with exit code: $TEST_EXIT_CODE${NC}"
exit $TEST_EXIT_CODE
