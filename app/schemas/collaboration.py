from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CollaborationCreate(BaseModel):
    project_id: int = Field(..., ge=1)
    user_id: int = Field(..., ge=1)
    role: str = Field(min_length=1)
    invitation_message: Optional[str] = None


class CollaborationUpdate(BaseModel):
    role: Optional[str] = None
    status: Optional[str] = None


class CollaborationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: Optional[int] = None
    user_id: Optional[int] = None
    role: Optional[str] = None
    status: Optional[str] = None
