import sys
import subprocess
import pkg_resources

# Tự động kiểm tra và cài đặt thư viện thiếu
def install_requirements():
    required = {'fastapi', 'uvicorn', 'jinja2', 'sqlalchemy', 'psycopg2-binary', 'python-multipart', 'python-jose', 'passlib', 'pydantic-settings'}
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed

    if missing:
        print(f"Missing libraries: {missing}. Installing...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])
            print("Libraries installed successfully. Please restart the program!")
            sys.exit(0) # Dừng chương trình để người dùng chạy lại (để load thư viện mới)
        except subprocess.CalledProcessError as e:
            print(f"Error installing libraries: {e}")
            sys.exit(1)

# Chạy hàm kiểm tra trước khi import các thư viện khác
try:
    import fastapi
    import uvicorn
    import jinja2
    import sqlalchemy
    import psycopg2
    import jose
except ImportError:
    install_requirements()

from fastapi import FastAPI, Request, Cookie
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.modules.auth import router as auth_router, models as auth_models
from app.modules.devices import router as devices_router, models as devices_models
from app.modules.bookings import router as bookings_router, models as bookings_models
from app.modules.audits import models as audit_models # Import model audit
from app.core.database import engine, Base
import time
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retry logic for database connection
def create_tables():
    retries = 10
    while retries > 0:
        try:
            logger.info(f"Attempting to connect to database... ({retries} retries left)")
            # Import all models here to ensure they are registered with Base
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully.")
            break
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            logger.info("Retrying in 5 seconds...")
            time.sleep(5)
            retries -= 1
    else:
        logger.error("Could not connect to the database after multiple attempts.")

create_tables()

app = FastAPI(title="CareLink", description="Personal Equipment Maintenance Manager")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include Routers
app.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])
app.include_router(devices_router.router, prefix="/devices", tags=["Devices"])
app.include_router(bookings_router.router, prefix="/bookings", tags=["Bookings"])

@app.get("/")
async def read_root(request: Request, access_token: Optional[str] = Cookie(None)):
    # Nếu có cookie access_token, chuyển hướng đến trang devices
    if access_token:
        # Lưu ý: Ở đây chỉ kiểm tra sự tồn tại, chưa xác thực token.
        # Để bảo mật hơn, cần có một dependency để giải mã và xác thực token.
        return RedirectResponse(url="/devices")
    
    # Nếu không có cookie, hiển thị trang đăng nhập
    return templates.TemplateResponse("index.html", {"request": request, "title": "Login to CareLink"})

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    # Cho phép chạy trực tiếp file này trong PyCharm để debug
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
