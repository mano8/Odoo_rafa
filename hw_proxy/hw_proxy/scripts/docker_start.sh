#!/bin/sh
set -e

# Start the FastAPI server
if [ "$VSCODE_DEBUG" = "true" ]; then
  echo "Starting under debugpy on port 5679..."
  if ! python -m debugpy \
    --listen 0.0.0.0:5679 \
    --wait-for-client \
    -m uvicorn hw_proxy.main:app \
      --host 0.0.0.0 --port 9002 --reload; then
        echo "Uvicorn failed to start. Dropping to a shell for debugging."
        exit 1
    fi
else
    if ! uvicorn hw_proxy.main:app --host 0.0.0.0 --port 9002 --reload --proxy-headers --forwarded-allow-ips "*"; then
        echo "Uvicorn failed to start. Dropping to a shell for debugging."
        exit 1
    fi
fi