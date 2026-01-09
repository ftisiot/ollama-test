FROM ollama/ollama:latest

# Set working directory
WORKDIR /app

# Expose the default Ollama port
EXPOSE 11434

# The base image already includes Ollama, so we can use it directly
# You can add additional setup commands here if needed

