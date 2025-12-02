#!/bin/bash
# Set environment (dev by default)
export ENVIRONMENT=${ENVIRONMENT:-dev}

# Load the appropriate .env file
if [ -f ".env.${ENVIRONMENT}" ]; then
    export $(cat .env.${ENVIRONMENT} | grep -v '^#' | xargs)
fi

# Run the application
poetry run uvicorn app.main:app --reload --host ${HOST:-0.0.0.0} --port ${PORT:-9000}

