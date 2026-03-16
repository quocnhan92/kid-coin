from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user_family import User, Role, Family
from app.core import context
from uuid import UUID

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    # 1. Try to get user_id from Cookie
    user_id = request.cookies.get("user_id")
    
    # 2. If no cookie, check for "Authorization" header (Bearer token) - simplified for now
    if not user_id:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            user_id = auth_header.split(" ")[1]

    user = None
    if user_id:
        try:
            # Validate UUID format
            UUID(user_id)
            user = db.query(User).filter(User.id == user_id).first()
        except ValueError:
            pass # Invalid UUID

    # 3. If still no user, Auto-Seed/Fallback (ONLY FOR DEV)
    if not user:
        # Check if we have any users, if not, seed them
        if db.query(User).count() == 0:
             from uuid import uuid4
             # Create Family
             family = Family(id=uuid4(), name="Nhà Cà Rốt", parent_pin="1234")
             db.add(family)
             db.flush()
             
             # Create Parent
             parent = User(id=uuid4(), family_id=family.id, role=Role.PARENT, display_name="Bố Tuấn", username="botuan")
             db.add(parent)
             
             # Create Kids
             kid1 = User(id=uuid4(), family_id=family.id, role=Role.KID, display_name="Bé Bin", avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=Bin")
             kid2 = User(id=uuid4(), family_id=family.id, role=Role.KID, display_name="Em Na", avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=Na")
             db.add(kid1)
             db.add(kid2)
             
             db.commit()
             # Return the parent by default if nothing set
             user = parent
        else:
             # Just return the first parent found
             user = db.query(User).filter(User.role == Role.PARENT).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    # Set context
    context.set_current_user_id(str(user.id))
    return user

def require_role(role: Role):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have the required role: {role.value}"
            )
        return current_user
    return role_checker
