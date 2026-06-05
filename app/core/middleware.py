from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import uuid
import time
from app.core import context
from app.core.api_compat import apply_api_headers, check_client_version

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        context.set_request_id(request_id)

        market = request.cookies.get("kidcoin_market")
        if market:
            context.set_market(market.lower())

        if request.url.path.startswith("/api/"):
            check_client_version(request)

        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            if request.url.path.startswith("/api/"):
                apply_api_headers(response)
            return response
        except Exception as e:
            raise e
