#######################################################################
#                           BUILDER STAGE                             #
#######################################################################
# Use a small, secure base image
FROM python:3.11-slim AS builder

# Configure Poetry behavior
ENV POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Install only the tools required to install dependencies.
# No build-essential since your project has pure-Python deps.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry using the official installer script.
# This avoids pip conflicts and matches Poetry’s recommended method.
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH so we can run `poetry`
ENV PATH="/root/.local/bin:$PATH"

# All build-related work will happen under /app
WORKDIR /app

# Copy dependency definitions first to maximize docker layer caching.
# If code changes but dependencies do not, Docker won’t reinstall deps.
COPY pyproject.toml poetry.lock* ./

# Install dependencies into the *system environment* (not .venv).
# Use --no-root to skip installing the project itself (we'll copy the code separately).
# This is the recommended approach for Docker: cleaner, smaller images.
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi --no-root \
    && rm -rf $POETRY_CACHE_DIR

# Copy your application code.
# This is done *after* dependency installation to avoid invalidating cache.
COPY ./app ./app


#######################################################################
#                           RUNTIME STAGE                             #
#######################################################################
# Start a clean, minimal image for final runtime.
FROM python:3.11-slim AS runtime

# Force Python to run in full-buffered stdout/stderr mode.
# Ensures consistent logs and avoids writing .pyc files.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create an unprivileged user for security.
# Never run production containers as root unless absolutely necessary.
RUN useradd -m -u 1000 appuser

# Set the working directory where the app will run.
WORKDIR /app

# Copy system-level dependencies from builder stage.
# This includes installed Python packages only.
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11

# Copy Python entrypoints (e.g., uvicorn) from builder.
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the FastAPI application code itself.
COPY --from=builder /app/app /app/app

# Switch to non-root user.
USER appuser

# Expose the port Uvicorn will listen on.
EXPOSE 9000

# Define the container health check.
# The container orchestration platform will use this to verify health.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:9000/health')"

# Default command to start FastAPI with Uvicorn.
# Environment variables should be set at runtime (via docker run -e or docker-compose)
# The app will use ENVIRONMENT variable to load the appropriate .env file
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]
