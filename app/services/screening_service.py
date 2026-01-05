# app/services/screening_service.py

import uuid
from fastapi import UploadFile

from app.services.minio_service import upload_file
from app.services.pdf_service import parse_pdf
from app.services.llm_service import extract_resume_info
from app.db.models.screening import ScreeningResume

RESUME_BUCKET = "resumes"


async def upload_and_parse_pdf(file: UploadFile) -> ScreeningResume:
    content = await file.read()

    object_key = f"{uuid.uuid4()}.pdf"
    await upload_file(
        bucket=RESUME_BUCKET,
        object_key=object_key,
        content=content,
        content_type="application/pdf",
    )

    text, _ = parse_pdf(pdf_bytes=content)
    llm_result = await extract_resume_info(text)

    screening = await ScreeningResume.create(
        file_object_key=f"{RESUME_BUCKET}/{object_key}",
        extracted_name=llm_result.get("name"),
        extracted_school=llm_result.get("school"),
        extracted_major=llm_result.get("major"),
        extracted_degree=llm_result.get("degree"),
        extracted_grad_year=llm_result.get("grad_year"),
        extracted_phone=llm_result.get("phone"),
        extracted_email=llm_result.get("email"),
        is_screened=False,
    )
    return screening
