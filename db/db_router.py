from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from .db_manager import DatabaseManager

router = APIRouter(prefix="/summaries", tags=["summaries"])

# Pydantic models for request and response
class SummaryCreate(BaseModel):
    title: str
    content: str
    subject: Optional[str] = None

class SummaryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    subject: Optional[str] = None

class SummaryResponse(BaseModel):
    id: int
    title: str
    content: str
    subject: Optional[str] = None

    class Config:
        orm_mode = True

# Dependency to get database manager
def get_db():
    db = DatabaseManager()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=int, status_code=201)
def create_summary(summary: SummaryCreate, db: DatabaseManager = Depends(get_db)):
    """Create a new summary"""
    return db.add_summary(title=summary.title, content=summary.content, subject=summary.subject)

@router.get("/{summary_id}", response_model=SummaryResponse)
def get_summary(summary_id: int, db: DatabaseManager = Depends(get_db)):
    """Get a summary by ID"""
    summary = db.get_summary(summary_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary

@router.get("/", response_model=List[SummaryResponse])
def get_all_summaries(db: DatabaseManager = Depends(get_db)):
    """Get all summaries"""
    return db.get_all_summaries()

@router.get("/subject/{subject}", response_model=List[SummaryResponse])
def get_summaries_by_subject(subject: str, db: DatabaseManager = Depends(get_db)):
    """Get summaries by subject"""
    return db.get_summaries_by_subject(subject)

@router.get("/title/{title}", response_model=List[SummaryResponse])
def get_summaries_by_title(title: str, db: DatabaseManager = Depends(get_db)):
    """Get summaries by title"""
    return db.get_summaries_by_title(title)

@router.put("/{summary_id}", response_model=bool)
def update_summary(summary_id: int, summary: SummaryUpdate, db: DatabaseManager = Depends(get_db)):
    """Update a summary"""
    result = db.update_summary(
        summary_id=summary_id,
        title=summary.title,
        content=summary.content,
        subject=summary.subject
    )
    if not result:
        raise HTTPException(status_code=404, detail="Summary not found")
    return result

@router.delete("/{summary_id}", response_model=bool)
def delete_summary(summary_id: int, db: DatabaseManager = Depends(get_db)):
    """Delete a summary"""
    result = db.delete_summary(summary_id)
    if not result:
        raise HTTPException(status_code=404, detail="Summary not found")
    return result



    