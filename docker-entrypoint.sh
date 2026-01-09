#!/bin/bash
set -e

# Start Ollama server in the background
ollama serve &

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
timeout=30
counter=0
while ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    sleep 1
    counter=$((counter + 1))
    if [ $counter -ge $timeout ]; then
        echo "Error: Ollama failed to start within $timeout seconds"
        exit 1
    fi
done

echo "Ollama is ready. Pulling model..."
# Pull the model
ollama pull gemma3:270m

echo "Model pulled successfully. Keeping server running..."
# Keep the server running
wait
