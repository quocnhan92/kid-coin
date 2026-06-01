"""API: flappy session returns stickers_unlocked on end."""

import uuid
from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_flappy_practice_unlocks_sticker_in_batch(kid_token):
    sid = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    headers = {
        "Authorization": f"Bearer {kid_token}",
        "Idempotency-Key": f"flappy-sticker-{sid}",
    }
    start = client.post(
        "/api/v1/play/sessions/batch",
        json={
            "sessions": [
                {
                    "op": "start",
                    "session_id": sid,
                    "game_id": "math_blast",
                    "game_mode_id": "math_blast:flappy",
                    "started_at": now,
                }
            ]
        },
        headers=headers,
    )
    assert start.status_code == 200

    end = client.post(
        "/api/v1/play/sessions/batch",
        json={
            "sessions": [
                {
                    "op": "end",
                    "session_id": sid,
                    "ended_at": now,
                    "summary": {
                        "duration_s": 90,
                        "score": 25,
                        "questions_count": 6,
                        "correct_count": 5,
                        "accuracy": 0.83,
                        "summary_json": {
                            "tier": "T1",
                            "grade": 1,
                            "play_mode": "practice",
                            "combo_max": 4,
                            "play_date": "2026-05-21",
                            "manual_end": True,
                            "persistent_correct": True,
                        },
                    },
                }
            ]
        },
        headers={
            "Authorization": f"Bearer {kid_token}",
            "Idempotency-Key": f"flappy-sticker-end-{sid}",
        },
    )
    assert end.status_code == 200
    row = end.json()["results"][0]
    assert row["status"] == "completed"
    assert "ga_con" in row.get("stickers_unlocked", [])

    boot = client.get(
        "/api/v1/play/bootstrap",
        params={"game_id": "math_blast", "game_mode_id": "math_blast:flappy"},
        headers={"Authorization": f"Bearer {kid_token}"},
    )
    assert boot.status_code == 200
    flappy = boot.json().get("flappy") or {}
    assert "ga_con" in flappy.get("stickers_unlocked", [])
    assert flappy.get("sticker_total") == 16
    assert len(flappy.get("sticker_meta", [])) == 16
