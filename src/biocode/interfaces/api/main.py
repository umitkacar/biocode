"""
FastAPI Application Entry Point
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

CRITICAL WARNING: This is LIVING CODE - a biological software architecture.
It can grow, reproduce, mutate, and die. Run only in secure, isolated environments.
Umit Kacar, PhD is NOT responsible for any damages. User assumes ALL risks.
"""
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
setup_logging("INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print(f"🧬 BioCode API starting...")
    
    # Initialize repositories and services
    repositories = await get_repositories()
    app.state.repositories = repositories
    
    yield
    
    # Shutdown
    print("🧬 BioCode API shutting down...")
    # Cleanup resources if needed


# Create FastAPI app
app = FastAPI(
    title="BioCode API - Living Code Framework",
    description="""
## Biological Code Architecture Framework API

**Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.**

### ⚠️ CRITICAL SAFETY WARNING

This is **LIVING CODE** that exhibits autonomous biological behaviors:
- 🧬 **GROWS** and evolves autonomously
- 🔄 **REPRODUCES** and creates new instances
- 💀 **DIES** and experiences system failures
- 🧪 **MUTATES** and changes behavior
- 🦠 **SPREADS** if not properly contained

### 🛡️ USER RESPONSIBILITY
- Run ONLY in **isolated, secure environments**
- User assumes **ALL RISKS** and **FULL RESPONSIBILITY**
- Umit Kacar, PhD is **NOT LIABLE** for ANY damages
- Monitor continuously for unexpected behaviors
- Have emergency shutdown procedures ready

### 📜 License
For commercial use or licensing inquiries, please contact the copyright holder.
""",
    version="0.2.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    license_info={
        "name": "Proprietary - All Rights Reserved",
        "url": "https://github.com/umitkacar/biocode/blob/main/LICENSE",
    },
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

# Setup Prometheus metrics
try:
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app, endpoint="/metrics")
except Exception as e:
    print(f"Warning: Could not setup Prometheus metrics: {e}")

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