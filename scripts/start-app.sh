#!/bin/bash

# Define color codes
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Store initial directory and script directory
INITIAL_DIR=$(pwd)
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Check if we're in scripts, client, or server directory and navigate up one level
current_directory=$(basename $(pwd))
if [[ "$current_directory" =~ ^(scripts|client|server|server-java)$ ]]; then
    cd ..
fi

echo "Starting API (Spring Boot) server..."

# Build and start Spring Boot server
cd server-java || {
    echo "Error: server-java directory not found"
    cd "$INITIAL_DIR"
    exit 1
}
./gradlew bootRun &

# Store the Java server process ID
SERVER_PID=$!

echo "Starting client (Astro)..."
cd ../client || {
    echo "Error: client directory not found"
    cd "$INITIAL_DIR"
    exit 1
}
npm install
npm run dev -- --no-clearScreen &

# Store the SvelteKit server process ID
CLIENT_PID=$!

# Sleep for 3 seconds
sleep 5

# Display the server URLs
echo -e "\n${GREEN}Server (Spring Boot) running at: http://localhost:5100${NC}"
echo -e "${GREEN}Client (Astro) server running at: http://localhost:4321${NC}\n"

echo "Ctl-C to stop the servers"

# Function to handle script termination
cleanup() {
    echo "Shutting down servers..."
    
    # Send SIGTERM first to allow graceful shutdown
    kill -TERM $SERVER_PID 2>/dev/null
    kill -TERM $CLIENT_PID 2>/dev/null
    
    # Wait briefly for graceful shutdown
    sleep 2
    
    # Then force kill if still running
    if ps -p $SERVER_PID > /dev/null 2>&1; then
        pkill -P $SERVER_PID 2>/dev/null
        kill -9 $SERVER_PID 2>/dev/null
    fi
    
    if ps -p $CLIENT_PID > /dev/null 2>&1; then
        pkill -P $CLIENT_PID 2>/dev/null
        kill -9 $CLIENT_PID 2>/dev/null
    fi

    # Return to initial directory
    cd "$INITIAL_DIR"
    exit 0
}

# Trap multiple signals
trap cleanup SIGINT SIGTERM SIGQUIT EXIT

# Keep the script running
wait