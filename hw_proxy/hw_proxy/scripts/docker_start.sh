#!/bin/sh
set -e

# Start the FastAPI server
if [ "$VSCODE_DEBUG" = "true" ]; then
  echo "🔍 Starting under vscode debugpy…"
  # Wait for VS Code to attach before running Uvicorn
  if ! python -m debugpy \
    --listen 0.0.0.0:8015 \
    --wait-for-client \
    -m uvicorn hw_proxy.main:app \
      --host 0.0.0.0 --port 8015 --reload; then
        echo "Uvicorn failed to start. Dropping to a shell for debugging."
        exit 1  # Ensure the script exits if needed
    fi
else
    if ! uvicorn hw_proxy.main:app --host 0.0.0.0 --port 8015 --reload --proxy-headers; then
        echo "Uvicorn failed to start. Dropping to a shell for debugging."
        exit 1  # Ensure the script exits if needed
    fi
fi