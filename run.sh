#!/bin/bash
# Set environment (dev by default)
export ENVIRONMENT=${ENVIRONMENT:-dev}

# Load the appropriate .env file
# This properly handles quoted values with equals signs and special characters
if [ -f ".env.${ENVIRONMENT}" ]; then
    set -a  # Automatically export all variables
    # Read and export each line, handling quoted values correctly
    # Process substitution ensures variables are set in current shell
    while IFS= read -r line || [ -n "$line" ]; do
        # Skip comments and empty lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// }" ]] && continue
        # Export the line - shell will properly parse KEY="VALUE" or KEY=VALUE
        export "$line"
    done < <(grep -v '^[[:space:]]*#' ".env.${ENVIRONMENT}" | grep -v '^[[:space:]]*$')
    set +a  # Turn off automatic export
fi

# Set OpenTelemetry environment variables if not already set
# These can be overridden by values in .env files
export OTEL_RESOURCE_ATTRIBUTES=${OTEL_RESOURCE_ATTRIBUTES:-"service.name=fastapi-app"}
export OTEL_EXPORTER_OTLP_ENDPOINT=${OTEL_EXPORTER_OTLP_ENDPOINT:-""}
export OTEL_EXPORTER_OTLP_HEADERS=${OTEL_EXPORTER_OTLP_HEADERS:-""}
export OTEL_EXPORTER_OTLP_PROTOCOL=${OTEL_EXPORTER_OTLP_PROTOCOL:-"grpc"}

# Optional: Print OpenTelemetry config for debugging
# Set DEBUG_OTEL=true to enable
if [ "${DEBUG_OTEL:-false}" = "true" ]; then
    echo "OpenTelemetry Configuration:"
    echo "  OTEL_RESOURCE_ATTRIBUTES: ${OTEL_RESOURCE_ATTRIBUTES}"
    echo "  OTEL_EXPORTER_OTLP_ENDPOINT: ${OTEL_EXPORTER_OTLP_ENDPOINT}"
    echo "  OTEL_EXPORTER_OTLP_PROTOCOL: ${OTEL_EXPORTER_OTLP_PROTOCOL}"
    if [ -n "${OTEL_EXPORTER_OTLP_HEADERS}" ]; then
        echo "  OTEL_EXPORTER_OTLP_HEADERS: [SET]"
    else
        echo "  OTEL_EXPORTER_OTLP_HEADERS: [NOT SET]"
    fi
fi

# Run the application with OpenTelemetry instrumentation
# Note: We don't use --reload as it breaks OpenTelemetry instrumentation
# If you need hot-reload for development, use --reload but be aware it may break telemetry
poetry run opentelemetry-instrument uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-9000}

