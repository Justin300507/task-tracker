from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.collaboration import Collaboration
from app.models.project import Project
from app.models.users import Users
from app.schemas.collaboration import CollaborationCreate, CollaborationUpdate, CollaborationResponse

collaboration_router = APIRouter()

@collaboration_router.get(
    "/collaborations",
    response_model=dict
)
def list_collaborations(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    project_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Collaboration)
    if project_id is not None:
        query = query.filter(Collaboration.project_id == project_id)
    if user_id is not None:
        query = query.filter(Collaboration.user_id == user_id)
    total = query.count()
    items = (
        query.offset(offset)
        .limit(limit)
        .all()
    )
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }

@collaboration_router.get(
    "/collaborations/{collaboration_id}",
    response_model=CollaborationResponse
)
def get_collaboration(
    collaboration_id: int = Path(...),
    db: Session = Depends(get_db)
):
    collab = db.query(Collaboration).filter(Collaboration.id == collaboration_id).first()
    if not collab:
        raise HTTPException(status_code=404, detail="Not found")
    return collab

@collaboration_router.post(
    "/collaborations",
    response_model=CollaborationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_collaboration(
    collab_in: CollaborationCreate,
    db: Session = Depends(get_db)
):
    # verify project exists
    project = db.query(Project).filter(Project.id == collab_in.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # verify user exists
    user = db.query(Users).filter(Users.id == collab_in.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    collab = Collaboration(
        project_id=collab_in.project_id,
        user_id=collab_in.user_id,
        role=collab_in.role,
        status=collab_in.status,
    )
    db.add(collab)
    db.commit()
    db.refresh(collab)
    return collab

@collaboration_router.put(
    "/collaborations/{collaboration_id}",
    response_model=CollaborationResponse
)
def update_collaboration(
    collab_update: CollaborationUpdate,
    collaboration_id: int = Path(...),
    db: Session = Depends(get_db)
):
    collab = db.query(Collaboration).filter(Collaboration.id == collaboration_id).first()
    if not collab:
        raise HTTPException(status_code=404, detail="Not found")
    if collab_update.role is not None:
        collab.role = collab_update.role
    if collab_update.status is not None:
        collab.status = collab_update.status
    db.commit()
    db.refresh(collab)
    return collab

@collaboration_router.delete(
    "/collaborations/{collaboration_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_collaboration(
    collaboration_id: int = Path(...),
    db: Session = Depends(get_db)
):
    collab = db.query(Collaboration).filter(Collaboration.id == collaboration_id).first()
    if not collab:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(collab)
    db.commit()
    return