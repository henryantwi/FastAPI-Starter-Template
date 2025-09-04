from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.api import v1_router
from app.core.config import settings
from app.core.redis import redis_client, get_cache_info
from app.core.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting FastAPI application...")
    
    # Initialize Redis connection
    try:
        if settings.CACHE_ENABLED:
            redis_client.get_sync_client()
            cache_info = get_cache_info()
            if cache_info["status"] == "connected":
                logger.info(f"Redis connected successfully. Version: {cache_info.get('redis_version', 'unknown')}")
            elif cache_info["status"] == "disabled":
                logger.info("Caching is disabled via CACHE_ENABLED=False")
            else:
                logger.warning("Redis connection failed. Caching will be disabled.")
        else:
            logger.info("Caching is disabled via CACHE_ENABLED=False")
    except Exception as e:
        logger.warning(f"Redis initialization error: {e}. Caching will be disabled.")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application...")
    redis_client.close_connections()


app = FastAPI(
    title="FastAPI Server with SQLModel and Redis",
    version="0.1.0",
    description="A scalable FastAPI server template with SQLModel, Alembic, and Redis caching",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
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
    cache_info = get_cache_info()
    return {
        "status": "healthy",
        "cache": {
            "redis_status": cache_info["status"],
            "redis_version": cache_info.get("redis_version"),
            "cache_enabled": settings.CACHE_ENABLED,
        }
    }


app.include_router(v1_router.routes, prefix="/api")