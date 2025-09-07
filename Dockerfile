# Start from a modern, slim Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy the dependency files
COPY pyproject.toml poetry.lock ./

# Install the Python dependencies using Poetry
# --no-interaction: Do not ask any interactive question
# --no-root: Do not install the root package (the project itself)
# --no-dev: Do not install dev dependencies
RUN poetry install --no-interaction --no-root --no-dev

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

# Command to run the application using poetry's virtual env
# The host 0.0.0.0 makes it accessible from outside the container
# Use shell form to correctly expand the PORT variable
CMD exec poetry run uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
