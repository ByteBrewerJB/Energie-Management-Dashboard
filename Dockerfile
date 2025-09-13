# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install poetry
# We are using the official installer which is recommended.
# https://python-poetry.org/docs/#installation
RUN pip install poetry

# Copy the dependency files to the working directory
COPY pyproject.toml poetry.lock* /app/

# Install project dependencies
# --no-root is used because we only need the dependencies, not the project itself installed.
# The project code will be mounted as a volume in docker-compose.
RUN poetry install --no-root --no-dev

# Copy the rest of the application code into the container
COPY ./app /app/app

# Command to run the application
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
