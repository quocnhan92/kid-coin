from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.core import context
from app.locale.jinja import locale_from_request
from app.models.user_family import User
from app.services.feature_flag_service import is_enabled


def _resolve_market(request: Request) -> Optional[str]:
    lc = locale_from_request(request)
    if lc and lc.market:
        return lc.market
    return context.get_market()


def _optional_user(request: Request, db: Session) -> Optional[User]:
    try:
        return deps.get_current_user(request, db)
    except HTTPException:
        return None


def require_feature(flag_key: str):
    def checker(
        request: Request,
        db: Session = Depends(deps.get_db),
    ):
        user = _optional_user(request, db)
        family_id = user.family_id if user else None
        market = _resolve_market(request)
        if not is_enabled(db, flag_key, family_id=family_id, market=market):
            raise HTTPException(status_code=404, detail="Feature not available")
        return True

    return checker
