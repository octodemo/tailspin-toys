#!/bin/bash

# Setup environment: client Node.js dependencies

# Determine project root
if [[ $(basename $(pwd)) == "scripts" ]]; then
    PROJECT_ROOT=$(pwd)/..
else
    PROJECT_ROOT=$(pwd)
fi

cd "$PROJECT_ROOT" || exit 1

echo "Installing client dependencies..."
cd client || exit 1
npm install
npx playwright install

# Return to project root
cd "$PROJECT_ROOT"
