from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.platform import FeatureFlag

_SCOPE_ORDER = {"family": 0, "market": 1, "global": 2}


def _flag_rows(db: Session, key: str) -> List[FeatureFlag]:
    return db.query(FeatureFlag).filter(FeatureFlag.key == key).all()


def _norm_scope_value(scope: str, scope_value: Optional[str]) -> str:
    if scope == "global":
        return ""
    return scope_value or ""


def is_enabled(
    db: Session,
    key: str,
    *,
    family_id: Optional[UUID] = None,
    market: Optional[str] = None,
) -> bool:
    rows = _flag_rows(db, key)
    if not rows:
        if key == "play.test_unlock_all":
            return settings.PLAY_TEST_UNLOCK_ALL
        return True

    candidates: List[FeatureFlag] = []
    for row in rows:
        if row.scope == "global" and (row.scope_value or "") == "":
            candidates.append(row)
        elif row.scope == "market" and market and row.scope_value == market:
            candidates.append(row)
        elif row.scope == "family" and family_id and row.scope_value == str(family_id):
            candidates.append(row)

    if not candidates:
        global_rows = [r for r in rows if r.scope == "global" and (r.scope_value or "") == ""]
        if global_rows:
            return bool(global_rows[0].enabled)
        return True

    candidates.sort(key=lambda r: _SCOPE_ORDER.get(r.scope, 99))
    return bool(candidates[0].enabled)


def list_effective_flags(
    db: Session,
    *,
    family_id: Optional[UUID] = None,
    market: Optional[str] = None,
) -> Dict[str, bool]:
    keys = [r.key for r in db.query(FeatureFlag.key).distinct().all()]
    return {k: is_enabled(db, k, family_id=family_id, market=market) for k in keys}


def upsert_flag(
    db: Session,
    key: str,
    enabled: bool,
    scope: str = "global",
    scope_value: Optional[str] = None,
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> FeatureFlag:
    norm_value = _norm_scope_value(scope, scope_value)
    row = (
        db.query(FeatureFlag)
        .filter(
            FeatureFlag.key == key,
            FeatureFlag.scope == scope,
            FeatureFlag.scope_value == norm_value,
        )
        .first()
    )
    if row:
        row.enabled = enabled
        if description is not None:
            row.description = description
        if metadata is not None:
            row.metadata_json = metadata
        return row

    row = FeatureFlag(
        key=key,
        enabled=enabled,
        scope=scope,
        scope_value=norm_value,
        description=description,
        metadata_json=metadata or {},
    )
    db.add(row)
    return row
