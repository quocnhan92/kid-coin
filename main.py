from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import logging
import os
from app.core.database import engine, Base
from app.api.v1 import system as system_router
from app.api.v1 import users as users_router
from app.api.v1 import quests as quests_router
from app.api.v1 import rewards as rewards_router
from app.api.v1 import clubs as clubs_router
from app.core.middleware import RequestContextMiddleware # Import Middleware

# Import all models to ensure they are registered with Base
from app.models.user_family import Family, User, Role
from app.models.tasks_rewards import MasterTask, FamilyTask, MasterReward, FamilyReward
from app.models.logs_transactions import TaskLog, Transaction, RedemptionLog
from app.models.social import Club, ClubMember
from app.models.audit import AuditLog

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

# Include Routers - Modular API Structure
app.include_router(system_router.router, prefix="/api/v1/system", tags=["System"])
app.include_router(users_router.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(quests_router.router, prefix="/api/v1/quests", tags=["Quests"])
app.include_router(rewards_router.router, prefix="/api/v1/rewards", tags=["Rewards"])
app.include_router(clubs_router.router, prefix="/api/v1/clubs", tags=["Clubs"])

# Webpage Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
