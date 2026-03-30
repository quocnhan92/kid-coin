from fastapi import APIRouter, Depends, HTTPException, Header, Response, Request
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user_family import User, Family, Role
from app.models.devices import FamilyDevice
from app.schemas import auth as auth_schemas
from app.services.audit import AuditService, AuditStatus
from uuid import UUID
from app.core.security import create_access_token

router = APIRouter()

# --- Helpers ---
def get_device_info(db: Session, device_id: str):
    return db.query(FamilyDevice).filter(
        FamilyDevice.device_token == device_id,
        FamilyDevice.is_active == True
    ).first()

# --- Endpoints ---

@router.get("/device-status", response_model=auth_schemas.DeviceContextResponse)
async def check_device_status(
    x_device_id: str = Header(..., alias="X-Device-ID"),
    db: Session = Depends(deps.get_db)
):
    """
    Kiểm tra trạng thái thiết bị.
    """
    device = get_device_info(db, x_device_id)
    
    if not device:
        return {"is_registered": False, "members": []}

    # Nếu đã đăng ký, lấy danh sách thành viên gia đình
    users = db.query(User).filter(User.family_id == device.family_id).all()
    
    members = []
    for user in users:
        members.append({
            "id": user.id,
            "display_name": user.display_name,
            "avatar_url": user.avatar_url,
            "role": user.role,
            "has_pin": bool(user.family.parent_pin) if user.role == Role.PARENT else False
        })
    
    return {
        "is_registered": True,
        "family_name": device.family.name,
        "members": members
    }

@router.post("/register-device", response_model=auth_schemas.DeviceContextResponse)
async def register_device(
    request: Request,
    payload: auth_schemas.DeviceLoginRequest,
    db: Session = Depends(deps.get_db)
):
    """
    Đăng nhập thiết bị mới vào nhà ĐÃ CÓ (Kiểm tra username và pin của nhà).
    """
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "Unknown")
    device_info = {"raw": user_agent}

    parent = db.query(User).filter(
        User.username == payload.username,
        User.role == Role.PARENT
    ).first()

    if not parent:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản quản trị này.")
    
    if parent.family.parent_pin != payload.password:
        raise HTTPException(status_code=401, detail="Mật khẩu hoặc tên tài khoản không đúng.")

    # Tạo hoặc cập nhật Device để "nhớ" thiết bị này
    existing_device = db.query(FamilyDevice).filter(FamilyDevice.device_token == payload.device_id).first()
    if existing_device:
        existing_device.is_active = True
        existing_device.family_id = parent.family_id
        existing_device.device_name = payload.device_name
        existing_device.user_agent = user_agent
        existing_device.device_info = device_info
    else:
        new_device = FamilyDevice(
            family_id=parent.family_id,
            device_name=payload.device_name,
            device_token=payload.device_id,
            initial_ip_address=client_ip,
            user_agent=user_agent,
            device_info=device_info,
            is_active=True
        )
        db.add(new_device)

    db.commit()
    
    AuditService.log(
        db=db,
        action="LOGIN_DEVICE",
        resource_type="FamilyDevice",
        user_id=str(parent.id),
        status=AuditStatus.SUCCESS,
        ip_address=client_ip,
        user_agent=user_agent,
        device_info=device_info,
        details={"device_name": payload.device_name}
    )

    return await check_device_status(x_device_id=payload.device_id, db=db)

@router.post("/register-family", response_model=auth_schemas.DeviceContextResponse)
async def register_family(
    request: Request,
    payload: auth_schemas.FamilyRegistrationRequest,
    db: Session = Depends(deps.get_db)
):
    """
    Tạo NHÀ MỚI (Family) và đăng ký thiết bị lần đầu.
    """
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "Unknown")
    device_info = {"raw": user_agent}

    existing_user = db.query(User).filter(User.username == payload.admin_username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Tên đăng nhập này đã được sử dụng. Vui lòng chọn tên khác.")

    from uuid import uuid4
    new_family = Family(id=uuid4(), name=payload.family_name, parent_pin=payload.admin_password)
    db.add(new_family)
    db.flush()

    parent = User(
        id=uuid4(),
        family_id=new_family.id,
        role=Role.PARENT,
        display_name=payload.admin_display_name,
        username=payload.admin_username,
        avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={payload.admin_username}"
    )
    db.add(parent)
    db.flush()

    new_device = FamilyDevice(
        family_id=new_family.id,
        device_name=payload.device_name,
        device_token=payload.device_id,
        initial_ip_address=client_ip,
        user_agent=user_agent,
        device_info=device_info,
        is_active=True
    )
    db.add(new_device)

    db.commit()
    
    AuditService.log(
        db=db,
        action="REGISTER_FAMILY",
        resource_type="Family",
        user_id=str(parent.id),
        status=AuditStatus.SUCCESS,
        ip_address=client_ip,
        user_agent=user_agent,
        device_info=device_info,
        details={"family_name": payload.family_name}
    )

    return await check_device_status(x_device_id=payload.device_id, db=db)

@router.post("/quick-login")
async def quick_login(
    request: Request,
    payload: auth_schemas.QuickLoginRequest,
    response: Response,
    db: Session = Depends(deps.get_db)
):
    """
    Đăng nhập nhanh bằng cách chọn Avatar.
    """
    # Get Context Info
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "Unknown")
    device_info = {"raw": user_agent}

    # 1. Kiểm tra Device hợp lệ
    device = get_device_info(db, payload.device_id)
    if not device:
        raise HTTPException(status_code=403, detail="Thiết bị chưa được đăng ký.")

    # 2. Lấy User
    user = db.query(User).filter(User.id == payload.user_id, User.family_id == device.family_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại trong gia đình này.")

    # 3. Logic xác thực
    if user.role == Role.PARENT:
        if not payload.pin or payload.pin != user.family.parent_pin:
             AuditService.log(
                db=db,
                action="LOGIN_FAILED",
                resource_type="User",
                user_id=str(user.id),
                status=AuditStatus.FAILED,
                ip_address=client_ip,
                user_agent=user_agent,
                device_info=device_info,
                details={"reason": "Wrong PIN"}
             )
             raise HTTPException(status_code=401, detail="Mã PIN không đúng!")

    # 4. Login Success - ISSUE JWT TOKEN
    access_token = create_access_token(subject=str(user.id))
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=30*24*60*60)
    
    # Audit
    AuditService.log(
        db=db,
        action="LOGIN_QUICK",
        resource_type="User",
        user_id=str(user.id),
        status=AuditStatus.SUCCESS,
        ip_address=client_ip,
        user_agent=user_agent,
        device_info=device_info,
        details={"device": device.device_name}
    )

    redirect_url = "/parent" if user.role == Role.PARENT else "/kid"

    return {
        "message": f"Chào mừng {user.display_name}!",
        "role": user.role.value,
        "redirect_url": redirect_url
    }

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Đã đăng xuất"}
