# app/services/screening_service.py

import uuid
from fastapi import UploadFile
from typing import List, Dict, Any

from app.services.minio_service import upload_file
from app.services.pdf_service import parse_pdf
from app.services.llm_service import extract_resume_info
from app.db.models.screening import ScreeningResume
from app.db.models.selection import ScreeningCondition

RESUME_BUCKET = "resumes"
RESUME_IMAGE_BUCKET = "resume-images"


async def upload_and_parse_pdf(file: UploadFile) -> ScreeningResume:
    content = await file.read()

    object_key = f"{uuid.uuid4()}.pdf"
    await upload_file(
        bucket=RESUME_BUCKET,
        object_key=object_key,
        content=content,
        content_type="application/pdf",
    )

    text, images = parse_pdf(pdf_bytes=content)
    image_object_keys: list[str] = []
    for idx, img_bytes in enumerate(images):
        image_key = f"{uuid.uuid4()}_{idx}.png"
        await upload_file(
            bucket=RESUME_IMAGE_BUCKET,
            object_key=image_key,
            content=img_bytes,
            content_type="image/png",
        )
        image_object_keys.append(f"{RESUME_IMAGE_BUCKET}/{image_key}")

    llm_result = await extract_resume_info(text)

    matched_condition_ids = await _match_conditions(llm_result)

    screening = await ScreeningResume.create(
        file_object_key=f"{RESUME_BUCKET}/{object_key}",
        extracted_name=llm_result.get("name"),
        extracted_school=llm_result.get("school"),
        extracted_major=llm_result.get("major"),
        extracted_degree=llm_result.get("degree"),
        extracted_grad_year=llm_result.get("grad_year"),
        extracted_phone=llm_result.get("phone"),
        extracted_email=llm_result.get("email"),
        extracted_skills=llm_result.get("skills") or [],
        image_object_keys=image_object_keys,
        matched_condition_ids=matched_condition_ids or [],
        is_screened=False,
    )
    return screening


def _match_text(value: str | None, keywords: List[str] | None) -> bool:
    if not keywords:
        return True
    if not value:
        return False
    return any(k.lower() in value.lower() for k in keywords if k)


def _match_condition(result: Dict[str, Any], condition: ScreeningCondition) -> bool:
    criteria = condition.criteria or {}
    if not criteria:
        return True

    if not _match_text(result.get("name"), criteria.get("name_keywords")):
        return False
    if criteria.get("schools") and (result.get("school") not in criteria["schools"]):
        return False
    if criteria.get("majors") and (result.get("major") not in criteria["majors"]):
        return False
    if criteria.get("degrees") and (result.get("degree") not in criteria["degrees"]):
        return False

    gy = result.get("grad_year")
    min_year = criteria.get("grad_year_min")
    max_year = criteria.get("grad_year_max")
    if min_year is not None and gy is not None and gy < min_year:
        return False
    if max_year is not None and gy is not None and gy > max_year:
        return False

    return True


async def _match_conditions(result: Dict[str, Any]) -> list[int]:
    conditions = await ScreeningCondition.filter(
        status="active", is_deleted=False
    ).all()
    matched: list[int] = []
    for c in conditions:
        if _match_condition(result, c):
            matched.append(c.id)
    return matched
