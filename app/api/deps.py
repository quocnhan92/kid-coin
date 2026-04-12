from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user_family import User, Role, Family
from app.core import context
from uuid import UUID
from app.core.security import decode_access_token

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_token_from_request(request: Request, cookie_name: str = "access_token") -> str:
    # 1. Try to get token from Cookie
    token = request.cookies.get(cookie_name)
    
    # 2. If no cookie, check for "Authorization" header (Bearer token)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    return token

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = get_token_from_request(request, "access_token")
    user = None
    if token:
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            user_id = payload["sub"]
            # Check if it's a user token (starts with UUID)
            try:
                UUID(user_id)
                user = db.query(User).filter(User.id == user_id).first()
            except ValueError:
                pass

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    # Set context
    context.set_current_user_id(str(user.id))
    return user

def get_current_admin(request: Request, db: Session = Depends(get_db)) -> str:
    token = get_token_from_request(request, "admin_token")
    if token:
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            subject = payload["sub"]
            if subject.startswith("admin:"):
                return subject # Return 'admin:<id>'
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin access required",
    )

def require_role(role: Role):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have the required role: {role.value}"
            )
        return current_user
    return role_checker
