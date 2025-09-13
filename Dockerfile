# Use a more full-featured Python image based on Debian
FROM python:3.9-bookworm

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for building some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Copy only the files that define the dependencies
COPY pyproject.toml poetry.lock* /app/

# Install project dependencies
# Using --no-lock to resolve dependencies from pyproject.toml, which is safer across different environments
# Using --no-root because we only need the dependencies, not the project itself installed.
RUN poetry install --no-root --without dev

# Copy the rest of the application code into the container
COPY ./app /app/app
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/alembic.ini

# Command to run the application, including running migrations on startup
CMD ["sh", "-c", "poetry run alembic upgrade head && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
