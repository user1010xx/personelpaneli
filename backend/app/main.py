from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .config import settings
from .database import Base, engine
from .routes import auth, users, personnel, sales, attendance, warnings, training, call_monitoring, whatsapp

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Personel Panel API - Call Center Management System"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc), "errors": exc.errors()},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(personnel.router)
app.include_router(sales.router)
app.include_router(attendance.router)
app.include_router(warnings.router)
app.include_router(training.router)
app.include_router(call_monitoring.router)
app.include_router(whatsapp.router)

@app.get("/")
def root():
    """API health check"""
    return {
        "message": "Personel Panel API",
        "version": settings.API_VERSION,
        "status": "running"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected"
    }

@app.get("/api/docs")
def api_docs():
    """API Documentation"""
    return {
        "title": settings.API_TITLE,
        "version": settings.API_VERSION,
        "endpoints": {
            "auth": "/api/auth",
            "users": "/api/users",
            "personnel": "/api/personnel",
            "sales": "/api/sales",
            "attendance": "/api/attendance",
            "warnings": "/api/warnings",
            "training": "/api/training",
            "call_monitoring": "/api/call-monitoring",
            "whatsapp": "/api/whatsapp"
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )
