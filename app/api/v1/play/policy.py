from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.api.deps_play import require_kid, require_parent
from app.models.user_family import User
from app.services import play_consent_service, play_screen_time_service

router = APIRouter()


@router.get("/consent/mic")
def get_mic_consent(
    db: Session = Depends(deps.get_db),
    kid: User = Depends(require_kid),
):
    return play_consent_service.mic_status(db, kid.id)


@router.post("/consent/mic")
def grant_mic_consent(
    db: Session = Depends(deps.get_db),
    kid: User = Depends(require_kid),
    parent: User = Depends(require_parent),
):
    out = play_consent_service.grant_mic(db, kid, parent)
    db.commit()
    return out


@router.get("/screen-time")
def get_screen_time(
    db: Session = Depends(deps.get_db),
    kid: User = Depends(require_kid),
):
    return play_screen_time_service.get_status(db, kid.id)
