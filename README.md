# JouleJournal - Energy Management Dashboard

A web application for monitoring, analyzing, and reporting on energy consumption, generation, costs, and the financial Return on Investment (ROI) of a solar panel installation.

## Features

- **Dynamic Dashboard:** Real-time visualization of your energy data.
- **KPI Overview:** Key Performance Indicators for the current year, including net costs and self-sufficiency.
- **ROI Tracker:** A visual progress bar showing the payback period of your investment.
- **Interactive Charts (Chart.js):**
    - **Energy Balance:** Stacked bar chart of Import, Export, and Self-Consumption.
    - **Consumption Breakdown:** Pie chart showing consumption from the house vs. an electric car.
    - **Production vs. Forecast:** Line chart comparing actual production with the forecast.
- **Robust Backend API:** Built with FastAPI for fast and reliable data processing.
- **Containerized:** Fully configured to run with Docker for a simple and consistent setup.

## Requirements

- [Docker](https://www.docker.com/get-started)
- Docker Compose V1 (`docker-compose`) or V2 (`docker compose`)

## Deployment in Portainer (Recommended)

For a simple and managed deployment, you can run this application as a "Stack" in Portainer.

1.  **Navigate to Stacks:** Log in to your Portainer instance and go to "Stacks" in the menu.
2.  **Add a new Stack:** Click on "Add stack".
3.  **Configure the Stack:**
    *   **Name:** Give your stack a name (e.g., `joulejournal`).
    *   **Repository:** Select "Repository" as the build method.
    *   **Repository URL:** Paste the URL of this GitHub repository.
    *   **Compose path:** Ensure the path is set to `docker-compose.yml`.
4.  **Environment Variables:**
    Add the following environment variables. These are essential for the database connection. Click "Add environment variable" for each variable.
    *   `POSTGRES_USER`: The username for your database (e.g., `joule`).
    *   `POSTGRES_PASSWORD`: A strong password for the database user.
    *   `POSTGRES_DB`: The name of the database (e.g., `joulejournal`).
5.  **Deploy the Stack:** Click "Deploy the stack" and wait for Portainer to build the images and start the containers.
6.  **Database Setup:** Database migrations and data seeding now happen automatically when the `backend` container starts.
7.  **View the Application:** Your application is now available on the hostname of your Portainer server on port 8000 (e.g., `http://<your-server-ip>:8000`).

## Installation and Startup

You can run this project in two ways:

1.  **With Docker (Recommended):** A containerized setup using PostgreSQL.
2.  **Locally without Docker:** A local setup using a SQLite database.

---

### 1. With Docker (uses PostgreSQL)

This is the recommended way to run the project, as it sets up a consistent environment with a PostgreSQL database.

1.  **Clone the Repository**
    ```bash
    git clone <repository_url>
    cd joulejournal-project
    ```

2.  **Create a `.env` file**
    Create a file named `.env` in the project root and add the following variables. These are used by `docker-compose.yml` to configure the PostgreSQL database.
    ```
    POSTGRES_USER=joule
    POSTGRES_PASSWORD=a_strong_password
    POSTGRES_DB=joulejournal
    PORT=8000
    ```

3.  **Build and Start the Application**
    This command builds the Docker image for the backend and starts all services (backend and database).
    ```bash
    docker-compose up --build
    ```
    *Wait for the output to indicate that the Uvicorn server is running.*

    The `backend` service will automatically:
    - Run database migrations using Alembic.
    - Seed the database with initial data from `scripts/seed_db.py`.

4.  **View the Application**
    - **Frontend Dashboard:** [http://localhost:8000](http://localhost:8000)
    - **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 2. Locally without Docker (uses SQLite)

This setup is useful for local development and testing. It uses a simple SQLite database file (`joulejournal.db`).

1.  **Clone the Repository**
    ```bash
    git clone <repository_url>
    cd joulejournal-project
    ```

2.  **Set up a Virtual Environment**
    It's recommended to use a virtual environment to manage dependencies.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run Database Migrations**
    This will create the `joulejournal.db` file and set up the database schema.
    ```bash
    alembic upgrade head
    ```

5.  **Seed the Database**
    This will populate the database with initial data.
    ```bash
    python scripts/seed_db.py
    ```

6.  **Start the Application**
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000
    ```

7.  **View the Application**
    - **Frontend Dashboard:** [http://localhost:8000](http://localhost:8000)
    - **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

## Project Structure

```
.
├── .env              # (Optional) Environment variables for Docker setup
├── app/              # Backend FastAPI application
├── scripts/          # Helper scripts (e.g., seed_db.py)
├── static/           # Static files (CSS, JS)
├── templates/        # HTML templates
├── alembic/          # Database migrations
├── joulejournal.db   # SQLite database file (used for local development)
├── Dockerfile
└── docker-compose.yml
```

## Stopping the Application

To stop the containers, press `Ctrl+C` in the terminal where `docker-compose up` is running, or execute:
```bash
docker-compose down
```
To also remove the database volume (CAUTION: THIS WILL DELETE ALL DATA), use:
```bash
docker-compose down -v
```
