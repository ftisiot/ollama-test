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
ollama pull gemma3:1b

echo "Model pulled successfully. Starting web interface..."
# Start web server in the background
cd /app && python3 -m http.server 8080 &

echo "Web interface available at http://localhost:8080"
echo "Ollama API available at http://localhost:11434"
echo "Keeping servers running..."
# Keep the servers running
wait
