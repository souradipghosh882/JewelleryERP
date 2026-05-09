from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.inventory import router as inventory_router
from app.api.billing import router as billing_router
from app.api.rates_analytics import router as rates_router, analytics_router
from app.api.customers import router as customers_router
from app.api.schemes import router as schemes_router
from app.api.operations import router as operations_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Comprehensive ERP system for jewellery shops",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploaded images
uploads_dir = Path(settings.UPLOAD_DIR)
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(inventory_router, prefix="/api/v1")
app.include_router(billing_router, prefix="/api/v1")
app.include_router(rates_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(customers_router, prefix="/api/v1")
app.include_router(schemes_router, prefix="/api/v1")
app.include_router(operations_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
