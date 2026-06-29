from fastapi import APIRouter, Depends, Query, Path, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models.projects import Project
from app.models.users import Users
from app.schemas.project import ProjectCreate
from app.utils.auth import get_current_user

# OAuth2 scheme (required for token generation elsewhere)
# Not used directly in this file but kept for completeness
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

project_router = APIRouter()


def _to_dict(obj) -> dict:
    """Convert a SQLAlchemy model instance to a plain dict, stripping the SA state."""
    data = dict(obj.__dict__)
    data.pop("_sa_instance_state", None)
    return data


@project_router.get("/projects")
def list_projects(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None, description="Search by title"),
    owner_id: Optional[int] = Query(None, description="Filter by owner id"),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """List projects with optional search and owner filtering, paginated."""
    query = db.query(Project)
    if search:
        query = query.filter(Project.title.ilike(f"%{search}%"))
    if owner_id is not None:
        query = query.filter(Project.owner_id == owner_id)

    total = query.count()
    projects = query.offset(offset).limit(limit).all()
    items = [_to_dict(p) for p in projects]
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@project_router.get("/projects/{project_id}")
def get_project(
    project_id: int = Path(..., description="The ID of the project to retrieve"),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return _to_dict(project)


@project_router.post("/projects", status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    # If owner_id is omitted, assign the current user as owner
    owner_id = project_in.owner_id if project_in.owner_id is not None else current_user.id
    new_project = Project(
        name=project_in.title, description=project_in.description, owner_id=owner_id, )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return _to_dict(new_project)


@project_router.put("/projects/{project_id}")
def update_project(
    project_in: ProjectCreate,
    project_id: int = Path(..., description="The ID of the project to update"),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project.title = project_in.title
    project.description = project_in.description
    if project_in.owner_id is not None:
        project.owner_id = project_in.owner_id
    db.commit()
    db.refresh(project)
    return _to_dict(project)


@project_router.delete("/projects/{project_id}")
def delete_project(
    project_id: int = Path(..., description="The ID of the project to delete"),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
