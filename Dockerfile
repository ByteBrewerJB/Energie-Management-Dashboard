# Start from a modern, slim Python base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install Poetry (pin to lockfile version) and upgrade pip
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir poetry==2.1.3

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the dependency files
COPY pyproject.toml poetry.lock ./

# Configure Poetry to install into the system environment (no venv in container)
ENV POETRY_VIRTUALENVS_CREATE=false

# Install the Python dependencies using Poetry
# --no-interaction: Do not ask any interactive question
# --no-root: Do not install the root package (the project itself)
RUN poetry install --no-interaction --no-root

# Copy the entire application source code into the container
COPY . /app

# Set the project root as the PYTHONPATH
ENV PYTHONPATH /app

# Set an argument for the port with a default value
ARG PORT=5201
# Set the environment variable for the port
ENV PORT=${PORT}

# Expose the port the app will run on
EXPOSE ${PORT}

# Command to run the application
# The host 0.0.0.0 makes it accessible from outside the container
# Use shell form to correctly expand the PORT variable
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
