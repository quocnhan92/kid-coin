from contextvars import ContextVar
from typing import Optional, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from app.locale.resolver import LocaleContext

_request_id_ctx_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
_user_id_ctx_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
_family_id_ctx_var: ContextVar[Optional[str]] = ContextVar("family_id", default=None)
_market_ctx_var: ContextVar[Optional[str]] = ContextVar("market", default=None)
_locale_ctx_var: ContextVar[Optional["LocaleContext"]] = ContextVar("locale_ctx", default=None)


def get_request_id() -> str:
    return _request_id_ctx_var.get() or str(uuid.uuid4())


def set_request_id(request_id: str):
    _request_id_ctx_var.set(request_id)


def get_current_user_id() -> Optional[str]:
    return _user_id_ctx_var.get()


def set_current_user_id(user_id: str):
    _user_id_ctx_var.set(user_id)


def get_family_id() -> Optional[str]:
    return _family_id_ctx_var.get()


def set_family_id(family_id: Optional[str]):
    _family_id_ctx_var.set(family_id)


def get_market() -> Optional[str]:
    return _market_ctx_var.get()


def set_market(market: Optional[str]):
    _market_ctx_var.set(market)


def get_locale_context() -> Optional["LocaleContext"]:
    return _locale_ctx_var.get()


def set_locale_context(ctx: "LocaleContext"):
    _locale_ctx_var.set(ctx)
