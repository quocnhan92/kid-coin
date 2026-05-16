from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user_family import User, Role


def require_kid(current_user: User = Depends(deps.get_current_user)) -> User:
    if current_user.role != Role.KID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hãy chọn tài khoản bé trên màn hình đăng nhập để bắt đầu chơi",
        )
    return current_user


def require_parent(current_user: User = Depends(deps.get_current_user)) -> User:
    if current_user.role != Role.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Parent play endpoints require PARENT role",
        )
    return current_user


def require_parent_child_access(
    child_id: UUID,
    parent: User = Depends(require_parent),
    db: Session = Depends(deps.get_db),
) -> User:
    child = db.query(User).filter(User.id == child_id).first()
    if not child or child.family_id != parent.family_id or child.role != Role.KID:
        raise HTTPException(status_code=404, detail="Child not found in your family")
    return child
