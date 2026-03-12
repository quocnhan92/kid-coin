from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import uuid
import time
from app.core import context
from app.services.audit import AuditService, AuditStatus
from app.core.database import SessionLocal

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Generate or get Request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        context.set_request_id(request_id)
        
        # 2. Add to response headers
        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Simple Audit for non-GET requests or specific paths could be added here
            # But usually, we log specific business actions inside Service layer.
            
            return response
        except Exception as e:
            # Global Exception Handler could be here
            raise e
