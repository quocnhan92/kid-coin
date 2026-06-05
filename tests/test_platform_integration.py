"""
Platform API integration tests — PostgreSQL + migrated schema required.
"""
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from main import app
from app.core.database import SessionLocal, get_db
from app.core.security import create_access_token, get_password_hash
from app.models.admin import AdminUser
from app.models.user_family import User, Role, Family
from app.services.feature_flag_service import upsert_flag
from app.services.platform_seed import seed_platform

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def require_postgres():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db.execute(text("SELECT 1 FROM feature_flags LIMIT 1"))
    except OperationalError as exc:
        pytest.skip(f"PostgreSQL/migration 017 required: {exc}")
    except Exception as exc:
        pytest.skip(f"Platform tables missing — run alembic upgrade head: {exc}")
    finally:
        db.close()


@pytest.fixture
def db_session(require_postgres):
    db = SessionLocal()
    try:
        seed_platform(db)
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def kid_token(db_session):
    fam = db_session.query(Family).first()
    if not fam:
        fam = Family(id=uuid.uuid4(), name="PG Fam", parent_pin="1234")
        db_session.add(fam)
        db_session.flush()
    kid = (
        db_session.query(User)
        .filter(User.family_id == fam.id, User.role == Role.KID)
        .first()
    )
    if not kid:
        kid = User(id=uuid.uuid4(), family_id=fam.id, role=Role.KID, display_name="Kid")
        db_session.add(kid)
    db_session.commit()
    return create_access_token(str(kid.id))


class TestSystemApiIntegration:
    def test_features_endpoint(self, client):
        r = client.get("/api/v1/system/features")
        assert r.status_code == 200
        assert "core.auth" in r.json()["flags"]

    def test_public_games(self, client):
        r = client.get("/api/v1/system/public-games")
        assert r.status_code == 200
        assert isinstance(r.json()["games"], list)

    def test_api_version_header(self, client):
        r = client.get("/api/v1/system/health")
        assert r.headers.get("X-API-Version") == "1"


class TestFeatureGatingIntegration:
    def test_reward_playground_disabled(self, client, db_session, kid_token):
        upsert_flag(db_session, "play.reward_playground", False)
        db_session.commit()
        r = client.get(
            "/api/v1/play/rewards",
            headers={"Authorization": f"Bearer {kid_token}"},
        )
        assert r.status_code == 404

    def test_play_games_launch_url(self, client, kid_token):
        r = client.get(
            "/api/v1/play/games",
            headers={"Authorization": f"Bearer {kid_token}"},
        )
        assert r.status_code == 200
        games = r.json()["games"]
        mb = next((g for g in games if g["id"] == "math_blast"), None)
        if mb:
            assert mb.get("launch_url")


class TestAdminFlagsIntegration:
    def test_admin_crud_flags(self, client, db_session):
        admin = AdminUser(
            id=uuid.uuid4(),
            username=f"adm_{uuid.uuid4().hex[:8]}",
            password_hash=get_password_hash("pass123"),
            display_name="Admin",
        )
        db_session.add(admin)
        db_session.commit()
        login = client.post(
            "/api/v1/admin/auth/login",
            json={"username": admin.username, "password": "pass123"},
        )
        assert login.status_code == 200
        h = {"Authorization": f"Bearer {login.json()['access_token']}"}
        lst = client.get("/api/v1/admin/feature-flags", headers=h)
        assert lst.status_code == 200
        upd = client.put(
            "/api/v1/admin/feature-flags/mod.ads",
            json={"enabled": False, "scope": "global"},
            headers=h,
        )
        assert upd.status_code == 200
