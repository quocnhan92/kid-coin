from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
import logging

from app.models.teen import TeenContract, ContractCheckin, ContractStatus, CheckinStatus
from app.models.teen import PersonalProject, ProjectMilestoneLog, ProjectStatus, MilestoneStatus
from app.models.user_family import User, Role
from app.models.notifications import Notification, NotificationType
from app.services import finance_service

logger = logging.getLogger(__name__)

def create_contract(db: Session, kid_id: UUID, family_id: UUID, data: dict):
    """Create a draft contract for a teen."""
    contract = TeenContract(
        kid_id=kid_id,
        family_id=family_id,
        title=data.get("title"),
        description=data.get("description"),
        period_type=data.get("period_type"),
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        salary_coins=data.get("salary_coins"),
        milestones=data.get("milestones"),
        status=ContractStatus.DRAFT
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract

def sign_contract(db: Session, contract_id: UUID, user_id: UUID):
    """Sign a contract. Changes status to ACTIVE if both sides sign logic (Simplified)"""
    contract = db.query(TeenContract).get(contract_id)
    if not contract:
        return None
        
    # Simplified logic: If both parent and kid sign, it becomes active.
    # For now, we'll just set it to ACTIVE on sign if called correctly.
    contract.status = ContractStatus.ACTIVE
    contract.signed_at = datetime.now()
    
    # Notify other party
    notif = Notification(
        user_id=contract.kid_id,
        type=NotificationType.SYSTEM,
        title="Hợp đồng kích hoạt! 📄",
        content=f"Hợp đồng '{contract.title}' đã chính thức có hiệu lực.",
        action_data={"contract_id": str(contract.id)}
    )
    db.add(notif)
    db.commit()
    return contract

def create_checkin(db: Session, contract_id: UUID, kid_id: UUID, note: str, proof_url: str):
    """Kid submits a check-in for a contract."""
    checkin = ContractCheckin(
        contract_id=contract_id,
        kid_id=kid_id,
        checkin_date=date.today(),
        note=note,
        proof_url=proof_url,
        status=CheckinStatus.PENDING
    )
    db.add(checkin)
    db.commit()
    return checkin

def create_project(db: Session, kid_id: UUID, family_id: UUID, data: dict):
    """Create a personal project for a teen."""
    project = PersonalProject(
        kid_id=kid_id,
        family_id=family_id,
        title=data.get("title"),
        description=data.get("description"),
        total_budget=data.get("total_budget"),
        milestones=data.get("milestones"), # [{"name": "Step 1", "reward": 500}, ...]
        status=ProjectStatus.ACTIVE
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def submit_milestone(db: Session, project_id: UUID, kid_id: UUID, milestone_idx: int, note: str, proof_url: str):
    """Submit proof for a project milestone."""
    project = db.query(PersonalProject).get(project_id)
    if not project or milestone_idx >= len(project.milestones):
        return None
        
    coins_reward = project.milestones[milestone_idx].get("reward", 0)
    
    log = ProjectMilestoneLog(
        project_id=project_id,
        milestone_index=milestone_idx,
        note=note,
        proof_url=proof_url,
        coins_released=coins_reward,
        status=MilestoneStatus.PENDING
    )
    db.add(log)
    db.commit()
    return log
