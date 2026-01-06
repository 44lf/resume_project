from typing import Optional,Dict, Any
from pydantic import BaseModel



class TalentCreateFromScreening(BaseModel):
    screening_id: int
    skill_names: Optional[list[str]] = None


class TalentOut(BaseModel):
    id: int
    name: Optional[str]
    gender: Optional[str]
    school: Optional[str]
    major: Optional[str]
    degree: Optional[str]
    grad_year: Optional[int]
    phone: Optional[str]
    email: Optional[str]
    resume_object_key: str
    source_screening_id: Optional[int]

    class Config:
        from_attributes = True


class TalentListOut(BaseModel):
    total: int
    items: list[TalentOut]


class GraphResponse(BaseModel):
    nodes: list[Dict[str, Any]]
    edges: list[Dict[str, Any]]