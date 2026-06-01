"""Play Hub write paths: sessions/batch, events/batch, idempotency."""
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.models.play import (
    PlaySession,
    PlayEvent,
    PlaySessionSummary,
    PlayIdempotencyKey,
    PlayUserGameStats,
)
from app.services.english_shooter_progress_service import (
    apply_english_live_sync,
    GOLD_PER_VOCAB_HIT,
    GAME_ID as ENGLISH_GAME_ID,
)
from app.models.user_family import User
from app.schemas.play import (
    SessionStartOp,
    SessionEndOp,
    SessionSummaryIn,
    SessionsBatchResponse,
    SessionBatchResult,
    EventsBatchResponse,
    PlayEventIn,
)
from app.services.play_rollup_service import rollup_after_session_end
from app.services.play_service import compute_bootstrap_etag
from app.services import streak_service


def _hash_request(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def get_idempotent_response(
    db: Session, user_id: UUID, key: str, endpoint: str, request_hash: str
) -> Optional[Dict[str, Any]]:
    row = (
        db.query(PlayIdempotencyKey)
        .filter(
            PlayIdempotencyKey.key == key,
            PlayIdempotencyKey.user_id == user_id,
            PlayIdempotencyKey.endpoint == endpoint,
        )
        .first()
    )
    if row and row.request_hash == request_hash:
        return row.response_json
    if row and row.request_hash != request_hash:
        raise HTTPException(status_code=409, detail="Idempotency-Key reused with different body")
    return None


def store_idempotent_response(
    db: Session, user_id: UUID, key: str, endpoint: str, request_hash: str, response: Dict[str, Any]
) -> None:
    db.add(
        PlayIdempotencyKey(
            key=key,
            user_id=user_id,
            endpoint=endpoint,
            request_hash=request_hash,
            response_json=response,
        )
    )


def _coerce_session_op(
    item: Union[SessionStartOp, SessionEndOp, Dict[str, Any]],
) -> Union[SessionStartOp, SessionEndOp]:
    if isinstance(item, (SessionStartOp, SessionEndOp)):
        return item
    if not isinstance(item, dict):
        raise HTTPException(
            status_code=422,
            detail="Mỗi phần tử trong sessions phải là object (start/end)",
        )
    op = item.get("op")
    try:
        if op == "start":
            return SessionStartOp.model_validate(item)
        if op == "end":
            return SessionEndOp.model_validate(item)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    raise HTTPException(status_code=400, detail=f"Unknown op: {op}")


def process_sessions_batch(
    db: Session,
    user: User,
    sessions_payload: List[Union[SessionStartOp, SessionEndOp, Dict[str, Any]]],
) -> SessionsBatchResponse:
    results: List[SessionBatchResult] = []
    game_id_for_etag = "math_blast"
    mode_for_etag: Optional[str] = None

    for item in sessions_payload:
        data = _coerce_session_op(item)
        if isinstance(data, SessionStartOp):
            game_id_for_etag = data.game_id
            mode_for_etag = data.game_mode_id
            existing = db.query(PlaySession).filter(PlaySession.id == data.session_id).first()
            if existing:
                if existing.user_id != user.id:
                    raise HTTPException(status_code=403, detail="Session belongs to another user")
                results.append(
                    SessionBatchResult(session_id=data.session_id, status=existing.status)
                )
                continue
            session = PlaySession(
                id=data.session_id,
                user_id=user.id,
                family_id=user.family_id,
                game_id=data.game_id,
                game_mode_id=data.game_mode_id,
                status="active",
                started_at=data.started_at,
                content_pack_id=data.content_pack_id,
                manifest_hash=data.manifest_hash,
            )
            db.add(session)
            results.append(SessionBatchResult(session_id=data.session_id, status="active"))

        else:
            game_id_for_etag = db.query(PlaySession.game_id).filter(PlaySession.id == data.session_id).scalar() or game_id_for_etag
            session = db.query(PlaySession).filter(PlaySession.id == data.session_id).first()
            if not session:
                raise HTTPException(status_code=404, detail=f"Session {data.session_id} not found")
            if session.user_id != user.id:
                raise HTTPException(status_code=403, detail="Session belongs to another user")

            session.status = "completed"
            session.ended_at = data.ended_at
            mode_for_etag = session.game_mode_id

            summary = data.summary
            existing_sum = db.query(PlaySessionSummary).filter(
                PlaySessionSummary.session_id == data.session_id
            ).first()
            if not existing_sum:
                db.add(
                    PlaySessionSummary(
                        session_id=data.session_id,
                        duration_s=summary.duration_s,
                        questions_count=summary.questions_count,
                        correct_count=summary.correct_count,
                        accuracy=summary.accuracy,
                        score=summary.score,
                        stars_earned=summary.stars,
                        level_id=summary.level_id,
                        summary_json=summary.summary_json,
                    )
                )

            rollup = rollup_after_session_end(
                db, user.id, session.game_id, session.game_mode_id, summary
            )

            if summary.duration_s >= 40 or summary.questions_count >= 8:
                try:
                    streak_service.update_streak(db, str(user.id))
                except Exception:
                    pass

            results.append(
                SessionBatchResult(
                    session_id=data.session_id,
                    status="completed",
                    level_progress=rollup.get("level_progress"),
                    mastery_updated=rollup.get("mastery_updated", []),
                    new_high_score=rollup.get("new_high_score", False),
                )
            )

    db.commit()
    etag = compute_bootstrap_etag(db, user.id, game_id_for_etag, mode_for_etag)
    return SessionsBatchResponse(results=results, bootstrap_etag=etag)


def process_events_batch(
    db: Session,
    user: User,
    session_id: UUID,
    events: List[PlayEventIn],
) -> EventsBatchResponse:
    session = db.query(PlaySession).filter(PlaySession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Session belongs to another user")

    accepted = duplicates = rejected = 0
    max_seq = 0
    correct_accepted = 0

    for ev in events:
        max_seq = max(max_seq, ev.client_seq)
        exists = (
            db.query(PlayEvent.id)
            .filter(
                PlayEvent.session_id == session_id,
                PlayEvent.client_seq == ev.client_seq,
            )
            .first()
        )
        if exists:
            duplicates += 1
            continue
        db.add(
            PlayEvent(
                session_id=session_id,
                user_id=user.id,
                occurred_at=ev.occurred_at,
                client_seq=ev.client_seq,
                event_type=ev.event_type,
                skill_unit_id=ev.skill_unit_id,
                level_id=ev.level_id,
                item_id=ev.item_id,
                correct=ev.correct,
                latency_ms=ev.latency_ms,
                score_delta=ev.score_delta,
                context_json=ev.context,
            )
        )
        accepted += 1
        if ev.correct is True:
            correct_accepted += 1

    if correct_accepted > 0 and session.game_id == ENGLISH_GAME_ID:
        mode_key = session.game_mode_id or ""
        stats = (
            db.query(PlayUserGameStats)
            .filter(
                PlayUserGameStats.user_id == user.id,
                PlayUserGameStats.game_id == ENGLISH_GAME_ID,
                PlayUserGameStats.game_mode_id == mode_key,
            )
            .first()
        )
        if not stats:
            stats = PlayUserGameStats(
                user_id=user.id,
                game_id=ENGLISH_GAME_ID,
                game_mode_id=mode_key,
                high_score=0,
                total_sessions=0,
                extra_json={},
            )
            db.add(stats)
        gold_delta = 0
        if session.game_mode_id and "prairie" in session.game_mode_id:
            gold_delta = correct_accepted * GOLD_PER_VOCAB_HIT
        stats.extra_json = apply_english_live_sync(
            stats.extra_json, correct_accepted, gold_delta
        )

    db.commit()
    return EventsBatchResponse(
        accepted=accepted,
        duplicates=duplicates,
        rejected=rejected,
        server_seq_max=max_seq,
    )
