from fastapi import FastAPI, Request, Cookie, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse, Response
import logging
import os
import threading
from sqlalchemy.orm import Session # Added missing import
from app.core.database import SessionLocal
from app.api.v1 import system as system_router
from app.api.v1 import users as users_router
from app.api.v1 import quests as quests_router
from app.api.v1 import rewards as rewards_router
from app.api.v1 import clubs as clubs_router
from app.api.v1 import parent as parent_router
from app.api.v1 import auth as auth_router
from app.api.v1 import upload as upload_router
from app.api.v1 import notifications as notifications_router
from app.api.v1 import gamification as gamification_router
from app.api.v1 import finance as finance_router
from app.api.v1 import thinking as thinking_router
from app.api.v1 import social as social_router
from app.api.v1 import teen as teen_router
from app.api.v1 import admin as admin_router
from app.core.scheduler import start_scheduler, shutdown_scheduler
from app.services import admin_service
from app.core.middleware import RequestContextMiddleware
from app.models.user_family import User, Role, Family
from typing import Optional
from app.core.security import decode_access_token

# Import all models to ensure they are registered with Base
from app.models.user_family import Family, User, Role
from app.models.tasks_rewards import MasterTask, FamilyTask, MasterReward, FamilyReward
from app.models.logs_transactions import TaskLog, Transaction, RedemptionLog
from app.models.social import Club, ClubMember
from app.models.audit import AuditLog
from app.models.devices import FamilyDevice
from app.models.notifications import Notification

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Kid Coin", description="Family Task and Reward System")

# Add Middleware
app.add_middleware(RequestContextMiddleware)

# Mount static files
if not os.path.exists("app/static"):
    os.makedirs("app/static")
if not os.path.exists("app/static/uploads"):
    os.makedirs("app/static/uploads")
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
app.include_router(upload_router.router, prefix="/api/v1/upload", tags=["Upload"])
app.include_router(notifications_router.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(gamification_router.router, prefix="/api/v1/gamification", tags=["Gamification"])
app.include_router(finance_router.router, prefix="/api/v1/finance", tags=["Finance"])
app.include_router(thinking_router.router, prefix="/api/v1/thinking", tags=["Thinking"])
app.include_router(social_router.router, prefix="/api/v1/social", tags=["Social"])
app.include_router(teen_router.router, prefix="/api/v1/teen", tags=["Teen"])
app.include_router(admin_router.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(admin_router.router, prefix="/admin", tags=["Admin UI"])

# --- Startup Event for Seeding Data ---
@app.on_event("startup")
def startup_event():
    seed_initial_data()
    start_scheduler()

def seed_initial_data():
    # NOTE: alembic upgrade head đã được chạy bởi entrypoint.sh trước khi uvicorn start.
    # Không gọi run_alembic_upgrade() ở đây để tránh double migration.

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
        from app.models.tasks_rewards import MasterTask, Category, FamilyTask, VerificationType, MasterReward
        
        tasks = [
            MasterTask(name="Đánh răng", category=Category.PERSONAL, suggested_value=5, icon_url="🪥", verification_type=VerificationType.AUTO_APPROVE),
            MasterTask(name="Gấp chăn màn", category=Category.CHORE, suggested_value=10, icon_url="🛏️", verification_type=VerificationType.REQUIRE_PHOTO),
            MasterTask(name="Làm bài tập", category=Category.STUDY, suggested_value=20, icon_url="📚", verification_type=VerificationType.REQUIRE_PARENT_CHECK),
        ]
        db.add_all(tasks)

        # 4.1 Create Master Rewards
        rewards_master = [
            MasterReward(name="Xem TV 30p", suggested_cost=50, icon_url="📺"),
            MasterReward(name="Ăn kem", suggested_cost=100, icon_url="🍦"),
            MasterReward(name="Thêm 15p chơi game", suggested_cost=30, icon_url="🎮"),
        ]
        db.add_all(rewards_master)
        db.flush() # to get IDs

        # 5. Create Family Tasks (Assign to family)
        for mt in tasks:
            ft = FamilyTask(
                family_id=family.id,
                master_task_id=mt.id,
                name=mt.name,
                points_reward=mt.suggested_value,
                category=mt.category,
                verification_type=mt.verification_type,
                is_active=True
            )
            db.add(ft)

        # 6. Create Rewards
        from app.models.tasks_rewards import FamilyReward
        for mr in rewards_master[:2]: # Assign first 2 to family
            fr = FamilyReward(
                family_id=family.id,
                name=mr.name,
                points_cost=mr.suggested_cost,
                is_active=True
            )
            db.add(fr)

        db.commit()
        logger.info("Seeding completed successfully!")

    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        db.rollback()
    finally:
        # Seed Admin User
        admin_service.seed_admin(db)
        db.close()

@app.on_event("shutdown")
def shutdown_event():
    shutdown_scheduler()

# --- Helper to extract user from JWT cookie ---
def get_user_from_cookie(access_token: Optional[str], db: Session) -> Optional[User]:
    if not access_token:
        return None
    payload = decode_access_token(access_token)
    if payload and "sub" in payload:
        return db.query(User).filter(User.id == payload["sub"]).first()
    return None

# --- Webpage Routes ---

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, access_token: Optional[str] = Cookie(None)):
    if not access_token:
        return RedirectResponse("/login")
    
    db = SessionLocal()
    user = get_user_from_cookie(access_token, db)
    db.close()
    
    if not user:
         response = RedirectResponse("/login")
         response.delete_cookie("access_token")
         return response

    if user.role == Role.KID:
        return RedirectResponse("/kid")
    
    # Parent Dashboard
    return RedirectResponse("/parent")

@app.get("/parent", response_class=HTMLResponse)
async def read_parent_dashboard(request: Request, access_token: Optional[str] = Cookie(None)):
    if not access_token:
        return RedirectResponse("/login")

    db = SessionLocal()
    user = get_user_from_cookie(access_token, db)
    db.close()

    if not user or user.role != Role.PARENT:
        response = RedirectResponse("/login")
        response.delete_cookie("access_token")
        return response

    return templates.TemplateResponse("parent_dashboard.html", {"request": request})

@app.get("/kid", response_class=HTMLResponse)
async def read_kid_dashboard(request: Request, access_token: Optional[str] = Cookie(None)):
    if not access_token:
        return RedirectResponse("/login")
        
    db = SessionLocal()
    user = get_user_from_cookie(access_token, db)
    db.close()
    
    if not user:
        response = RedirectResponse("/login")
        response.delete_cookie("access_token")
        return response
        
    return templates.TemplateResponse("kid_dashboard.html", {"request": request})


# ===== SEO ROUTES =====

@app.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
async def robots_txt():
    """robots.txt — hướng dẫn search engine crawl"""
    return """User-agent: *
Allow: /login
Allow: /static/
Disallow: /parent
Disallow: /kid
Disallow: /admin
Disallow: /api/
Disallow: /analytics

# Sitemap location
Sitemap: https://kidcoin.app/sitemap.xml"""


@app.get("/sitemap.xml", include_in_schema=False)
async def sitemap_xml():
    """sitemap.xml — danh sách URLs cho search engine index"""
    from datetime import date
    today = date.today().isoformat()
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://kidcoin.app/login</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
    <xhtml:link rel="alternate" hreflang="vi" href="https://kidcoin.app/login"/>
  </url>
</urlset>"""
    return Response(content=content, media_type="application/xml")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
