from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.users import Users
from app.models.projects import Project
from app.models.tasks import Task
from app.models.tags import Tag
from app.models.task_tags import TaskTag

seed_router = APIRouter()

@seed_router.post("/seed", summary="Populate the database with demo data")
def seed(db: Session = Depends(get_db)):
    # ------------------- Users -------------------
    user_data = [
        {"email": "alex.chen@example.com", "username": "alexchen", "password": "Password123", "display_name": "Alex Chen"},
        {"email": "maria.garcia@example.com", "username": "mariagarcia", "password": "Password123", "display_name": "Maria Garcia"},
        {"email": "james.kim@example.com", "username": "jameskim", "password": "Password123", "display_name": "James Kim"},
        {"email": "sara.lee@example.com", "username": "saralee", "password": "Password123", "display_name": "Sara Lee"},
        {"email": "david.patel@example.com", "username": "davidpatel", "password": "Password123", "display_name": "David Patel"},
    ]
    for data in user_data:
        try:
            existing = db.query(Users).filter(Users.email == data["email"]).first()
            if existing:
                continue
            user = Users(**data)
            db.add(user)
            db.flush()
        except IntegrityError:
            db.rollback()
            continue

    # ------------------- Projects -------------------
    project_data = [
        {"name": "Alpha Launch", "description": "Launch the Alpha product line", "owner_id": 1},
        {"name": "Beta Revamp", "description": "Revamp the Beta platform", "owner_id": 2},
        {"name": "Gamma Expansion", "description": "Expand Gamma into new markets", "owner_id": 3},
        {"name": "Delta Migration", "description": "Migrate services to Delta cloud", "owner_id": 4},
        {"name": "Epsilon Research", "description": "Research new AI techniques", "owner_id": 5},
    ]
    for data in project_data:
        try:
            existing = db.query(Project).filter(Project.name == data["name"]).first()
            if existing:
                continue
            project = Project(**data)
            db.add(project)
            db.flush()
        except IntegrityError:
            db.rollback()
            continue

    # ------------------- Tags -------------------
    tag_names = ["Urgent", "Backend", "Frontend", "Design", "Testing"]
    for name in tag_names:
        try:
            existing = db.query(Tag).filter(Tag.name == name).first()
            if existing:
                continue
            tag = Tag(name=name)
            db.add(tag)
            db.flush()
        except IntegrityError:
            db.rollback()
            continue

    # ------------------- Tasks -------------------
    task_data = [
        {"title": "Launch Q3 campaign", "description": "Prepare marketing assets for Q3", "status": "In Progress", "project_id": 1},
        {"title": "Fix login bug", "description": "Resolve authentication issue", "status": "Done", "project_id": 2},
        {"title": "Design new UI", "description": "Create mockups for the new dashboard", "status": "Open", "project_id": 3},
        {"title": "Write unit tests", "description": "Increase coverage to 90%", "status": "Open", "project_id": 4},
        {"title": "Deploy to production", "description": "Run migration scripts and deploy", "status": "Planned", "project_id": 5},
    ]
    for data in task_data:
        try:
            existing = db.query(Task).filter(Task.title == data["title"]).first()
            if existing:
                continue
            task = Task(**data)
            db.add(task)
            db.flush()
        except IntegrityError:
            db.rollback()
            continue

    # ------------------- TaskTag (many‑to‑many) -------------------
    # Simple deterministic linking: first task gets first two tags, etc.
    for task in db.query(Task).all():
        tag_ids = [tag.id for tag in db.query(Tag).limit(2).all()]
        for tag_id in tag_ids:
            try:
                existing = (
                    db.query(TaskTag)
                    .filter(TaskTag.task_id == task.id, TaskTag.tag_id == tag_id)
                    .first()
                )
                if existing:
                    continue
                link = TaskTag(task_id=task.id, tag_id=tag_id)
                db.add(link)
                db.flush()
            except IntegrityError:
                db.rollback()
                continue

    db.commit()
    return {"status": "seeded"}
