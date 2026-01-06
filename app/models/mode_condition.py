from typing import Optional, Any
from pydantic import BaseModel, Field




class ConditionBase(BaseModel):
    name: str = Field(..., max_length=128)
    description: Optional[str] = None
    criteria: Optional[dict[str, Any]] = None
    status: str = Field(default="active", description="active / inactive")


class ConditionCreate(ConditionBase):
    ...


class ConditionUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = None
    criteria: Optional[dict[str, Any]] = None
    status: Optional[str] = Field(None, description="active / inactive")


class ConditionOut(ConditionBase):
    id: int
    is_deleted: bool

    class Config:
        from_attributes = True