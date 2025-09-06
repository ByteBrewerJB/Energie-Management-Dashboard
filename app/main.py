from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.endpoints import monthly_energy, solar_investment

app = FastAPI(
    title="JouleJournal",
    description="Een webapp voor energie- en zon-data.",
    version="2.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# --- API Routers ---
# Include the new API routers, correctly namespaced
api_router = FastAPI()
api_router.include_router(monthly_energy.router, prefix="/monthly-energy", tags=["Monthly Energy"])
api_router.include_router(solar_investment.router, prefix="/solar-investments", tags=["Solar Investments"])

app.mount("/api", api_router)


# --- Frontend Routes ---
@app.get("/", tags=["Frontend"])
def serve_dashboard(request: Request):
    """Serves the main application page."""
    return templates.TemplateResponse("index.html", {"request": request})
