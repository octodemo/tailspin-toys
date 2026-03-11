#!/bin/bash

# Run ESLint on the frontend codebase
# This script runs ESLint to check for code quality and consistency issues
# in TypeScript, Astro, and Svelte files.

set -e

# Navigate to the client directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT/client"

echo "Running ESLint..."
npm run lint
echo "ESLint passed!"
