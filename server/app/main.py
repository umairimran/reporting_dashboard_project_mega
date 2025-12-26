"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.logging import setup_logging, logger
from app.core.config import settings

# Import all routers
from app.auth.router import router as auth_router
from app.clients.router import router as clients_router
from app.campaigns.router import router as campaigns_router
from app.metrics.router import router as metrics_router
from app.dashboard.router import router as dashboard_router
from app.exports.router import router as exports_router
from app.facebook.router import router as facebook_router
from app.surfside.router import router as surfside_router
from app.vibe.router import router as vibe_router
from app.ingestion.router import router as ingestion_router

# Scheduler for background jobs
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("=" * 60)
    logger.info("STARTING PAID MEDIA PERFORMANCE DASHBOARD API")
    logger.info("=" * 60)
    
    # Test database connection
    from app.core.database import get_db
    try:
        db = next(get_db())
        logger.info("✓ Database connection successful")
        db.close()
    except Exception as e:
        logger.error(f"✗ Database connection failed: {str(e)}")
    
    # Start scheduler for background jobs
    scheduler.start()
    logger.info("✓ Background job scheduler started")
    
    # Setup all scheduled jobs
    from app.jobs.scheduler import setup_all_jobs
    setup_all_jobs(scheduler)
    
    logger.info("=" * 60)
    logger.info("APPLICATION STARTUP COMPLETE")
    logger.info("=" * 60)
    logger.info("")
    logger.info("🚀 API Documentation available at:")
    logger.info("   - Swagger UI: http://0.0.0.0:8000/docs")
    logger.info("   - ReDoc: http://0.0.0.0:8000/redoc")
    logger.info("   - OpenAPI JSON: http://0.0.0.0:8000/openapi.json")
    logger.info("")
    logger.info("💡 If you see CORS errors:")
    logger.info("   1. Check that your access URL is in CORS_ORIGINS (.env)")
    logger.info("   2. For testing, you can use: CORS_ORIGINS=[\"*\"]")
    logger.info("   3. Check logs above for loaded CORS origins")
    logger.info("")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("SHUTTING DOWN PAID MEDIA PERFORMANCE DASHBOARD API")
    logger.info("=" * 60)
    
    if scheduler.running:
        scheduler.shutdown()
        logger.info("✓ Background job scheduler stopped")
    
    logger.info("Application shutdown complete")


# Initialize logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Paid Media Performance Dashboard API",
    description="API for managing and analyzing paid media performance data from multiple sources (Surfside, Vibe, Facebook)",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS middleware - Read from .env file (CORS_ORIGINS)
# Log CORS configuration for debugging
logger.info("=" * 60)
logger.info("CORS CONFIGURATION")
logger.info("=" * 60)
try:
    cors_origins = settings.cors_origins_list
    logger.info(f"✓ CORS Origins loaded: {cors_origins}")
    logger.info(f"  Total allowed origins: {len(cors_origins)}")
    for idx, origin in enumerate(cors_origins, 1):
        logger.info(f"  [{idx}] {origin}")
except Exception as e:
    logger.error(f"✗ CORS configuration error: {str(e)}")
    logger.error("  Check your .env file - CORS_ORIGINS must be valid JSON array")
    raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Single config point from .env!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("✓ CORS middleware configured successfully")
logger.info("=" * 60)

# Zstd Compression Middleware (Custom)
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, StreamingResponse
import zstandard as zstd

class ZstdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Allow client to opt-out or if not supported (though browser usually sends Accept-Encoding: gzip, deflate, br)
        # We will assume modern client supports it or we just force it for our specialized client
        # Ideally we check 'Accept-Encoding' header
        accept_encoding = request.headers.get("Accept-Encoding", "")
        
        response = await call_next(request)
        
        # We only compress if it's a JSON response and reasonably large
        if "application/json" not in response.headers.get("Content-Type", ""):
            return response
            
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
            
        if len(response_body) < 1000: # Don't compress small responses
            return Response(content=response_body, status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type)

        cctx = zstd.ZstdCompressor(level=3)
        compressed_body = cctx.compress(response_body)
        
        # Create new headers dict from original response
        headers = dict(response.headers)
        
        # Remove any existing Content-Length headers to avoid conflicts
        # Starlette/Uvicorn might send both if we don't clean it up
        keys_to_remove = [k for k in headers.keys() if k.lower() == "content-length"]
        for k in keys_to_remove:
            del headers[k]
            
        headers["Content-Encoding"] = "zstd"
        
        # Note: We do NOT manually set "Content-Length" here.
        # The Response class automatically calculates and sets it based on the 'content' argument.
        # This prevents "Response content shorter than Content-Length" errors.
        
        return Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type
        )

