from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.api import v1_router
from app.core.config import settings

app = FastAPI(
    title="FastAPI Starter Template",
    version="0.1.0",
    description="A scalable FastAPI server template with SQLModel and Alembic",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# Set up CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/", status_code=status.HTTP_200_OK, tags=["Root"])
def read_root():
    return {"message": "Welcome to the FastAPI Server Template!", "version": "0.1.0"}


@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
def health_check():
    return {"status": "healthy"}


app.include_router(v1_router.routes, prefix="/api")