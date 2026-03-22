import logging
import json
import time
import uuid
from datetime import datetime
from typing import Optional


class JSONFormatter(logging.Formatter):
    """
    Standardizes logs into JSON format for cloud observability.
    """
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "trace_id": getattr(record, "trace_id", "system"),
            "execution_time": getattr(record, "execution_time", None)
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def setup_production_logging():
    """
    Configures the root logger for production-grade output.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
    
    # Silence chatty libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_trace_logger(name: str, trace_id: Optional[str] = None):
    """
    Returns a logger adapter that injects a Trace ID into every log.
    """
    logger = logging.getLogger(name)
    trace_id = trace_id or str(uuid.uuid4())
    return logging.LoggerAdapter(logger, {"trace_id": trace_id})
