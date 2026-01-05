from fastapi import APIRouter,UploadFile,File
from app.services.screening_service import upload_and_parse_pdf

router = APIRouter()
@router.post("/screening/upload")
async def upload_screening_pdf(file: UploadFile = File(...)):
    screening = await upload_and_parse_pdf(file)
    return {
        "screening_id": screening.id,
        "status": "uploaded",
    }