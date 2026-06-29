from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class TagCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)


class TagUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = Field(default=None, min_length=1)


class TagResponse(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TagRead(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
