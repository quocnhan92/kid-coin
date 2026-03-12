from contextvars import ContextVar
from typing import Optional
import uuid

# Define context variables to store request-scoped data
_request_id_ctx_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
_user_id_ctx_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)

def get_request_id() -> str:
    return _request_id_ctx_var.get() or str(uuid.uuid4())

def set_request_id(request_id: str):
    _request_id_ctx_var.set(request_id)

def get_current_user_id() -> Optional[str]:
    return _user_id_ctx_var.get()

def set_current_user_id(user_id: str):
    _user_id_ctx_var.set(user_id)
