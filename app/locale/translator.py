from __future__ import annotations

from typing import Any, Dict, Optional

from app.locale.catalog import format_message, merged_messages
from app.locale.resolver import LocaleContext


def translate(
    key: str,
    ctx: LocaleContext,
    params: Optional[Dict[str, Any]] = None,
    default: Optional[str] = None,
) -> str:
    msgs = merged_messages(ctx.locale)
    raw = msgs.get(key)
    if raw is None:
        raw = default if default is not None else key
    return format_message(raw, params)
