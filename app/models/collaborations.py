from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey, func
from app.database import Base

class Collaborations(Base):
    __tablename__ = "collaborations"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum("owner", "editor", "viewer", name="collaboration_role"), nullable=False)
    invited_at = Column(DateTime, server_default=func.now(), nullable=False)
    accepted_at = Column(DateTime, nullable=True)

