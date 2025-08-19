#!/bin/bash

# Run end-to-end tests: starts servers and runs Playwright tests

# Determine project root
if [[ $(basename $(pwd)) == "scripts" ]]; then
    PROJECT_ROOT=$(pwd)/..
else
    PROJECT_ROOT=$(pwd)
fi

cd "$PROJECT_ROOT" || exit 1

# Activate virtual environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source "$PROJECT_ROOT/venv/Scripts/activate" || . "$PROJECT_ROOT/venv/Scripts/activate"
else
    source "$PROJECT_ROOT/venv/bin/activate" || . "$PROJECT_ROOT/venv/bin/activate"
fi

# Check if the virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Virtual environment not activated. Running setup-env.sh..."
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        "$PROJECT_ROOT/scripts/setup-env.sh"
    else
        bash "$PROJECT_ROOT/scripts/setup-env.sh"
    fi
    
    # Re-activate virtual environment after setup
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source "$PROJECT_ROOT/venv/Scripts/activate" || . "$PROJECT_ROOT/venv/Scripts/activate"
    else
        source "$PROJECT_ROOT/venv/bin/activate" || . "$PROJECT_ROOT/venv/bin/activate"
    fi
fi

echo "Starting Flask backend server..."
# Start Flask server in background, suppress output
cd "$PROJECT_ROOT/server" || exit 1
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    py app.py > /dev/null 2>&1 &
else
    python3 app.py > /dev/null 2>&1 &
fi
FLASK_PID=$!

# Wait a moment for Flask to start
sleep 3

echo "Starting Astro frontend server..."
# Start Astro server in background, suppress output
cd "$PROJECT_ROOT/client" || exit 1
npm run dev > /dev/null 2>&1 &
ASTRO_PID=$!

# Wait for servers to be ready
echo "Waiting for servers to start..."
sleep 10

# Check if servers are running
echo "Verifying servers are ready..."
if ! kill -0 $FLASK_PID 2>/dev/null; then
    echo "Error: Flask server failed to start"
    exit 1
fi

if ! kill -0 $ASTRO_PID 2>/dev/null; then
    echo "Error: Astro server failed to start"
    exit 1
fi

echo "Servers are ready!"

# Function to cleanup background processes
cleanup() {
    echo "Stopping servers..."
    kill $FLASK_PID 2>/dev/null
    kill $ASTRO_PID 2>/dev/null
    wait $FLASK_PID 2>/dev/null
    wait $ASTRO_PID 2>/dev/null
}

# Set trap to cleanup on script exit
trap cleanup EXIT

echo "Running e2e tests..."
# Run Playwright tests
npm run test:e2e

# Store the exit code
TEST_EXIT_CODE=$?

# Cleanup will be called automatically by the trap
echo "E2E tests completed with exit code: $TEST_EXIT_CODE"
exit $TEST_EXIT_CODE
