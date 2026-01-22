# Ollama Docker Web Interface

A Dockerized web application that provides a beautiful, interactive chat interface for interacting with Ollama LLM models. This project packages Ollama with a modern web UI, allowing you to chat with language models through your browser.

## Features

- 🤖 **Web-based Chat Interface** - Beautiful, modern UI for chatting with LLM models
- 📝 **Markdown Rendering** - Properly renders markdown in LLM responses (code blocks, headers, lists, etc.)
- 💬 **Conversation Context** - Automatically includes previous conversation history in each request
- 🔍 **Automatic Web Browsing** - Automatically searches and browses the internet when LLM lacks information
- 🔄 **Model Selection** - Switch between different models (gemma3:270m, gemma3:1b)
- 🐳 **Dockerized** - Easy deployment with Docker
- 🔒 **Single Port** - Only exposes port 8080 (Ollama API is proxied internally)
- 💾 **Configurable Storage** - Models stored in `/tmp/models` (configurable)

## Prerequisites

- Docker installed and running
- Docker Desktop (for macOS/Windows) or Docker Engine (for Linux)

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t ollama-test .
```

### 2. Run the Container

```bash
docker run -d -p 8080:8080 --name ollama-test ollama-test
```

### 3. Access the Web Interface

Open your browser and navigate to:
```
http://localhost:8080
```

The container will automatically:
- Start the Ollama server
- Pull the required models (gemma3:270m and gemma3:1b)
- Start the web interface with proxy server

**Note:** The first run may take a few minutes while models are downloaded. You can monitor progress with:
```bash
docker logs -f ollama-test
```

## Usage

### Chat Interface

1. Select a model from the dropdown (gemma3:270m or gemma3:1b)
2. Type your message in the input field
3. Press Enter or click Send
4. The LLM response will appear with proper markdown rendering

### Conversation Context

The interface automatically includes previous conversation history in each request, allowing the LLM to maintain context across multiple messages. Previous questions and answers are formatted as a numbered list in the prompt.

### Automatic Web Browsing

The system automatically searches and browses the internet when the LLM indicates it doesn't have enough information:

- When the LLM responds with phrases like "I don't know", "I'm not sure", or "I don't have access to", the system automatically:
  1. Extracts a search query from your question
  2. Performs a web search using DuckDuckGo to find relevant URLs
  3. Automatically browses the top search result pages
  4. Extracts content from the browsed pages
  5. Provides the LLM with the browsed content
  6. Generates an updated answer with the new information

The browsed content is displayed in the chat, and the LLM uses it to provide comprehensive, up-to-date answers. This allows the LLM to provide current information even when it doesn't have it in its training data.

**Note:** Web browsing extracts text content from web pages (up to 5000 characters) and includes it in the LLM prompt for context-aware responses.

### Testing the Server

To check if the server is running:

```bash
curl http://localhost:8080/api/tags
```

Or use the included test script:
```bash
./test.sh
```

## Project Structure

```
.
├── Dockerfile              # Docker image configuration
├── docker-entrypoint.sh    # Startup script (starts Ollama, pulls models, starts web server)
├── server.py              # Python proxy server (forwards API requests to Ollama)
├── index.html             # Web interface (HTML, CSS, JavaScript)
├── test.sh                # Test script to verify server is running
└── README.md              # This file
```

## Configuration

### Change Models

Edit `docker-entrypoint.sh` to modify which models are pulled:

```bash
ollama pull gemma3:270m
ollama pull gemma3:1b
```

### Change Model Storage Location

Edit `Dockerfile` to change where models are stored:

```dockerfile
ENV OLLAMA_MODELS=/tmp/models
```

### Persist Models with Volume

To persist models across container restarts, mount a volume:

```bash
docker run -d -p 8080:8080 \
  -v ollama-models:/tmp/models \
  --name ollama-test ollama-test
```

Or use a host directory:

```bash
docker run -d -p 8080:8080 \
  -v /path/on/host:/tmp/models \
  --name ollama-test ollama-test
```

## Container Management

### View Logs

```bash
docker logs -f ollama-test
```

### Stop Container

```bash
docker stop ollama-test
```

### Start Container

```bash
docker start ollama-test
```

### Remove Container

```bash
docker rm -f ollama-test
```

### Check Memory Usage

```bash
docker stats --no-stream ollama-test
```

## How It Works

1. **Dockerfile** - Builds a container based on `ollama/ollama:latest`
2. **Entrypoint Script** - Starts Ollama server, waits for it to be ready, pulls models, then starts the web server
3. **Proxy Server** - Python server that serves the HTML interface and proxies API requests to Ollama (running on port 11434 internally)
4. **Web Interface** - Single-page application that:
   - Renders markdown responses
   - Maintains conversation history
   - Sends requests through the proxy to Ollama

## Ports

- **8080** - Web interface and API proxy (exposed to host)
- **11434** - Ollama API (internal only, not exposed)

## Troubleshooting

### Container won't start

Check logs:
```bash
docker logs ollama-test
```

### Port already in use

If port 8080 is already in use, change it:
```bash
docker run -d -p 8081:8080 --name ollama-test ollama-test
```
Then access at `http://localhost:8081`

### Models not loading

Check if models are being pulled:
```bash
docker logs ollama-test | grep -i "pull\|model"
```

### Permission errors

Make sure Docker Desktop is running and you have proper permissions.

## License

This project is provided as-is for educational and development purposes.
