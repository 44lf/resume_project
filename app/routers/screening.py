from fastapi import APIRouter, UploadFile, File, Query
from tortoise.expressions import Q
from app.services.screening_service import upload_and_parse_pdf
from app.db.models.screening import ScreeningResume
from app.models.model_screening import ScreeningListOut
from typing import Optional

router = APIRouter()




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
