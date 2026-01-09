FROM ollama/ollama:latest

# Set working directory
WORKDIR /app

# Expose the default Ollama port
EXPOSE 11434

# Pull the model during build
RUN ollama pull gemma3:270m

# Run the Ollama server
CMD ["ollama", "serve"]

