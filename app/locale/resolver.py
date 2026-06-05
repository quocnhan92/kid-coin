"""Resolve market + locale per HTTP request."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from starlette.requests import Request

from app.locale.registry import (
    DEFAULT_LOCALE,
    MARKET_PATH_PREFIX,
    MARKETS,
    ROUTE_LOCALE_HINTS,
    ROUTE_MARKET_HINTS,
    LOCALES,
    _default_market,
)

COOKIE_MARKET = "kidcoin_market"
COOKIE_LOCALE = "kidcoin_locale"
_PATH_MARKET_RE = re.compile(r"^/m/([a-z]{2})(?:/|$)")


@dataclass(frozen=True)
class LocaleContext:
    market: str
    locale: str
    speech_lang: str
    path_without_market_prefix: str

    @property
    def is_rtl(self) -> bool:
        m = MARKETS.get(self.market)
        return bool(m and m.rtl)

    @property
    def uses_english_ui(self) -> bool:
        return self.locale == "en" or self.locale.startswith("en-")


def _normalize_locale(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    tag = raw.strip().replace("_", "-")
    if tag in LOCALES:
        return tag
    short = tag.split("-")[0].lower()
    if short == "vi":
        return "vi-VN"
    if short == "en":
        return "en"
    if short == "ms":
        return "ms-MY"
    return None


def _locale_from_accept_language(header: Optional[str]) -> Optional[str]:
    if not header:
        return None
    for part in header.split(","):
        token = part.split(";")[0].strip()
        loc = _normalize_locale(token)
        if loc:
            return loc
    return None


def _route_hint_locale(path: str) -> Optional[str]:
    for prefix, loc in sorted(ROUTE_LOCALE_HINTS.items(), key=lambda x: -len(x[0])):
        if path.startswith(prefix):
            return loc
    return None


def _route_hint_market(path: str) -> Optional[str]:
    for prefix, market in sorted(ROUTE_MARKET_HINTS.items(), key=lambda x: -len(x[0])):
        if path.startswith(prefix):
            return market
    return None


def _parse_path_market(path: str) -> tuple[Optional[str], str]:
    m = _PATH_MARKET_RE.match(path)
    if not m:
        return None, path
    code = m.group(1)
    if code not in MARKETS:
        return None, path
    rest = path[m.end() - 1 :] if path[m.end() - 1 :] else "/"
    if rest != "/" and not rest.startswith("/"):
        rest = "/" + rest
    return code, rest


def resolve_locale_context(request: Request) -> LocaleContext:
    path = request.url.path
    path_market, inner_path = _parse_path_market(path)

    market = path_market or request.cookies.get(COOKIE_MARKET)
    market = (market or "").lower() or None
    if market and market not in MARKETS:
        market = None

    locale = _normalize_locale(request.cookies.get(COOKIE_LOCALE))
    if not locale:
        locale = _route_hint_locale(inner_path) or _route_hint_locale(path)
    if not locale:
        locale = _locale_from_accept_language(request.headers.get("accept-language"))

    if not market:
        market = _route_hint_market(inner_path) or _route_hint_market(path)

    if not market:
        market = _default_market()

    if market not in MARKETS:
        market = _default_market()

    mcfg = MARKETS[market]
    if not locale:
        locale = mcfg.default_locale

    if locale not in LOCALES:
        locale = mcfg.default_locale

    speech = LOCALES.get(locale).speech_lang if LOCALES.get(locale) else None
    speech_lang = speech or mcfg.speech_lang

    return LocaleContext(
        market=market,
        locale=locale,
        speech_lang=speech_lang,
        path_without_market_prefix=inner_path,
    )
