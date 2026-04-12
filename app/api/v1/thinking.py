from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.api import deps
from app.models.user_family import User, Role
from app.models.thinking import TaskBid, ProblemBoard, ProblemSolution, WeeklyReflection, BidStatus, ProblemStatus, SolutionStatus, ReflectionStatus
from app.schemas.thinking import (
    TaskBidCreate, TaskBidResponse, 
    ProblemBoardResponse, SolutionSubmitRequest,
    WeeklyReflectionResponse, WeeklyReflectionSubmit
)
from app.services import audit

router = APIRouter()

# --- Task Bidding ---
@router.post("/bids", response_model=TaskBidResponse)
async def create_bid(
    request: TaskBidCreate,
    current_user: User = Depends(deps.require_role(Role.KID)),
    db: Session = Depends(deps.get_db)
):
    """Kid proposes a task bid."""
    bid = TaskBid(
        kid_id=current_user.id,
        family_id=current_user.family_id,
        title=request.title,
        description=request.description,
        proposed_coins=request.proposed_coins,
        status=BidStatus.PENDING
    )
    db.add(bid)
    db.commit()
    db.refresh(bid)
    return bid

@router.get("/bids", response_model=List[TaskBidResponse])
async def list_my_bids(
    current_user: User = Depends(deps.require_role(Role.KID)),
    db: Session = Depends(deps.get_db)
):
    """List bids proposed by the kid."""
    return db.query(TaskBid).filter(TaskBid.kid_id == current_user.id).all()

# --- Problem Board ---
@router.get("/problems", response_model=List[ProblemBoardResponse])
async def list_open_problems(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """List open individual or family problems."""
    return db.query(ProblemBoard).filter(
        ProblemBoard.family_id == current_user.family_id,
        ProblemBoard.status == ProblemStatus.OPEN
    ).all()

@router.post("/problems/{problem_id}/solutions")
async def submit_solution(
    problem_id: UUID,
    request: SolutionSubmitRequest,
    current_user: User = Depends(deps.require_role(Role.KID)),
    db: Session = Depends(deps.get_db)
):
    """Kid submits a solution to a problem."""
    # Check if problem exists and is open
    problem = db.query(ProblemBoard).get(problem_id)
    if not problem or problem.status != ProblemStatus.OPEN:
        raise HTTPException(status_code=404, detail="Problem not found or closed")
    
    # Check if already submitted
    existing = db.query(ProblemSolution).filter(
        ProblemSolution.board_id == problem_id,
        ProblemSolution.kid_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bạn đã gửi lời giải cho bài toán này rồi.")

    solution = ProblemSolution(
        board_id=problem_id,
        kid_id=current_user.id,
        task_description=request.task_description,
        proof_image_url=request.proof_image_url,
        status=SolutionStatus.DONE
    )
    db.add(solution)
    db.commit()
    return {"status": "success", "message": "Lời giải đã được gửi đi!"}

# --- Weekly Reflection ---
@router.get("/reflections/me", response_model=List[WeeklyReflectionResponse])
async def get_my_reflections(
    current_user: User = Depends(deps.require_role(Role.KID)),
    db: Session = Depends(deps.get_db)
):
    """Get weekly reflections for the kid."""
    return db.query(WeeklyReflection).filter(WeeklyReflection.kid_id == current_user.id).all()

@router.put("/reflections/{reflection_id}/submit")
async def submit_reflection(
    reflection_id: UUID,
    request: WeeklyReflectionSubmit,
    current_user: User = Depends(deps.require_role(Role.KID)),
    db: Session = Depends(deps.get_db)
):
    """Kid submits answers to a weekly reflection."""
    reflection = db.query(WeeklyReflection).filter(
        WeeklyReflection.id == reflection_id,
        WeeklyReflection.kid_id == current_user.id
    ).first()
    
    if not reflection:
        raise HTTPException(status_code=404, detail="Reflection entry not found")
    
    if reflection.status != ReflectionStatus.PENDING:
        raise HTTPException(status_code=400, detail="Reflection already submitted or processed")
        
    reflection.q1_answer = request.q1_answer
    reflection.q2_answer = request.q2_answer
    reflection.q3_answer = request.q3_answer
    reflection.status = ReflectionStatus.SUBMITTED
    reflection.submitted_at = datetime.now()
    
    db.commit()
    return {"status": "success", "message": "Cảm ơn bạn đã hoàn thành bài nhìn lại tuần qua!"}
