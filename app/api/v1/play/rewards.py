from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user_family import Role, User
from app.schemas.play import RewardPlaygroundResponse
from app.services import play_reward_service
from app.services.feature_flag_service import is_enabled

router = APIRouter()


def _resolve_kid(db: Session, user: User) -> User:
    if user.role == Role.KID:
        return user
    if user.role == Role.PARENT:
        kid = (
            db.query(User)
            .filter(User.family_id == user.family_id, User.role == Role.KID)
            .first()
        )
        if kid:
            return kid
    raise HTTPException(status_code=403, detail="Kid account required")


@router.get("/rewards", response_model=RewardPlaygroundResponse)
def reward_playground_status(
    request: Request,
    genre: str | None = None,
    include_draft: bool = False,
    db: Session = Depends(deps.get_db),
):
    from app.locale.jinja import locale_from_request

    lc = locale_from_request(request)
    market = lc.market if lc else None
    if not is_enabled(db, "play.reward_playground", market=market):
        raise HTTPException(status_code=404, detail="Feature not available")
    user_id = None
    token = deps.get_token_from_request(request)
    if token:
        from app.core.security import decode_access_token

        payload = decode_access_token(token)
        if payload and payload.get("sub"):
            try:
                user = db.query(User).filter(User.id == payload["sub"]).first()
                if user:
                    kid = _resolve_kid(db, user)
                    user_id = kid.id
            except Exception:
                pass
    payload = play_reward_service.build_reward_playground(
        db, user_id, genre=genre, include_draft=include_draft
    )
    return RewardPlaygroundResponse(**payload)
