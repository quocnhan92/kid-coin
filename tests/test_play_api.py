"""Play Hub API smoke tests (requires PostgreSQL + migrated schema)."""
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from main import app
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.user_family import User, Role, Family
from app.services.play_catalog_seed import seed_play_catalog

client = TestClient(app)

pytestmark = pytest.mark.usefixtures("require_postgres")


@pytest.fixture(scope="module")
def require_postgres():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
    except OperationalError as exc:
        pytest.skip(f"PostgreSQL not available: {exc}")
    finally:
        db.close()


@pytest.fixture
def kid_token(require_postgres):
    db = SessionLocal()
    seed_play_catalog(db)
    family = db.query(Family).first()
    if not family:
        family = Family(id=uuid4(), name="Test Family", parent_pin="1234")
        db.add(family)
        db.flush()
    kid = (
        db.query(User)
        .filter(User.family_id == family.id, User.role == Role.KID)
        .first()
    )
    if not kid:
        kid = User(
            id=uuid4(),
            family_id=family.id,
            role=Role.KID,
            display_name="Test Kid",
        )
        db.add(kid)
        db.commit()
    token = create_access_token(str(kid.id))
    db.close()
    return token


def test_play_games_public_auth(kid_token):
    r = client.get(
        "/api/v1/play/games",
        headers={"Authorization": f"Bearer {kid_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert any(g["id"] == "math_blast" for g in data["games"])


def test_play_bootstrap(kid_token):
    r = client.get(
        "/api/v1/play/bootstrap",
        params={"game_id": "math_blast", "game_mode_id": "math_blast:candy"},
        headers={"Authorization": f"Bearer {kid_token}"},
    )
    assert r.status_code == 200
    assert "profile" in r.json()
    assert "ETag" in r.headers


def test_sessions_batch_nested_array(kid_token):
    """Regression: client sent sessions: [[{ op: start, ... }]] by mistake."""
    sid = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    inner = {
        "op": "start",
        "session_id": sid,
        "game_id": "math_blast",
        "game_mode_id": "math_blast:flappy",
        "started_at": now,
    }
    r = client.post(
        "/api/v1/play/sessions/batch",
        json={"sessions": [[inner]]},
        headers={
            "Authorization": f"Bearer {kid_token}",
            "Idempotency-Key": f"nested-{sid}",
        },
    )
    assert r.status_code == 200
    assert r.json()["results"][0]["status"] == "active"


def test_sessions_and_events_batch(kid_token):
    sid = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    headers = {
        "Authorization": f"Bearer {kid_token}",
        "Idempotency-Key": f"test-{sid}",
    }
    start = client.post(
        "/api/v1/play/sessions/batch",
        json={
            "sessions": [
                {
                    "op": "start",
                    "session_id": sid,
                    "game_id": "math_blast",
                    "game_mode_id": "math_blast:candy",
                    "started_at": now,
                }
            ]
        },
        headers=headers,
    )
    assert start.status_code == 200

    ev = client.post(
        "/api/v1/play/events/batch",
        json={
            "session_id": sid,
            "events": [
                {
                    "client_seq": 1,
                    "occurred_at": now,
                    "event_type": "answer",
                    "level_id": "L001",
                    "skill_unit_id": "l1_add_within_10",
                    "correct": True,
                    "latency_ms": 1500,
                }
            ],
        },
        headers={"Authorization": f"Bearer {kid_token}"},
    )
    assert ev.status_code == 200
    assert ev.json()["accepted"] == 1

    end = client.post(
        "/api/v1/play/sessions/batch",
        json={
            "sessions": [
                {
                    "op": "end",
                    "session_id": sid,
                    "ended_at": now,
                    "summary": {
                        "duration_s": 120,
                        "level_id": "L001",
                        "stars": 3,
                        "accuracy": 0.9,
                        "questions_count": 10,
                        "correct_count": 9,
                    },
                }
            ]
        },
        headers={"Authorization": f"Bearer {kid_token}"},
    )
    assert end.status_code == 200
    assert end.json()["results"][0]["status"] == "completed"


def test_flappy_session_score_persisted(kid_token):
  sid = str(uuid4())
  now = datetime.now(timezone.utc).isoformat()
  headers = {
    "Authorization": f"Bearer {kid_token}",
    "Idempotency-Key": f"flappy-score-{sid}",
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

  ev = client.post(
    "/api/v1/play/events/batch",
    json={
      "session_id": sid,
      "events": [
        {
          "client_seq": 1,
          "occurred_at": now,
          "event_type": "answer",
          "skill_unit_id": "l1_add_within_10",
          "correct": True,
          "latency_ms": 800,
          "score_delta": 12,
        }
      ],
    },
    headers={"Authorization": f"Bearer {kid_token}"},
  )
  assert ev.status_code == 200

  end = client.post(
    "/api/v1/play/sessions/batch",
    json={
      "sessions": [
        {
          "op": "end",
          "session_id": sid,
          "ended_at": now,
          "summary": {
            "duration_s": 55,
            "score": 48,
            "questions_count": 5,
            "correct_count": 4,
            "accuracy": 0.8,
            "summary_json": {"tier": "T1", "combo_max": 3},
          },
        }
      ]
    },
    headers={
      "Authorization": f"Bearer {kid_token}",
      "Idempotency-Key": f"flappy-end-{sid}",
    },
  )
  assert end.status_code == 200
  assert end.json()["results"][0]["status"] == "completed"

  boot = client.get(
    "/api/v1/play/bootstrap",
    params={"game_id": "math_blast", "game_mode_id": "math_blast:flappy"},
    headers={"Authorization": f"Bearer {kid_token}"},
  )
  assert boot.status_code == 200
  assert boot.json()["game_stats"]["high_score"] >= 48


def test_flappy_personal_best_per_tier(kid_token):
    """Mỗi lớp (T1…T3) lưu kỷ lục riêng trong personal_best_by_tier."""
    now = datetime.now(timezone.utc).isoformat()
    scores = [("T1", 30), ("T2", 55), ("T3", 40)]

    for tier, score in scores:
        sid = str(uuid4())
        headers = {
            "Authorization": f"Bearer {kid_token}",
            "Idempotency-Key": f"flappy-tier-{tier}-{sid}",
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
                            "duration_s": 50,
                            "score": score,
                            "questions_count": 8,
                            "correct_count": 6,
                            "accuracy": 0.75,
                            "summary_json": {"tier": tier, "grade": int(tier[1])},
                        },
                    }
                ]
            },
            headers={
                "Authorization": f"Bearer {kid_token}",
                "Idempotency-Key": f"flappy-tier-end-{tier}-{sid}",
            },
        )
        assert end.status_code == 200

    boot = client.get(
        "/api/v1/play/bootstrap",
        params={"game_id": "math_blast", "game_mode_id": "math_blast:flappy"},
        headers={"Authorization": f"Bearer {kid_token}"},
    )
    assert boot.status_code == 200
    pb = boot.json()["flappy"]["personal_best"]
    assert pb.get("T2") == 55
    assert pb.get("T3") == 40
    assert int(pb.get("T1", 0)) >= 30
