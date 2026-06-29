from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.inspection import inspect

from app.database import get_db
from app.models.tasks import Task
from app.models.task_tags import TaskTag
from app.models.tags import Tag
from app.schemas.task import TaskCreate
from app.utils.auth import get_current_user

# Router variable must be named exactly "task_router"
task_router = APIRouter()


def _task_to_dict(task: Task) -> dict:
    """Convert a SQLAlchemy Task instance to a plain dict, excluding internal attributes."""
    return {c.key: getattr(task, c.key) for c in inspect(task).mapper.column_attrs}


@task_router.get("/tasks")
def list_tasks(
    search: Optional[str] = Query(None, description="Search in title or description"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    tag_id: Optional[int] = Query(None, description="Filter by tag ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Task)

    if search:
        query = query.filter(
            or_(Task.title.ilike(f"%{search}%"), Task.description.ilike(f"%{search}%"))
        )
    if project_id is not None:
        query = query.filter(Task.project_id == project_id)
    if status is not None:
        query = query.filter(Task.status == status)
    if tag_id is not None:
        # Join through the association table to filter by tag
        query = query.join(TaskTag).filter(TaskTag.tag_id == tag_id)

    total = query.count()
    tasks = query.offset(offset).limit(limit).all()
    items = [_task_to_dict(t) for t in tasks]
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@task_router.get("/tasks/{task_id}")
def get_task(
    task_id: int = Path(..., description="The ID of the task to retrieve"),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Not found")
    return _task_to_dict(task)


@task_router.post("/tasks", status_code=201)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: "User" = Depends(get_current_user),
):
    # Build the Task instance. Assume the Task model has a ``user_id`` column.
    task = Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        due_date=task_in.due_date,
        user_id=getattr(current_user, "id", None),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_to_dict(task)


@task_router.put("/tasks/{task_id}")
def update_task(
    task_in: TaskCreate,
    task_id: int = Path(..., description="The ID of the task to update"),
    db: Session = Depends(get_db),
    current_user: "User" = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Not found")
    # Update mutable fields
    task.title = task_in.title
    task.description = task_in.description
    task.status = task_in.status
    task.due_date = task_in.due_date
    # Ownership check - optional but recommended
    if getattr(task, "user_id", None) != getattr(current_user, "id", None):
        raise HTTPException(status_code=403, detail="Forbidden")
    db.commit()
    db.refresh(task)
    return _task_to_dict(task)


@task_router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int = Path(..., description="The ID of the task to delete"),
    db: Session = Depends(get_db),
    current_user: "User" = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Not found")
    # Ownership check - optional but recommended
    if getattr(task, "user_id", None) != getattr(current_user, "id", None):
        raise HTTPException(status_code=403, detail="Forbidden")
    db.delete(task)
    db.commit()
    return Response(status_code=204)
