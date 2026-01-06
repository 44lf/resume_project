from typing import Optional
from pydantic import BaseModel
from typing import Optional, Dict, Any

class ScreeningOut(BaseModel):
    id: int
    file_object_key: str
    extracted_name: Optional[str]
    extracted_school: Optional[str]
    extracted_major: Optional[str]
    extracted_degree: Optional[str]
    extracted_grad_year: Optional[int]
    extracted_phone: Optional[str]
    extracted_email: Optional[str]
    extracted_skills: list[str] | None
    image_object_keys: list[str] | None
    is_screened: bool
    matched_condition_ids: list[int] | None

    class Config:
        from_attributes = True


class ScreeningListOut(BaseModel):
    total: int
    items: list[ScreeningOut]


class GraphResponse(BaseModel):
    nodes: list[Dict[str, Any]]
    edges: list[Dict[str, Any]]