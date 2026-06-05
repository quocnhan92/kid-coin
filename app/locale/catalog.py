"""Load & cache message bundles from JSON files."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from app.locale.registry import LOCALES

_MESSAGES_DIR = Path(__file__).resolve().parent / "messages"


@lru_cache(maxsize=32)
def load_bundle(locale: str) -> Dict[str, str]:
    path = _MESSAGES_DIR / f"{locale}.json"
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return {k: str(v) for k, v in data.items() if isinstance(v, str)}


def merged_messages(locale: str) -> Dict[str, str]:
    cfg = LOCALES.get(locale)
    if not cfg:
        return load_bundle("en")
    chain = [locale]
    fb = cfg.fallback
    while fb and fb not in chain:
        chain.append(fb)
        fb = LOCALES.get(fb).fallback if LOCALES.get(fb) else None
    out: Dict[str, str] = {}
    for tag in reversed(chain):
        out.update(load_bundle(tag))
    return out


def format_message(template: str, params: Dict[str, Any] | None) -> str:
    if not params:
        return template
    try:
        return template.format(**params)
    except (KeyError, ValueError):
        return template
