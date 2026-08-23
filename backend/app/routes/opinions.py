from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Opinion
from ..schemas import OpinionCreate, OpinionResponse, StatusUpdate
from ..auth import get_current_user, RoleChecker
from ..services.retrieval_service import RetrievalService
from ..services.risk_service import RiskService

router = APIRouter(prefix="/opinions", tags=["Legal Opinions"])

@router.post("/draft", response_model=OpinionResponse)
async def draft_opinion(opinion_in: OpinionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    chunks = await RetrievalService.search_relevant_chunks(db, opinion_in.title + " " + opinion_in.draft_content[:200], current_user, limit=5)
    context_str = "\n".join(f"[Doc: {c['filename']}] {c['content']}" for c in chunks)
    
    report = await RiskService.analyze_legal_risks(opinion_in.draft_content, context_str)
    
    opinion = Opinion(
        title=opinion_in.title,
        draft_content=opinion_in.draft_content,
        compliance_report=report,
        status="Draft",
        created_by=current_user.id
    )
    db.add(opinion)
    db.commit()
    db.refresh(opinion)
    return opinion

@router.get("/list", response_model=list[OpinionResponse])
def list_opinions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "Legal_Officer":
        return db.query(Opinion).filter(Opinion.created_by == current_user.id).all()
    return db.query(Opinion).all()

@router.put("/{opinion_id}/status", response_model=OpinionResponse)
def update_opinion_status(
    opinion_id: int, 
    status_update: StatusUpdate, 
    db: Session = Depends(get_db),     current_user: User = Depends(RoleChecker("Senior_Advisor"))
):
    opinion = db.query(Opinion).filter(Opinion.id == opinion_id).first()
    if not opinion:
        raise HTTPException(status_code=404, detail="Opinion not found.")
        
    if status_update.status not in ["Draft", "Under_Review", "Approved", "Rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status level.")
        
    opinion.status = status_update.status
    opinion.reviewed_by = current_user.id
    db.commit()
    db.refresh(opinion)
    return opinion