"""Market & locale registry — add new countries here."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class MarketConfig:
    code: str
    label: str
    default_locale: str
    speech_lang: str
    currency: str
    flag: str = ""
    rtl: bool = False


@dataclass(frozen=True)
class LocaleConfig:
    tag: str
    label: str
    native_label: str
    fallback: Optional[str] = "en"
    speech_lang: Optional[str] = None


MARKETS: Dict[str, MarketConfig] = {
    "vn": MarketConfig(
        code="vn",
        label="Vietnam",
        default_locale="vi-VN",
        speech_lang="vi-VN",
        currency="VND",
        flag="🇻🇳",
    ),
    "en": MarketConfig(
        code="en",
        label="English (International)",
        default_locale="en",
        speech_lang="en-US",
        currency="USD",
        flag="🌐",
    ),
    "my": MarketConfig(
        code="my",
        label="Malaysia",
        default_locale="en-MY",
        speech_lang="en-MY",
        currency="MYR",
        flag="🇲🇾",
    ),
    "ph": MarketConfig(
        code="ph",
        label="Philippines",
        default_locale="en-PH",
        speech_lang="en-PH",
        currency="PHP",
        flag="🇵🇭",
    ),
}

LOCALES: Dict[str, LocaleConfig] = {
    "vi-VN": LocaleConfig("vi-VN", "Vietnamese", "Tiếng Việt", fallback="en", speech_lang="vi-VN"),
    "en": LocaleConfig("en", "English", "English", fallback=None, speech_lang="en-US"),
    "en-MY": LocaleConfig("en-MY", "English (Malaysia)", "English", fallback="en", speech_lang="en-MY"),
    "en-PH": LocaleConfig("en-PH", "English (Philippines)", "English", fallback="en", speech_lang="en-PH"),
    "ms-MY": LocaleConfig("ms-MY", "Malay", "Bahasa Melayu", fallback="en-MY", speech_lang="ms-MY"),
}

def _default_market() -> str:
    try:
        from app.core.config import settings
        m = (settings.DEFAULT_MARKET or "vn").lower()
        return m if m in MARKETS else "vn"
    except Exception:
        return "vn"


DEFAULT_MARKET = "vn"
DEFAULT_LOCALE = "vi-VN"

# Path prefix: /m/my/game/...  (optional future routes)
MARKET_PATH_PREFIX = "/m/"

# Legacy routes → force UI locale until pages use bundles only
ROUTE_LOCALE_HINTS: Dict[str, str] = {
    "/game/english-shooter": "en",
    "/game/english-shooter/": "en",
}

# Product lines that imply English UI (math clone, shooter)
ROUTE_MARKET_HINTS: Dict[str, str] = {
    "/game/english-shooter": "en",
}
