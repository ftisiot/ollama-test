FROM ollama/ollama:latest

# Set working directory
WORKDIR /app

# Expose only the web interface port
EXPOSE 8080

# Set Ollama to store models in /tmp
ENV OLLAMA_MODELS=/tmp/models

# Install curl and Python (needed for health check and web server)
RUN apt-get update && apt-get install -y curl python3 && rm -rf /var/lib/apt/lists/*

# Create the models directory
RUN mkdir -p /tmp/models

# Copy web interface and proxy server
COPY index.html /app/index.html
COPY server.py /app/server.py
RUN chmod +x /app/server.py

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Use entrypoint script to start server and pull model
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

