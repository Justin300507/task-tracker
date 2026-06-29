from fastapi import FastAPI

# Models
from app.models.projects import *  # noqa: F401
from app.models.users import *  # noqa: F401
from app.models.tasks import *  # noqa: F401
from app.models.task_tags import *  # noqa: F401
from app.models.tags import *  # noqa: F401
from app.models.collaborations import *  # noqa: F401

# DB
from app.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS (required for frontend access)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoint (required for deployment health checks)
@app.get("/health")
def health():
    return {"status": "ok"}

# Routers
from app.routes.stats_routes import stats_router
from app.routes.task_routes import task_router
from app.routes.project_routes import project_router
from app.routes.seed_routes import seed_router
from app.routes.tag_routes import tag_router
from app.routes.user_routes import user_router
from app.routes.collaboration_routes import collaboration_router
from app.routes.auth_routes import auth_router

app.include_router(stats_router)
app.include_router(task_router)
app.include_router(project_router)
app.include_router(seed_router)
app.include_router(tag_router)
app.include_router(user_router)
app.include_router(collaboration_router)
app.include_router(auth_router)
