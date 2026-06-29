from fastapi import APIRouter, Depends, HTTPException, Query, Path, status, Response
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models.tags import Tag
from app.utils.auth import get_current_user
from app.schemas.tag import TagCreate, TagUpdate, TagRead

# Router
tag_router = APIRouter()

@tag_router.get("/tags", response_model=dict)
def list_tags(
    search: Optional[str] = Query(None, description="Search term for tag name"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Tag)
    if search:
        query = query.filter(Tag.name.ilike(f"%{search}%"))
    total = query.count()
    items: List[Tag] = query.offset(offset).limit(limit).all()
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }

@tag_router.get("/tags/{tag_id}", response_model=TagRead)
def get_tag(
    tag_id: int = Path(..., description="Tag ID"),
    db: Session = Depends(get_db),
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Not found")
    return tag

@tag_router.post("/tags", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag_in: TagCreate,
    db: Session = Depends(get_db),
    current_user: "User" = Depends(get_current_user),
):
    tag = Tag(name=tag_in.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

@tag_router.put("/tags/{tag_id}", response_model=TagRead)
def update_tag(
    tag_in: TagUpdate,
    tag_id: int = Path(..., description="Tag ID"),
    db: Session = Depends(get_db),
    current_user: "User" = Depends(get_current_user),
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Not found")
    if tag_in.name is not None:
        tag.name = tag_in.name
    db.commit()
    db.refresh(tag)
    return tag

@tag_router.delete("/tags/{tag_id}")
def delete_tag(
    tag_id: int = Path(..., description="Tag ID"),
    db: Session = Depends(get_db),
    current_user: "User" = Depends(get_current_user),
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(tag)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
