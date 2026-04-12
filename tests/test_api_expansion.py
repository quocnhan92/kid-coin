import os
import pytest
import uuid
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Force SQLite for testing
TEST_DB_FILE = "test_expansion.db"
os.environ["DATABASE_URL"] = f"sqlite:///./{TEST_DB_FILE}"

from main import app
from app.core.database import Base, get_db
from app.models.user_family import User, Role, Family
from app.models.admin import AdminUser
from app.models.tasks_rewards import MasterTask, MasterReward
from app.models.teen import TeenContract, PersonalProject, ContractStatus, ProjectStatus
from app.core.security import get_password_hash

# Note: Base here comes from app.core.database which now uses sqlite engine
# because of the os.environ set at the top.

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    
    from app.core.database import engine
    from app.core.database import Base
    Base.metadata.create_all(bind=engine)
    yield
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

@pytest.fixture
def db_session():
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_admin_flow(client, db_session):
    # 1. Create Admin
    admin_id = uuid.uuid4()
    admin = AdminUser(
        id=admin_id,
        username="admin_test",
        password_hash=get_password_hash("admin123"),
        display_name="Admin Test"
    )
    db_session.add(admin)
    db_session.commit()

    # 2. Admin Login
    login_resp = client.post("/api/v1/admin/auth/login", json={
        "username": "admin_test",
        "password": "admin123"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create Master Task
    task_resp = client.post("/api/v1/admin/master-tasks", json={
        "name": "Super Clean",
        "suggested_value": 100,
        "category": "Việc nhà"
    }, headers=headers)
    assert task_resp.status_code == 200
    assert task_resp.json()["name"] == "Super Clean"

    # 4. Get Dashboard
    dash_resp = client.get("/api/v1/admin/analytics/dashboard", headers=headers)
    assert dash_resp.status_code == 200
    assert "financials" in dash_resp.json()

    # 5. Update Master Task
    tid = task_resp.json()["id"]
    update_resp = client.put(f"/api/v1/admin/master-tasks/{tid}", json={"suggested_value": 150}, headers=headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["suggested_value"] == 150

    # 6. Avatar Item CRUD
    item_resp = client.post("/api/v1/admin/avatar-items", json={
        "name": "Cool Sunglasses", "item_type": "ACCESSORY", "image_url": "sunglasses.png", "price_coins": 50
    }, headers=headers)
    assert item_resp.status_code == 200
    
    # 7. Stats & Logs
    stats_resp = client.get("/api/v1/admin/stats/daily-active", headers=headers)
    assert stats_resp.status_code == 200
    
    logs_resp = client.get("/api/v1/admin/logs/errors", headers=headers)
    assert logs_resp.status_code == 200

def test_teen_and_parent_flow(client, db_session):
    # 1. Setup Family, Parent, Teen
    fid = uuid.uuid4()
    db_session.add(Family(id=fid, name="Test Family"))
    
    parent = User(id=uuid.uuid4(), family_id=fid, role=Role.PARENT, username="parent_test", display_name="Parent Test")
    kid = User(id=uuid.uuid4(), family_id=fid, role=Role.KID, username="kid_test", display_name="Kid Test", is_teen_mode=True, charity_rate=0)
    
    db_session.add_all([parent, kid])
    db_session.commit()

    # Setup overrides for authentication
    from app.api import deps
    app.dependency_overrides[deps.get_current_user] = lambda: kid
    app.dependency_overrides[deps.get_current_admin] = lambda: "admin:admin_id"

    # 2. Teen drafts contract
    contract_resp = client.post("/api/v1/teen/contracts", json={
        "title": "Gym Habit",
        "description": "Go to gym 3 times a week",
        "salary_coins": 300,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    })
    assert contract_resp.status_code == 200
    cid = contract_resp.json()["id"]

    # 3. Teen signs contract
    sign_resp = client.post(f"/api/v1/teen/contracts/{cid}/sign")
    assert sign_resp.status_code == 200
    assert sign_resp.json()["contract_status"] == "ACTIVE"

    # 4. Teen submits project milestone
    pid = uuid.uuid4()
    project = PersonalProject(
        id=pid, kid_id=kid.id, family_id=fid, title="Learn Guitar",
        total_budget=1000,
        milestones=[{"title": "Lesson 1", "reward": 200, "status": "PENDING"}],
        status=ProjectStatus.ACTIVE
    )
    db_session.add(project)
    db_session.commit()

    sub_resp = client.post(f"/api/v1/teen/projects/{pid}/milestones/0/submit", json={
        "note": "Finished first chord", "proof_url": "http://img.png"
    })
    assert sub_resp.status_code == 200

    # 5. Parent verifies milestone
    from app.api import deps
    app.dependency_overrides[deps.get_current_user] = lambda: parent
    
    verify_resp = client.post(f"/api/v1/parent/teen/projects/{pid}/milestones/0/verify", json={
        "approved": True, "comment": "Good job!"
    })
    assert verify_resp.status_code == 200
    
    # 6. Check balance
    db_session.refresh(kid)
    assert kid.current_coin == 200

    app.dependency_overrides.clear()
