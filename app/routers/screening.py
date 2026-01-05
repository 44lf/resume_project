from typing import Optional
from fastapi import APIRouter, UploadFile, File, Query
from pydantic import BaseModel
from tortoise.expressions import Q
from app.services.screening_service import upload_and_parse_pdf
from app.db.models.screening import ScreeningResume

router = APIRouter()


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


@router.post("/screening/upload")
async def upload_screening_pdf(file: UploadFile = File(...)):
    screening = await upload_and_parse_pdf(file)
    return {
        "screening_id": screening.id,
        "status": "uploaded",
    }


@router.get("/screening/resumes", response_model=ScreeningListOut)
async def list_screening_resumes(
    name: Optional[str] = Query(None),
    school: Optional[str] = Query(None),
    major: Optional[str] = Query(None),
    degree: Optional[str] = Query(None),
    is_screened: Optional[bool] = Query(None),
    matched_condition_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    qs = ScreeningResume.all()
    if name:
        qs = qs.filter(extracted_name__icontains=name)
    if school:
        qs = qs.filter(extracted_school__icontains=school)
    if major:
        qs = qs.filter(extracted_major__icontains=major)
    if degree:
        qs = qs.filter(extracted_degree__icontains=degree)
    if is_screened is not None:
        qs = qs.filter(is_screened=is_screened)
    if matched_condition_id is not None:
        qs = qs.filter(Q(matched_condition_ids__contains=str(matched_condition_id)) | Q(matched_condition_ids__contains=matched_condition_id))

    total = await qs.count()
    items = await qs.order_by("-at_time").offset((page - 1) * page_size).limit(page_size)
    return {"total": total, "items": items}
