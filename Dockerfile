# Start from a modern, slim Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application source code into the container
COPY . /app

# Set an argument for the port with a default value
ARG PORT=5201
# Set the environment variable for the port
ENV PORT=${PORT}

# Expose the port the app will run on
EXPOSE ${PORT}

# Command to run the application
# The host 0.0.0.0 makes it accessible from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${PORT}"]
