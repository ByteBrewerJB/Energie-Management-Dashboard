from fastapi import FastAPI
from app.db.session import SessionLocal
from app.api.endpoints import auth, tariffs, cars, journal
from app import crud
from app.schemas.user import UserCreate

app = FastAPI(
    title="JouleJournal",
    description="A web application for monitoring, analyzing, and reporting energy consumption.",
    version="0.1.0"
)

# Create initial user on startup
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    user = crud.user.get_user_by_username(db, username="admin")
    if not user:
        user_in = UserCreate(username="admin", password="admin")
        crud.user.create_user(db=db, user=user_in)
    db.close()

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(tariffs.router, prefix="/api/tariffs", tags=["tariffs"])
app.include_router(cars.router, prefix="/api/cars", tags=["cars"])
app.include_router(journal.router, prefix="/api/journal", tags=["journal"])

@app.get("/")
def read_root():
    """A simple endpoint to confirm the API is running."""
    return {"status": "ok"}
