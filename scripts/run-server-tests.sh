#!/bin/bash

# Determine project root
if [[ $(basename $(pwd)) == "scripts" || $(basename $(pwd)) == "server-java" ]]; then
    PROJECT_ROOT=$(pwd)/..
else
    PROJECT_ROOT=$(pwd)
fi

# Run Java (Spring Boot) server tests via Gradle
cd "$PROJECT_ROOT/server-java" || exit 1
echo "Running server tests (Spring Boot / Gradle)..."

./gradlew test