app.add_middleware(ZstdMiddleware)


# Request logging middleware for debugging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log incoming request
        origin = request.headers.get("origin", "N/A")
        logger.info(f"→ {request.method} {request.url.path} | Origin: {origin} | Client: {request.client.host if request.client else 'N/A'}")
        
        response = await call_next(request)
        
        # Log response
        process_time = (time.time() - start_time) * 1000
        logger.info(f"← {request.method} {request.url.path} | Status: {response.status_code} | Time: {process_time:.2f}ms")
        
        return response

app.add_middleware(RequestLoggingMiddleware)
logger.info("✓ Request logging middleware configured")


# Include all routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(clients_router, prefix="/api/v1")
app.include_router(campaigns_router, prefix="/api/v1")
app.include_router(metrics_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(exports_router, prefix="/api/v1")
app.include_router(facebook_router, prefix="/api/v1")
app.include_router(surfside_router, prefix="/api/v1")
app.include_router(vibe_router, prefix="/api/v1")
app.include_router(ingestion_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Paid Media Performance Dashboard API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "data_sources": ["Surfside (S3)", "Vibe (API)", "Facebook (Upload)"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from app.core.database import engine
    
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "database": "connected",
            "scheduler": "running" if scheduler.running else "stopped"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@app.get("/api/v1/info")
async def api_info():
    """API information endpoint."""
    return {
        "api_version": "1.0.0",
        "status": "production_ready",
        "modules": {
            "authentication": {
                "status": "active",
                "features": ["JWT auth", "User management", "Role-based access (admin/client)"],
                "endpoints": ["/api/v1/auth/register", "/api/v1/auth/login", "/api/v1/auth/me"]
            },
            "clients": {
                "status": "active",
                "features": ["Client CRUD", "CPM settings", "Historical CPM tracking"],
                "endpoints": ["/api/v1/clients", "/api/v1/clients/{id}/cpm"]
            },
            "campaigns": {
                "status": "active",
                "features": ["Campaign hierarchy", "Find-or-create pattern", "4-level structure"],
                "endpoints": ["/api/v1/campaigns", "/api/v1/strategies", "/api/v1/placements", "/api/v1/creatives"]
            },
            "metrics": {
                "status": "active",
                "features": ["Daily metrics", "Weekly summaries", "Monthly summaries", "Aggregation"],
                "endpoints": ["/api/v1/metrics/daily", "/api/v1/metrics/weekly", "/api/v1/metrics/monthly"]
            },
            "dashboard": {
                "status": "active",
                "features": ["Summary stats", "Campaign breakdown", "Source breakdown", "Daily trends", "Top performers"],
                "endpoints": ["/api/v1/dashboard", "/api/v1/dashboard/summary", "/api/v1/dashboard/campaigns"]
            },
            "exports": {
                "status": "active",
                "features": ["CSV export (daily/summary)", "PDF reports"],
                "endpoints": ["/api/v1/exports/csv/daily-metrics", "/api/v1/exports/pdf/dashboard-report"]
            },
            "data_sources": {
                "surfside": {
                    "status": "active",
                    "type": "S3 automated",
                    "schedule": "Daily at 5:00 AM",
                    "format": "CSV/XLSX from S3"
                },
                "vibe": {
                    "status": "active",
                    "type": "API automated",
                    "schedule": "Daily at 5:00 AM",
                    "format": "Async API reports"
                },
                "facebook": {
                    "status": "active",
                    "type": "Manual upload",
                    "format": "CSV/XLSX upload",
                    "endpoints": ["/api/v1/facebook/upload"]
                }
            },
            "scheduler": {
                "status": "running",
                "jobs": [
                    {"name": "Daily data ingestion", "schedule": "Daily at 5:00 AM"},
                    {"name": "Weekly aggregation", "schedule": "Sundays at 7:00 AM"},
                    {"name": "Monthly aggregation", "schedule": "1st of month at 8:00 AM"}
                ]
            }
        },
        "documentation": "/docs",
        "health_check": "/health"
    }


@app.get("/api/v1/scheduler/status")
async def scheduler_status():
    """Get scheduler status and upcoming jobs."""
    from app.jobs.scheduler import get_scheduler_status
    return get_scheduler_status(scheduler)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
