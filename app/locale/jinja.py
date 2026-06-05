from __future__ import annotations

import json
from typing import Any, Dict, Optional

from starlette.requests import Request

from app.locale.catalog import merged_messages
from app.locale.registry import LOCALES, MARKETS
from app.locale.resolver import LocaleContext, resolve_locale_context
from app.locale.translator import translate


def locale_from_request(request: Request) -> LocaleContext:
    lc = getattr(request.state, "locale_ctx", None)
    return lc if lc else resolve_locale_context(request)


def template_context(request: Request, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    lc = locale_from_request(request)
    msgs = merged_messages(lc.locale)

    def t(key: str, default: Optional[str] = None, **params: Any) -> str:
        return translate(key, lc, params or None, default=default)

    ctx: Dict[str, Any] = {
        "locale": lc.locale,
        "market": lc.market,
        "speech_lang": lc.speech_lang,
        "locale_ctx": lc,
        "t": t,
        "locale_messages_json": json.dumps(msgs, ensure_ascii=False),
        "locale_config_json": json.dumps(
            {
                "locale": lc.locale,
                "market": lc.market,
                "speechLang": lc.speech_lang,
                "rtl": lc.is_rtl,
                "markets": [
                    {
                        "code": m.code,
                        "label": m.label,
                        "flag": m.flag,
                        "defaultLocale": m.default_locale,
                    }
                    for m in MARKETS.values()
                ],
                "locales": [
                    {"tag": l.tag, "label": l.label, "nativeLabel": l.native_label}
                    for l in LOCALES.values()
                ],
            },
            ensure_ascii=False,
        ),
    }
    if extra:
        ctx.update(extra)
    return ctx
