# Use a more full-featured Python image based on Debian
FROM python:3.9-bookworm

# Set the working directory in the container
WORKDIR /app

# Ensure our source tree is importable without relying on Compose
ENV PYTHONPATH=/app \
    POETRY_VIRTUALENVS_CREATE=false

# Install system dependencies required for building some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy only the files that define the dependencies
COPY pyproject.toml poetry.lock* /app/

# Install project dependencies into the system environment (no venv)
# Using --no-lock to resolve dependencies from pyproject.toml
# Using --no-root because we only need the dependencies, not the project itself installed.
RUN poetry install --no-root --without dev --no-interaction --no-ansi

# Copy the rest of the application code into the container
COPY ./app /app/app
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/alembic.ini

# Default command (may be overridden by compose)
CMD ["bash", "-lc", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
