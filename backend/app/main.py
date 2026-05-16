import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.extension import _rate_limit_exceeded_handler
from sqlalchemy.orm import Session
from sqlalchemy import text
from .config import settings
from .database import Base, SessionLocal, engine, get_db
from .routes import auth, users, personnel, sales, attendance, warnings, training, call_monitoring, whatsapp, call_process, docs_links, dashboard, setup
from .utils.bootstrap import ensure_initial_admin
from .utils.migrations import upgrade_database

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    upgrade_database()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_initial_admin(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Personel Panel API - Call Center Management System",
    lifespan=lifespan,
    redirect_slashes=False,
)

app.state.limiter = auth.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    sanitized_errors = []
    for error in exc.errors():
        sanitized_error = dict(error)
        context = sanitized_error.get('ctx')
        if context:
            sanitized_error['ctx'] = {key: str(value) for key, value in context.items()}
        sanitized_errors.append(sanitized_error)
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": "Validation error", "errors": sanitized_errors}),
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    request_id = getattr(request.state, "request_id", None)
    logger.error(
        "Unhandled exception on %s %s request_id=%s: %s",
        request.method,
        request.url.path,
        request_id,
        str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "request_id": request_id},
    )

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(personnel.router)
app.include_router(sales.router)
app.include_router(attendance.router)
app.include_router(warnings.router)
app.include_router(training.router)
app.include_router(call_monitoring.router)
app.include_router(whatsapp.router)
app.include_router(call_process.router)
app.include_router(docs_links.router)
app.include_router(dashboard.router)
app.include_router(setup.router)

@app.get("/")
def root():
    return {
        "message": "Personel Panel API",
        "version": settings.API_VERSION,
        "status": "running"
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status
    }

@app.get("/api/docs")
def api_docs():
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
            "whatsapp": "/api/whatsapp",
            "call_process": "/api/call-process",
            "docs_links": "/api/docs-links",
            "dashboard": "/api/dashboard"
        }
    }
