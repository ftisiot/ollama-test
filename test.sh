#!/bin/bash

echo "=== Testing if Ollama server is reachable ==="

# Check if server is responding
if curl -s -f http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Server is UP and REACHABLE!"
    echo ""
    echo "Server response:"
    curl -s http://localhost:11434/api/tags | jq '.' 2>/dev/null || curl -s http://localhost:11434/api/tags
else
    echo "❌ Server is NOT reachable"
    echo ""
    echo "Make sure the container is running:"
    echo "  docker ps | grep ollama"
    echo ""
    echo "If not running, start it with:"
    echo "  docker run -d -p 11434:11434 --name ollama-test ollama-test"
fi
