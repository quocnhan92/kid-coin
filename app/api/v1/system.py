from fastapi import APIRouter, File, UploadFile, HTTPException
from app.core.database import engine
from sqlalchemy import text
import os
import uuid

router = APIRouter()

@router.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}

# --- Minimal Image Upload API for 1GB RAM Server ---
# We save directly to the filesystem instead of MinIO to save RAM.
UPLOAD_DIR = "app/static/uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Generate random filename
        file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        file_name = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        
        # Save file
        with open(file_path, "wb") as buffer:
            # Read in chunks to avoid memory overflow on 1GB RAM
            while chunk := await file.read(1024 * 1024): # 1MB chunks
                buffer.write(chunk)
                
        # Return URL (assuming static files are mounted at /static)
        return {"url": f"/static/uploads/{file_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload: {str(e)}")
