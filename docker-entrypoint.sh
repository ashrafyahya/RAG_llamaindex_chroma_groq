#!/bin/bash
set -e

# Create necessary directories if they don't exist
mkdir -p /app/data /app/chroma_db /app/.streamlit_cache

# Set proper permissions
chmod -R 755 /app/data /app/chroma_db /app/.streamlit_cache

echo "Starting Agentic AI Assistant..."
echo "Application will be available at http://localhost:8501"

# Execute the main command
exec "$@"