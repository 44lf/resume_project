from typing import Optional
from fastapi import APIRouter, UploadFile, File, Query
from pydantic import BaseModel
from app.services.screening_service import upload_and_parse_pdf, list_screening_resumes

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
    """
    上传简历PDF文件并解析
    
    Args:
        file: 上传的PDF文件
        
    Returns:
        screening_id: 创建的简历记录ID
        status: 上传状态
    """
    # 验证文件类型
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只支持PDF格式文件")
    
    screening = await upload_and_parse_pdf(file)
    return {
        "screening_id": screening.id,
        "status": "uploaded",
    }