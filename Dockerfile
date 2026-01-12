FROM ollama/ollama:latest

# Set working directory
WORKDIR /app

# Expose the default Ollama port and web interface port
EXPOSE 11434 8080

# Set Ollama to store models in /tmp
ENV OLLAMA_MODELS=/tmp/models

# Install curl and Python (needed for health check and web server)
RUN apt-get update && apt-get install -y curl python3 && rm -rf /var/lib/apt/lists/*

# Create the models directory
RUN mkdir -p /tmp/models

# Copy web interface
COPY index.html /app/index.html

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Use entrypoint script to start server and pull model
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

