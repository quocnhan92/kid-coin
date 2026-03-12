from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user_family import User, Role
from app.core import context

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Placeholder for a real authentication system (e.g., JWT)
def get_current_user(db: Session = Depends(get_db)) -> User:
    # For now, we'll simulate getting a user. In a real app, this would
    # decode a JWT token from the request header.
    # Let's assume we have a header 'X-User-ID' for simulation.
    # In a real app, you would get this from the token.
    
    # SIMULATION: Let's hardcode a PARENT user for testing management APIs
    # and a KID user for testing quest submission.
    # We can switch between them for testing.
    
    # user_id = "a_hardcoded_parent_uuid" # Replace with a real UUID from your DB
    user_id = "a_hardcoded_kid_uuid" # Replace with a real UUID from your DB
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        # In a real app, you'd create some seed users.
        # For now, let's create them if they don't exist.
        from uuid import uuid4
        
        # Create a family first
        family = db.query(Family).first()
        if not family:
            family = Family(id=uuid4(), name="Test Family", parent_pin="hashed_pin")
            db.add(family)
            db.commit()
            db.refresh(family)

        # Create a parent and a kid
        parent_user = User(id="a_hardcoded_parent_uuid", family_id=family.id, role=Role.PARENT, display_name="Test Parent")
        kid_user = User(id="a_hardcoded_kid_uuid", family_id=family.id, role=Role.KID, display_name="Test Kid")
        
        db.add(parent_user)
        db.add(kid_user)
        db.commit()
        
        user = kid_user # Default to kid for this run

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Set user_id in context for audit logs
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
