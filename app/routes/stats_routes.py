from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.projects import Project
from app.models.tasks import Task

stats_router = APIRouter()

@stats_router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_projects = db.query(func.count(Project.id)).scalar() or 0
    total_tasks = db.query(func.count(Task.id)).scalar() or 0
    upcoming_tasks = (
        db.query(func.count(Task.id))
        .filter(Task.due_date > func.now())
        .scalar()
    ) or 0
    completed_tasks = (
        db.query(func.count(Task.id))
        .filter(Task.status == "Done")
        .scalar()
    ) or 0
    return {
        "total_projects": total_projects,
        "total_tasks": total_tasks,
        "upcoming_tasks": upcoming_tasks,
        "completed_tasks": completed_tasks,
    }
