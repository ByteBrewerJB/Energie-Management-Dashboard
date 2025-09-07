from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.endpoints import (
    analysis,
    metrics,
    tariffs,
    roi,
    forecast,
    auth,
    solar_panels,
    batteries,
    cars
)

app = FastAPI(
    title="JouleJournal",
    description="Een webapplicatie voor het monitoren, analyseren en rapporteren van energieverbruik.",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include the API routers
app.include_router(analysis.router, prefix="/api", tags=["Analysis"])
app.include_router(metrics.router, prefix="/api", tags=["Metrics"])
app.include_router(tariffs.router, prefix="/api", tags=["Tariffs"])
app.include_router(roi.router, prefix="/api", tags=["ROI"])
app.include_router(forecast.router, prefix="/api", tags=["Forecast"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(solar_panels.router, prefix="/api", tags=["Solar Panels"])
app.include_router(batteries.router, prefix="/api", tags=["Batteries"])
app.include_router(cars.router, prefix="/api", tags=["Cars"])


@app.get("/", tags=["Root"])
def serve_dashboard(request: Request):
    """Serves the main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", tags=["Authentication"])
def serve_login_page(request: Request):
    """Serves the login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/admin", tags=["Admin"])
def serve_admin_page(request: Request):
    """Serves the admin page."""
    return templates.TemplateResponse("admin.html", {"request": request})
