"""Parent consent for mic / privacy-sensitive features."""
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.play.policy import PlayKidConsent
from app.models.user_family import Role, User

CONSENT_MIC = "mic"
POLICY_URL = "/privacy-play"


def mic_status(db: Session, kid_id: UUID) -> Dict[str, Any]:
    row = (
        db.query(PlayKidConsent)
        .filter(
            PlayKidConsent.kid_id == kid_id,
            PlayKidConsent.consent_type == CONSENT_MIC,
            PlayKidConsent.revoked_at.is_(None),
        )
        .first()
    )
    return {
        "consent_type": CONSENT_MIC,
        "required": True,
        "granted": row is not None,
        "granted_at": row.granted_at.isoformat() if row and row.granted_at else None,
        "policy_url": POLICY_URL,
    }


def grant_mic(db: Session, kid: User, parent: User) -> Dict[str, Any]:
    if parent.role != Role.PARENT or parent.family_id != kid.family_id:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Parent must grant mic consent")
    row = (
        db.query(PlayKidConsent)
        .filter(PlayKidConsent.kid_id == kid.id, PlayKidConsent.consent_type == CONSENT_MIC)
        .first()
    )
    now = datetime.now(timezone.utc)
    if row:
        row.revoked_at = None
        row.granted_by = parent.id
        row.granted_at = now
    else:
        db.add(
            PlayKidConsent(
                kid_id=kid.id,
                consent_type=CONSENT_MIC,
                granted_by=parent.id,
                granted_at=now,
            )
        )
    return mic_status(db, kid.id)
