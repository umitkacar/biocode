"""FastAPI Application Entry Point"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from biocode.shared.config import settings
from biocode.shared.logging import setup_logging
from biocode.interfaces.api.v1 import cells, tissues, organs, system
from biocode.interfaces.api.dependencies import get_repositories
from biocode.interfaces.api.middleware.error_handler import error_handler_middleware


# Setup logging
setup_logging(settings.environment)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print(f"🧬 BioCode API starting in {settings.environment} mode...")
    
    # Initialize repositories and services
    repositories = await get_repositories()
    app.state.repositories = repositories
    
    # Setup Prometheus metrics
    if settings.prometheus_enabled:
        instrumentator = Instrumentator()
        instrumentator.instrument(app).expose(app, endpoint="/metrics")
    
    yield
    
    # Shutdown
    print("🧬 BioCode API shutting down...")
    # Cleanup resources if needed


# Create FastAPI app
app = FastAPI(
    title="BioCode API",
    description="Biological Code Architecture Framework API",
    version="0.2.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom error handler
app.middleware("http")(error_handler_middleware)

# Include routers
app.include_router(cells.router, prefix=f"{settings.api_prefix}/cells", tags=["cells"])
app.include_router(tissues.router, prefix=f"{settings.api_prefix}/tissues", tags=["tissues"])
app.include_router(organs.router, prefix=f"{settings.api_prefix}/organs", tags=["organs"])
app.include_router(system.router, prefix=f"{settings.api_prefix}/system", tags=["system"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to BioCode API",
        "version": "0.2.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "0.2.0",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "biocode.interfaces.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )