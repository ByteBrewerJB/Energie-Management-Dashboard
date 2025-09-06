from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.endpoints import analysis, metrics, investments, tariffs

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
app.include_router(investments.router, prefix="/api", tags=["Investments"])
app.include_router(tariffs.router, prefix="/api", tags=["Tariffs"])


@app.get("/", tags=["Root"])
def serve_dashboard(request: Request):
    """Serves the main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})
