from fastapi import FastAPI
from app.core.logging_config import setup_logging, get_logger
from app.db.session import SessionLocal
from app.api.endpoints import auth, tariffs, cars, journal, batteries, solar_panels, roi
from app import crud
from app.schemas.user import UserCreate

# Set up logging
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="JouleJournal",
    description="A web application for monitoring, analyzing, and reporting energy consumption.",
    version="0.1.0"
)

# Create initial user on startup
@app.on_event("startup")
def startup_event():
    logger.info("Starting up and creating initial user if needed.")
    db = SessionLocal()
    user = crud.user.get_user_by_username(db, username="admin")
    if not user:
        logger.info("Creating admin user.")
        user_in = UserCreate(username="admin", password="admin")
        crud.user.create_user(db=db, user=user_in)
    db.close()

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(tariffs.router, prefix="/api/tariffs", tags=["tariffs"])
app.include_router(cars.router, prefix="/api/cars", tags=["cars"])
app.include_router(journal.router, prefix="/api/journal", tags=["journal"])
app.include_router(batteries.router, prefix="/api/batteries", tags=["batteries"])
app.include_router(solar_panels.router, prefix="/api/solar_panels", tags=["solar_panels"])
app.include_router(roi.router, prefix="/api/roi", tags=["roi"])

@app.get("/")
def read_root():
    """A simple endpoint to confirm the API is running."""
    return {"status": "ok"}


@app.get("/health")
def health_check():
    """
    Health check endpoint to verify that the application is running and can connect to the database.
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "error", "detail": str(e)}
