from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core import context as app_context
from app.locale.resolver import resolve_locale_context


class LocaleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        lc = resolve_locale_context(request)
        request.state.locale_ctx = lc
        app_context.set_locale_context(lc)
        response = await call_next(request)
        response.headers["Content-Language"] = lc.locale
        response.headers["X-KidCoin-Market"] = lc.market
        return response
