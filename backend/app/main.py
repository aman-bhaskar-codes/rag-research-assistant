import uuid
import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.routes import query, history, upload
from app.utils.production_logger import setup_production_logging
from app.core.config import settings

# 1. Initialize Production Logging
setup_production_logging()
logger = logging.getLogger("app.main")

app = FastAPI(title=settings.PROJECT_NAME)

# 2. Production Middleware: Trace ID & Execution Time
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Trace-ID"] = trace_id
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# 3. Global Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": str(exc.detail),
                "type": "HTTPException",
                "code": exc.status_code
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "message": "Invalid request payload",
                "type": "ValidationError",
                "code": 422,
                "details": exc.errors()
            }
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, "trace_id", "unknown")
    logger.error(f"Unhandled error [{trace_id}]: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "An internal server error occurred.",
                "type": "InternalServerError",
                "code": 500,
                "trace_id": trace_id
            }
        }
    )

# 4. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router, tags=["Research"])
app.include_router(history.router, prefix="/api", tags=["History"])
app.include_router(upload.router, prefix="/api", tags=["Knowledge"])