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
from app.api.v1.play import router as play_router
from app.api.v1.learning import router as learning_router
from app.core.scheduler import start_scheduler, shutdown_scheduler
from app.services import admin_service
from app.core.middleware import RequestContextMiddleware
from app.locale.middleware import LocaleMiddleware
from app.locale.jinja import template_context
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
from app.models.learning import (
    LearningSubject,
    LearningChapter,
    LearningLesson,
    LearningChapterProgress,
    LearningLessonProgress,
    LearningDailySummary,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security Configuration for Docs
ENV = os.getenv("ENV", "dev") # default to dev
app = FastAPI(
    title="Kid Coin", 
    description="Family Task and Reward System",
    docs_url="/docs" if ENV != "prod" else None,
    redoc_url="/redoc" if ENV != "prod" else None,
)

# Add Middleware (locale after request id)
app.add_middleware(LocaleMiddleware)
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


def render_page(request: Request, template_name: str, extra: dict | None = None):
    """HTML page with locale/market context + message bundles for JS."""
    ctx = template_context(request, extra)
    return templates.TemplateResponse(request, template_name, ctx)


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
app.include_router(play_router, prefix="/api/v1/play", tags=["Play"])
app.include_router(learning_router, prefix="/api/v1/learning", tags=["Learning"])

# --- Startup Event for Seeding Data ---
@app.on_event("startup")
def startup_event():
    """Seed + scheduler. Migration chạy mỗi lần startup (nhanh nếu đã head)."""
    if os.getenv("SKIP_STARTUP_MIGRATION", "").lower() not in ("1", "true", "yes"):
        from app.core.migration_runner import run_alembic_upgrade

        try:
            run_alembic_upgrade()
        except Exception as mig_err:
            logger.error("Migration failed at startup — API learning có thể 500: %s", mig_err)
    try:
        seed_initial_data()
    except Exception as seed_err:
        logger.error("Startup seed failed (app vẫn chạy): %s", seed_err)
    start_scheduler()
    try:
        from app.core.game_registry import register_game_routes, register_legacy_redirects

        mounted = register_game_routes(app, render_page)
        register_legacy_redirects(app)
        logger.info("Game registry: %s dynamic routes mounted", mounted)
    except Exception as reg_err:
        logger.warning("Game registry skipped: %s", reg_err)

def seed_initial_data():
    # NOTE: alembic upgrade head đã được chạy bởi entrypoint.sh trước khi uvicorn start.
    # Không gọi run_alembic_upgrade() ở đây để tránh double migration.

    db = SessionLocal()
    try:
        from app.services.play_catalog_seed import seed_play_catalog
        from app.services.english_catalog_seed import ensure_english_shooter_catalog
        from app.services.platform_seed import seed_platform

        seed_play_catalog(db)
        ensure_english_shooter_catalog(db)
        try:
            seed_platform(db)
        except Exception as plat_err:
            logger.warning("Platform seed skipped (run migration 017): %s", plat_err)
        try:
            from app.services.learning_curriculum_seed import seed_learning_curriculum
            seed_learning_curriculum(db)
        except Exception as learn_err:
            logger.warning("Learning curriculum seed skipped: %s", learn_err)

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
        logger.error("Seeding failed: %s", e)
        db.rollback()
    finally:
        try:
            admin_service.seed_admin(db)
        except Exception as admin_err:
            logger.warning("Admin seed skipped: %s", admin_err)
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
    return templates.TemplateResponse(request, "login.html")


@app.get("/logout")
async def logout_page():
    """Đăng xuất bố mẹ/bé — chỉ xóa access_token, không ảnh hưởng admin_token."""
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response


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

    return templates.TemplateResponse(request, "parent_dashboard.html")

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
        
    return templates.TemplateResponse(request, "kid_dashboard.html")

@app.get("/learning", response_class=HTMLResponse)
async def read_learning_page(request: Request, access_token: Optional[str] = Cookie(None)):
    if not access_token:
        return RedirectResponse("/login")
    db = SessionLocal()
    user = get_user_from_cookie(access_token, db)
    db.close()
    if not user:
        response = RedirectResponse("/login")
        response.delete_cookie("access_token")
        return response
    return render_page(request, "learning/index.html")

# --- Game Hub Routes (Independent Module) ---

@app.get("/set-market/{market_code}")
async def set_market_cookie(market_code: str, request: Request, next: str = "/"):
    """Set market + default locale cookies then redirect (market switcher)."""
    from app.locale.registry import MARKETS

    code = market_code.lower()
    if code not in MARKETS:
        return RedirectResponse(next or "/")
    m = MARKETS[code]
    target = next if next.startswith("/") else "/"
    response = RedirectResponse(url=target)
    response.set_cookie("kidcoin_market", code, max_age=60 * 60 * 24 * 365, samesite="lax")
    response.set_cookie("kidcoin_locale", m.default_locale, max_age=60 * 60 * 24 * 365, samesite="lax")
    return response


@app.get("/game", response_class=HTMLResponse)
async def game_hub(request: Request):
    """Trang chủ kho game mini"""
    return templates.TemplateResponse(request, "game_hub.html")

@app.get("/game/rewards", response_class=HTMLResponse)
async def game_reward_playground(request: Request):
    """Reward Playground — fun games unlocked by learning"""
    return templates.TemplateResponse(request, "games/reward_playground.html")

@app.get("/game/snake", response_class=HTMLResponse)
async def game_snake(request: Request):
    """Game Rắn săn mồi"""
    from app.core.reward_route_guard import reward_route_guard

    blocked = reward_route_guard(request)
    if blocked:
        return blocked
    return templates.TemplateResponse(request, "games/snake.html")

@app.get("/game/2048", response_class=HTMLResponse)
async def game_2048(request: Request):
    """Game 2048"""
    from app.core.reward_route_guard import reward_route_guard

    blocked = reward_route_guard(request)
    if blocked:
        return blocked
    return templates.TemplateResponse(request, "games/2048.html")

@app.get("/game/memory", response_class=HTMLResponse)
async def game_memory(request: Request):
    """Game Lật bài — reward zone"""
    from app.core.reward_route_guard import reward_route_guard

    blocked = reward_route_guard(request)
    if blocked:
        return blocked
    return templates.TemplateResponse(request, "games/memory.html")

@app.get("/game/memory-learn", response_class=HTMLResponse)
async def game_memory_learn(request: Request):
    """Gà Nhớ bài — learning zone"""
    return templates.TemplateResponse(request, "games/memory.html")

@app.get("/privacy-play", response_class=HTMLResponse)
async def privacy_play(request: Request):
    return templates.TemplateResponse(request, "privacy_play.html")

@app.get("/game/flappy", response_class=HTMLResponse)
async def game_flappy(request: Request):
    """Game Flappy Baby"""
    from app.core.reward_route_guard import reward_route_guard

    blocked = reward_route_guard(request)
    if blocked:
        return blocked
    return templates.TemplateResponse(request, "games/flappy.html")

@app.get("/game/math-blast", response_class=HTMLResponse)
async def game_math_blast(request: Request):
    """Game Math Blast"""
    return templates.TemplateResponse(request, "games/math_blast.html")

@app.get("/game/math-blast-v2", response_class=HTMLResponse)
async def game_math_blast_v2_hub(request: Request):
    """Math Blast v2 — hub chọn SKU (Candy / Flappy / Arcade)"""
    return templates.TemplateResponse(request, "games/math_blast_v2_hub.html")

@app.get("/game/math-blast-v2/candy", response_class=HTMLResponse)
async def game_math_blast_v2_candy(request: Request):
    """Math Blast v2 — Candy Map prototype"""
    return templates.TemplateResponse(request, "games/math_blast_v2_candy.html")

@app.get("/game/math-blast-v2/flappy", response_class=HTMLResponse)
async def game_math_blast_v2_flappy(request: Request):
    """Math Blast v2 — Flappy Sprint prototype"""
    return templates.TemplateResponse(request, "games/math_blast_v2_flappy.html")

@app.get("/game/math-blast-v2/arcade", response_class=HTMLResponse)
async def game_math_blast_v2_arcade(request: Request):
    """Math Blast v2 — Arcade prototype"""
    return templates.TemplateResponse(request, "games/math_blast_v2_arcade.html")

@app.get("/game/english-shooter/math", response_class=HTMLResponse)
async def game_english_math_hub(request: Request):
    return render_page(request, "games/english_math_hub.html")

@app.get("/game/english-shooter/math/v1", response_class=HTMLResponse)
async def game_english_math_v1(request: Request):
    return render_page(request, "games/english_math_v1.html")

@app.get("/game/english-shooter/math/v2", response_class=HTMLResponse)
async def game_english_math_v2_hub(request: Request):
    return render_page(request, "games/english_math_v2_hub.html")

@app.get("/game/english-shooter/math/v2/candy", response_class=HTMLResponse)
async def game_english_math_v2_candy(request: Request):
    return render_page(request, "games/english_math_v2_candy.html")

@app.get("/game/english-shooter/math/v2/flappy", response_class=HTMLResponse)
async def game_english_math_v2_flappy(request: Request):
    return render_page(request, "games/english_math_v2_flappy.html")

@app.get("/game/english-shooter/math/v2/arcade", response_class=HTMLResponse)
async def game_english_math_v2_arcade(request: Request):
    return render_page(request, "games/english_math_v2_arcade.html")

@app.get("/game/english-shooter", response_class=HTMLResponse)
async def game_english_shooter_hub(request: Request):
    """English Shooter — hub chọn chế độ"""
    return templates.TemplateResponse(request, "games/english_shooter_hub.html")

@app.get("/game/english-shooter/vocab", response_class=HTMLResponse)
async def game_english_shooter_vocab(request: Request):
    """English Shooter — Vocab Shooter (bắn từ vựng + mind map)"""
    return templates.TemplateResponse(request, "games/english_shooter_vocab.html")

@app.get("/game/english-shooter/lily", response_class=HTMLResponse)
async def game_english_shooter_lily(request: Request):
    """English Shooter — Lily Bakery & Fashion (kéo từ vựng)"""
    return templates.TemplateResponse(request, "games/english_shooter_lily.html")

@app.get("/game/english-shooter/prairie", response_class=HTMLResponse)
async def game_english_shooter_prairie(request: Request):
    """English Shooter — Thảo nguyên (từ vựng)"""
    return templates.TemplateResponse(request, "games/english_shooter_prairie.html")

@app.get("/game/english-shooter/city", response_class=HTMLResponse)
async def game_english_shooter_city(request: Request):
    """English Shooter — Bảo vệ thành phố (ngữ pháp + nói)"""
    return templates.TemplateResponse(request, "games/english_shooter_city.html")

@app.get("/game/english-shooter/boss", response_class=HTMLResponse)
async def game_english_shooter_boss(request: Request):
    """English Shooter — Đại Boss (đoạn văn + speaking)"""
    return templates.TemplateResponse(request, "games/english_shooter_boss.html")

@app.get("/game/block-breaker", response_class=HTMLResponse)
async def game_block_breaker(request: Request):
    """Game Block Breaker"""
    return templates.TemplateResponse(request, "games/block_breaker.html")


_REWARD_ROUTES_REGISTERED = {
    "/game/snake",
    "/game/2048",
    "/game/memory",
    "/game/flappy",
    "/game/block-breaker",
}

REWARD_PLAY_TEMPLATES = {
    "/game/minesweeper": "games/minesweeper.html",
    "/game/pong-2p": "games/pong_2p.html",
    "/game/snake-2p": "games/snake_2p.html",
    "/game/air-hockey-2p": "games/air_hockey_2p.html",
    "/game/hextris": "games/hextris.html",
    "/game/ohh1": "games/ohh1.html",
    "/game/ohn0": "games/ohn0.html",
    "/game/reversi": "games/reversi.html",
    "/game/tower-defense": "games/tower_defense_lite.html",
    "/game/connect4-2p": "games/connect4_2p.html",
    "/game/tic-tac-toe-2p": "games/tic_tac_toe_2p.html",
    "/game/coop-catch-2p": "games/coop_catch_2p.html",
    "/game/memory-duel-2p": "games/memory_duel_2p.html",
    "/game/bubble-pop-2p": "games/bubble_pop_2p.html",
    "/game/checkers-lite-2p": "games/checkers_lite_2p.html",
    "/game/maze-race-2p": "games/maze_race_2p.html",
    "/game/draw-guess-2p": "games/draw_guess_2p.html",
    "/game/rhythm-duel-2p": "games/rhythm_duel_2p.html",
    "/game/gomoku-lite-2p": "games/gomoku_lite_2p.html",
}


def _reward_page_handler(template_name: str):
    async def handler(request: Request):
        from app.core.reward_route_guard import reward_route_guard

        blocked = reward_route_guard(request)
        if blocked:
            return blocked
        return templates.TemplateResponse(request, template_name)

    return handler


def _register_reward_play_routes() -> None:
    for route, tpl in REWARD_PLAY_TEMPLATES.items():
        app.add_api_route(
            route,
            _reward_page_handler(tpl),
            methods=["GET"],
            response_class=HTMLResponse,
            name=f"reward_play_{route.replace('/', '_')}",
        )
        _REWARD_ROUTES_REGISTERED.add(route)


def _register_reward_stub_routes() -> None:
    from app.data.reward_playground_catalog import REWARD_GAMES

    skip = _REWARD_ROUTES_REGISTERED | frozenset(REWARD_PLAY_TEMPLATES.keys())

    for game in REWARD_GAMES:
        route = game["route"]
        if route in skip:
            continue

        async def handler(request: Request, g=game):
            from app.core.reward_route_guard import reward_route_guard

            blocked = reward_route_guard(request)
            if blocked:
                return blocked
            return templates.TemplateResponse(
                request,
                "games/reward_stub.html",
                {
                    "game_id": g["id"],
                    "game_title": g["title"],
                    "game_emoji": g["emoji"],
                    "game_desc": g["desc_en"],
                    "rollout_status": g.get("rollout_status", "draft"),
                },
            )

        app.add_api_route(
            route,
            handler,
            methods=["GET"],
            response_class=HTMLResponse,
            name=f"reward_stub_{game['id']}",
        )
        _REWARD_ROUTES_REGISTERED.add(route)


_register_reward_play_routes()


@app.get("/game/rhythm-trainer", response_class=HTMLResponse, name="reward_play_rhythm_trainer")
async def reward_rhythm_trainer(request: Request):
    from app.core.reward_route_guard import reward_route_guard

    blocked = reward_route_guard(request)
    if blocked:
        return blocked
    return templates.TemplateResponse(request, "games/rhythm_trainer.html")


@app.get("/game/paint-sandbox", response_class=HTMLResponse, name="reward_play_paint_sandbox")
async def reward_paint_sandbox(request: Request):
    from app.core.reward_route_guard import reward_route_guard

    blocked = reward_route_guard(request)
    if blocked:
        return blocked
    return templates.TemplateResponse(request, "games/paint_sandbox.html")


_REWARD_ROUTES_REGISTERED.update({"/game/rhythm-trainer", "/game/paint-sandbox"})


@app.get("/game/space-fly", response_class=HTMLResponse, name="reward_play_space_fly")
async def reward_space_fly(request: Request):
    from app.core.reward_route_guard import reward_route_guard

    blocked = reward_route_guard(request)
    if blocked:
        return blocked
    return templates.TemplateResponse(request, "games/space_fly.html")


_REWARD_ROUTES_REGISTERED.add("/game/space-fly")


@app.get("/game/fly-shooter", response_class=HTMLResponse, name="reward_play_fly_shooter")
async def reward_fly_shooter(request: Request):
    from app.core.reward_route_guard import reward_route_guard

    blocked = reward_route_guard(request)
    if blocked:
        return blocked
    return templates.TemplateResponse(request, "games/fly_shooter.html")


_REWARD_ROUTES_REGISTERED.add("/game/fly-shooter")
_register_reward_stub_routes()


@app.get("/test_voice", response_class=HTMLResponse)
async def test_voice_page():
    """Trang test voice recognition"""
    with open("app/static/test_voice.html", "r", encoding="utf-8") as f:
        return f.read()


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
Sitemap: https://choimahoc.io.vn/sitemap.xml"""


@app.get("/sitemap.xml", include_in_schema=False)
async def sitemap_xml():
    """sitemap.xml — danh sách URLs cho search engine index"""
    from datetime import date
    today = date.today().isoformat()
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://choimahoc.io.vn/login</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://choimahoc.io.vn/game</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>"""
    return Response(content=content, media_type="application/xml")


if __name__ == "__main__":
    import uvicorn

    if os.getenv("SKIP_STARTUP_MIGRATION", "").lower() not in ("1", "true", "yes"):
        try:
            from app.core.migration_runner import run_alembic_upgrade

            run_alembic_upgrade()
        except Exception as mig_err:
            logger.error("Pre-start migration failed: %s", mig_err)

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
