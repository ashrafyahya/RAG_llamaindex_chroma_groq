# Docker Deployment Guide

This guide explains how to run the Agentic AI project using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (usually included with Docker Desktop)

## Important Note for Windows Users

If you get an error like "docker-compose is not recognized", try using `docker compose` (without hyphen) instead of `docker-compose`. Modern Docker Desktop versions use Docker Compose V2 which uses the space syntax.

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Clone and navigate to the project directory:**
   ```bash
   cd agentic_ai_project
   ```

2. **Build and run the application:**
   ```bash
   # For Docker Compose V2 (newer versions, Windows/Linux/Mac):
   docker compose up --build
   
   # For Docker Compose V1 (older versions):
   docker-compose up --build
   ```

3. **Access the application:**
   Open your browser and go to `http://localhost:8504`

4. **Stop the application:**
   ```bash
   # Docker Compose V2:
   docker compose down
   
   # Docker Compose V1:
   docker-compose down
   ```

### Option 2: Using Docker directly

1. **Build the Docker image:**
   ```bash
   docker build -t agentic-ai .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8501:8501 \
     -v $(pwd)/chroma_db:/app/chroma_db \
     -v $(pwd)/data:/app/data \
     --name agentic-ai-app \
     agentic-ai
   ```

3. **Access the application:**
   Open your browser and go to `http://localhost:8501`

## Configuration

### Environment Variables

You can customize the application behavior using environment variables:

- `STREAMLIT_SERVER_PORT`: Port for the Streamlit server (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Server address (default: 0.0.0.0)
- `PYTHONPATH`: Python path (default: /app)

### Persistent Data

The Docker setup includes persistent volumes for:
- **ChromaDB database**: `./chroma_db` - Stores your vector embeddings
- **Document data**: `./data` - Stores uploaded documents
- **User cache**: Docker volume `agentic_ai_cache` - Stores encrypted API keys and settings

### API Keys

API keys are securely stored in the container's persistent cache. Configure them through the application's Settings modal once it's running.

## Development

### Development with Docker Compose

For development, you can mount the source code as a volume:

```yaml
# Add this to docker-compose.yml under the agentic-ai service volumes section:
volumes:
  - .:/app
  - ./chroma_db:/app/chroma_db
  - ./data:/app/data
```

Then run with:
```bash
# Docker Compose V2:
docker compose up --build

# Docker Compose V1:
docker-compose up --build
```

### Debugging

To access the container shell for debugging:
```bash
docker exec -it agentic-ai-app /bin/bash
```

## Production Deployment

### Security Considerations

1. **API Keys**: Ensure API keys are properly configured and secured
2. **Network**: Consider using Docker networks for multi-container setups
3. **Volumes**: Backup your ChromaDB and data volumes regularly
4. **Updates**: Regularly update the base image and dependencies

### Scaling

For production scaling, consider:
- Using a reverse proxy (nginx)
- Implementing load balancing
- Using external databases for larger datasets
- Monitoring and logging solutions

### Resource Limits

You can add resource limits to the docker-compose.yml:

```yaml
services:
  agentic-ai:
    # ... other configuration
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port mapping in docker-compose.yml
2. **Permission issues**: Ensure Docker has proper permissions for volume mounts
3. **Memory issues**: Increase Docker's memory allocation
4. **Build failures**: Check internet connection and try rebuilding without cache:
   ```bash
   # Docker Compose V2:
   docker compose build --no-cache
   
   # Docker Compose V1:
   docker-compose build --no-cache
   ```

### Logs

To view application logs:
```bash
# Docker Compose V2:
docker compose logs -f agentic-ai

# Docker Compose V1:
docker-compose logs -f agentic-ai
```

### Health Check

The container includes a health check. Monitor container health with:
```bash
docker ps
```

Look for "healthy" status in the STATUS column.

## Cleanup

To completely remove the application and its data:

```bash
# Stop and remove containers
# Docker Compose V2:
docker compose down
# Docker Compose V1:
docker-compose down

# Remove volumes (WARNING: This will delete all your data!)
# Docker Compose V2:
docker compose down -v
# Docker Compose V1:
docker-compose down -v

# Remove images
docker rmi agentic-ai-app_agentic-ai
```