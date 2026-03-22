import uuid
import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.routes import query
from app.utils.production_logger import setup_production_logging

# 1. Initialize Production Logging
setup_production_logging()
logger = logging.getLogger("app.main")

app = FastAPI(title="Research Assistant API")

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

# 3. Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, "trace_id", "unknown")
    logger.error(f"Unhandled error: {exc}", extra={"trace_id": trace_id})
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred.",
            "trace_id": trace_id
        }
    )

# 4. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router)