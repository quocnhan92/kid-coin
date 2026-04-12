from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.api import deps
from app.models.user_family import User, Role
from app.models.teen import TeenContract, ContractStatus, PersonalProject, ProjectStatus
from app.schemas.teen import TeenContractResponse, TeenContractCreate, ContractCheckinRequest
from app.schemas.teen import PersonalProjectResponse, PersonalProjectCreate, MilestoneSubmitRequest
from app.services import teen_service

router = APIRouter()

# --- Teen Contracts ---
@router.get("/contracts", response_model=List[TeenContractResponse])
async def list_my_contracts(
    current_user: User = Depends(deps.require_role(Role.KID)),
    db: Session = Depends(deps.get_db)
):
    """List all contracts for current teen."""
    if not current_user.is_teen_mode:
        raise HTTPException(status_code=403, detail="Teen mode is NOT active for this account.")
    return db.query(TeenContract).filter(TeenContract.kid_id == current_user.id).all()

@router.post("/contracts", response_model=TeenContractResponse)
async def draft_contract(
    request: TeenContractCreate,
    current_user: User = Depends(deps.require_role(Role.KID)),
    db: Session = Depends(deps.get_db)
):
    """Draft a new contract for the parent to review/sign."""
    if not current_user.is_teen_mode:
        raise HTTPException(status_code=403, detail="Teen mode is NOT active for this account.")
    return teen_service.create_contract(db, current_user.id, current_user.family_id, request.dict())

@router.post("/contracts/{contract_id}/sign")
async def sign_contract(
    contract_id: UUID,
    current_user: User = Depends(deps.require_role(Role.KID)),
    db: Session = Depends(deps.get_db)
):
    """Kid signs the contract to activate it."""
    contract = db.query(TeenContract).get(contract_id)
    if not contract or contract.kid_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contract not found")
        
    result = teen_service.sign_contract(db, contract_id, current_user.id)
    return {"status": "success", "contract_status": result.status}

@router.post("/contracts/{contract_id}/checkin")
async def contract_checkin(
    contract_id: UUID,
    request: ContractCheckinRequest,
    current_user: User = Depends(deps.require_role(Role.KID)),
    db: Session = Depends(deps.get_db)
):
    """Kid submits a daily check-in for a contract."""
    contract = db.query(TeenContract).get(contract_id)
    if not contract or contract.kid_id != current_user.id or contract.status != ContractStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Active contract not found")
        
    checkin = teen_service.create_checkin(db, contract_id, current_user.id, request.note, request.proof_url)
    return {"status": "success", "checkin_id": checkin.id}

# --- Personal Projects ---
@router.get("/projects", response_model=List[PersonalProjectResponse])
async def list_my_projects(
    current_user: User = Depends(deps.require_role(Role.KID)),
    db: Session = Depends(deps.get_db)
):
    """List all personal projects for current teen."""
    if not current_user.is_teen_mode:
        raise HTTPException(status_code=403, detail="Teen mode is NOT active.")
    return db.query(PersonalProject).filter(PersonalProject.kid_id == current_user.id).all()

@router.post("/projects/{project_id}/milestones/{milestone_idx}/submit")
async def submit_project_milestone(
    project_id: UUID,
    milestone_idx: int,
    request: MilestoneSubmitRequest,
    current_user: User = Depends(deps.require_role(Role.KID)),
    db: Session = Depends(deps.get_db)
):
    """Submit proof for a project milestone."""
    project = db.query(PersonalProject).get(project_id)
    if not project or project.kid_id != current_user.id or project.status != ProjectStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Active project not found")
        
    result = teen_service.submit_milestone(
        db, project_id, current_user.id, milestone_idx, request.note, request.proof_url
    )
    if not result:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return {"status": "success", "log_id": result.id}
