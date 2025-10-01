from fastapi import APIRouter

from . import assets, auth, cars, dashboard, journals

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(journals.router, prefix="/journals", tags=["journals"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(cars.router, prefix="/cars", tags=["cars"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
