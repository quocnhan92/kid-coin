from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request, Response, status
from sqlalchemy.orm import Session

from app.api import deps
from app.api.deps_play import require_kid, require_parent
from app.models.user_family import Role
from app.models.user_family import User
from app.schemas.play import (
    PlayBootstrapResponse,
    PlayGamesResponse,
    PlayLevelsResponse,
    PlayHistoryResponse,
    SessionsBatchRequest,
    SessionsBatchResponse,
    EventsBatchRequest,
    EventsBatchResponse,
    LeaderboardResponse,
    ParentDashboardResponse,
    ParentChildLevelsResponse,
)
from app.services import play_service, play_session_service, play_parent_service

router = APIRouter()


@router.get("/games", response_model=PlayGamesResponse)
def list_play_games(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return play_service.list_games(db)


@router.get("/levels", response_model=PlayLevelsResponse)
def play_levels(
    game_mode_id: str = "math_blast:candy",
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return play_service.list_levels(db, game_mode_id)


@router.get("/bootstrap", response_model=PlayBootstrapResponse)
def play_bootstrap(
    request: Request,
    response: Response,
    game_id: str = "math_blast",
    game_mode_id: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role not in (Role.KID, Role.PARENT):
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Not allowed")
    kid = current_user
    if current_user.role == Role.PARENT:
        kid = (
            db.query(User)
            .filter(User.family_id == current_user.family_id, User.role == Role.KID)
            .first()
        )
        if not kid:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="No kid in family")

    body, etag = play_service.get_bootstrap(db, kid, game_id, game_mode_id)
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)
    response.headers["ETag"] = etag
    return body


@router.get("/history", response_model=PlayHistoryResponse)
def play_history(
    game_id: Optional[str] = None,
    game_mode_id: Optional[str] = None,
    limit: int = 20,
    cursor: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_kid),
):
    return play_service.get_history(
        db, current_user.id, game_id, game_mode_id, min(limit, 50), cursor
    )


@router.get("/leaderboard", response_model=LeaderboardResponse)
def play_leaderboard(
    game_id: str = "math_blast",
    game_mode_id: str = "math_blast:flappy",
    tier: Optional[str] = None,
    scope: str = "family",
    period: str = "daily",
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if scope != "family":
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Only family scope supported in MVP")
    return play_service.get_leaderboard(
        db, current_user, game_id, game_mode_id, tier, period
    )


@router.post("/sessions/batch", response_model=SessionsBatchResponse)
def sessions_batch(
    payload: SessionsBatchRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_kid),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    req_hash = play_session_service._hash_request(payload.model_dump())
    if idempotency_key:
        cached = play_session_service.get_idempotent_response(
            db, current_user.id, idempotency_key, "sessions/batch", req_hash
        )
        if cached:
            try:
                return SessionsBatchResponse.model_validate(cached)
            except Exception:
                pass

    session_items = []
    for item in payload.sessions:
        if hasattr(item, "model_dump"):
            session_items.append(item.model_dump(mode="json"))
        else:
            session_items.append(item)

    result = play_session_service.process_sessions_batch(
        db, current_user, session_items
    )
    if idempotency_key:
        play_session_service.store_idempotent_response(
            db,
            current_user.id,
            idempotency_key,
            "sessions/batch",
            req_hash,
            result.model_dump(mode="json"),
        )
        db.commit()
    return result


@router.post("/events/batch", response_model=EventsBatchResponse)
def events_batch(
    payload: EventsBatchRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_kid),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    req_hash = play_session_service._hash_request(payload.model_dump())
    if idempotency_key:
        cached = play_session_service.get_idempotent_response(
            db, current_user.id, idempotency_key, "events/batch", req_hash
        )
        if cached:
            return EventsBatchResponse(**cached)

    result = play_session_service.process_events_batch(
        db, current_user, payload.session_id, payload.events
    )
    if idempotency_key:
        play_session_service.store_idempotent_response(
            db,
            current_user.id,
            idempotency_key,
            "events/batch",
            req_hash,
            result.model_dump(),
        )
        db.commit()
    return result


@router.get("/parent/dashboard", response_model=ParentDashboardResponse)
def parent_play_dashboard(
    request: Request,
    response: Response,
    period: str = "7d",
    db: Session = Depends(deps.get_db),
    parent: User = Depends(require_parent),
):
    body = play_parent_service.get_parent_dashboard(db, parent, period)
    if request.headers.get("if-none-match") == body.etag:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)
    response.headers["ETag"] = body.etag
    return body


@router.get("/parent/child/{child_id}/levels", response_model=ParentChildLevelsResponse)
def parent_child_levels(
    child_id: UUID,
    db: Session = Depends(deps.get_db),
    parent: User = Depends(require_parent),
):
    return play_parent_service.get_child_levels(db, parent, child_id)
