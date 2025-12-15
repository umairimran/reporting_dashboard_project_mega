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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
