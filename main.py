from fastapi import FastAPI, Request, Cookie, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import logging
import os
from app.core.database import engine, Base, SessionLocal
from app.api.v1 import system as system_router
from app.api.v1 import users as users_router
from app.api.v1 import quests as quests_router
from app.api.v1 import rewards as rewards_router
from app.api.v1 import clubs as clubs_router
from app.api.v1 import parent as parent_router
from app.api.v1 import auth as auth_router
from app.core.middleware import RequestContextMiddleware
from app.models.user_family import User, Role, Family
from typing import Optional

# Import all models to ensure they are registered with Base
from app.models.user_family import Family, User, Role
from app.models.tasks_rewards import MasterTask, FamilyTask, MasterReward, FamilyReward
from app.models.logs_transactions import TaskLog, Transaction, RedemptionLog
from app.models.social import Club, ClubMember
from app.models.audit import AuditLog
from app.models.devices import FamilyDevice

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")

app = FastAPI(title="Kid Coin", description="Family Task and Reward System")

# Add Middleware
app.add_middleware(RequestContextMiddleware)

# Mount static files
if not os.path.exists("app/static"):
    os.makedirs("app/static")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
if not os.path.exists("app/templates"):
    os.makedirs("app/templates")
templates = Jinja2Templates(directory="app/templates")

# Include Routers
app.include_router(system_router.router, prefix="/api/v1/system", tags=["System"])
app.include_router(users_router.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(quests_router.router, prefix="/api/v1/quests", tags=["Quests"])
app.include_router(rewards_router.router, prefix="/api/v1/rewards", tags=["Rewards"])
app.include_router(clubs_router.router, prefix="/api/v1/clubs", tags=["Clubs"])
app.include_router(parent_router.router, prefix="/api/v1/parent", tags=["Parent"])
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Auth"])

# --- Startup Event for Seeding Data ---
@app.on_event("startup")
def seed_initial_data():
    db = SessionLocal()
    try:
        # Check if any user exists
        if db.query(User).first():
            logger.info("Data already exists. Skipping seed.")
            return

        logger.info("Seeding initial data...")
        from uuid import uuid4
        
        # 1. Create Family
        family = Family(id=uuid4(), name="Nhà Cà Rốt", parent_pin="1234")
        db.add(family)
        db.flush() # flush to get ID if needed, though we set UUID manually

        # 2. Create Parent
        parent = User(
            id=uuid4(), 
            family_id=family.id, 
            role=Role.PARENT, 
            display_name="Bố Tuấn", 
            username="botuan",
            avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix"
        )
        db.add(parent)

        # 3. Create Kids
        kid1 = User(
            id=uuid4(), 
            family_id=family.id, 
            role=Role.KID, 
            display_name="Bé Bin", 
            current_coin=50,
            avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=Bin"
        )
        kid2 = User(
            id=uuid4(), 
            family_id=family.id, 
            role=Role.KID, 
            display_name="Em Na", 
            current_coin=120,
            avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=Na"
        )
        db.add(kid1)
        db.add(kid2)

        # 4. Create Master Tasks (Dữ liệu mồi)
        from app.models.tasks_rewards import MasterTask, Category, FamilyTask
        
        tasks = [
            MasterTask(name="Đánh răng", category=Category.CHORE, suggested_value=5, icon_url="🪥"),
            MasterTask(name="Gấp chăn màn", category=Category.CHORE, suggested_value=10, icon_url="🛏️"),
            MasterTask(name="Làm bài tập", category=Category.STUDY, suggested_value=20, icon_url="📚"),
        ]
        db.add_all(tasks)
        db.flush() # to get IDs

        # 5. Create Family Tasks (Assign to family)
        for mt in tasks:
            ft = FamilyTask(
                family_id=family.id,
                master_task_id=mt.id,
                name=mt.name,
                points_reward=mt.suggested_value,
                is_active=True
            )
            db.add(ft)

        # 6. Create Rewards
        from app.models.tasks_rewards import FamilyReward
        rewards = [
            FamilyReward(family_id=family.id, name="Xem TV 30p", points_cost=50, is_active=True),
            FamilyReward(family_id=family.id, name="Ăn kem", points_cost=100, is_active=True),
        ]
        db.add_all(rewards)

        db.commit()
        logger.info("Seeding completed successfully!")

    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

# --- Webpage Routes ---

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, user_id: Optional[str] = Cookie(None)):
    if not user_id:
        return RedirectResponse("/login")
    
    # Check Role to redirect to correct dashboard
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    
    if not user:
         response = RedirectResponse("/login")
         response.delete_cookie("user_id")
         return response

    if user.role == Role.KID:
        return RedirectResponse("/kid")
    
    # Parent Dashboard
    return templates.TemplateResponse("parent_dashboard.html", {"request": request})

@app.get("/kid", response_class=HTMLResponse)
async def read_kid_dashboard(request: Request, user_id: Optional[str] = Cookie(None)):
    if not user_id:
        return RedirectResponse("/login")
    return templates.TemplateResponse("kid_dashboard.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
