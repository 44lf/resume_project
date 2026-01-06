from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from tortoise.expressions import Q
from app.services.screening_service import upload_and_parse_pdf
from app.db.models.screening import ScreeningResume
from app.models.model_screening import ScreeningListOut
from typing import Optional
from enum import Enum

router = APIRouter()


# ============ 枚举定义 ============
class DegreeEnum(str, Enum):
    """学位枚举"""
    BACHELOR = "本科"
    MASTER = "硕士"
    DOCTOR = "博士"
    OTHER = "其他"


class ScreeningStatusEnum(str, Enum):
    """筛选状态枚举"""
    PENDING = "pending"      # 待筛选
    PASSED = "passed"        # 已通过
    REJECTED = "rejected"    # 已拒绝


# ============ 路由端点 ============
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
        "filename": file.filename,
    }


@router.get("/screening/resumes", response_model=ScreeningListOut)
async def list_screening_resumes(
    name: Optional[str] = Query(None, description="姓名（模糊搜索）"),
    school: Optional[str] = Query(None, description="学校（模糊搜索）"),
    major: Optional[str] = Query(None, description="专业（模糊搜索）"),
    degree: Optional[DegreeEnum] = Query(None, description="学位"),
    screening_status: Optional[ScreeningStatusEnum] = Query(None, description="筛选状态"),
    matched_condition_id: Optional[int] = Query(None, description="匹配的筛选条件ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
):
    """
    获取简历筛选列表
    
    支持多条件过滤和分页查询
    
    Args:
        name: 按姓名模糊搜索
        school: 按学校模糊搜索
        major: 按专业模糊搜索
        degree: 按学位精确筛选（枚举）
        screening_status: 按筛选状态精确筛选（枚举）
        matched_condition_id: 按匹配的筛选条件ID筛选
        page: 页码（从1开始）
        page_size: 每页条数（1-100）
        
    Returns:
        total: 符合条件的总记录数
        items: 当前页的简历列表
    """
    qs = ScreeningResume.all()
    
    # 字符串字段：模糊搜索
    if name:
        qs = qs.filter(extracted_name__icontains=name)
    if school:
        qs = qs.filter(extracted_school__icontains=school)
    if major:
        qs = qs.filter(extracted_major__icontains=major)
    
    # 枚举字段：精确匹配（自动转换为枚举的 value）
    if degree:
        qs = qs.filter(extracted_degree=degree.value)
    
    if screening_status:
        qs = qs.filter(screening_status=screening_status.value)
    
    # 数组字段：包含查询
    if matched_condition_id is not None:
        qs = qs.filter(
            Q(matched_condition_ids__contains=str(matched_condition_id)) | 
            Q(matched_condition_ids__contains=matched_condition_id)
        )

    # 统计总数
    total = await qs.count()
    
    # 分页查询
    items = await qs.order_by("-at_time")\
                    .offset((page - 1) * page_size)\
                    .limit(page_size)
    
    return {"total": total, "items": items}


@router.get("/screening/resumes/{resume_id}")
async def get_resume_detail(resume_id: int):
    """
    获取单个简历详情
    
    Args:
        resume_id: 简历ID
        
    Returns:
        简历完整信息
    """
    resume = await ScreeningResume.get_or_none(id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    return resume


@router.patch("/screening/resumes/{resume_id}/status")
async def update_resume_status(
    resume_id: int,
    status: ScreeningStatusEnum
):
    """
    更新简历筛选状态
    
    Args:
        resume_id: 简历ID
        status: 新的筛选状态（枚举）
        
    Returns:
        updated: 是否更新成功
        new_status: 新的状态值
    """
    resume = await ScreeningResume.get_or_none(id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    resume.screening_status = status.value
    resume.is_screened = True  # 标记为已筛选
    await resume.save()
    
    return {
        "updated": True,
        "resume_id": resume_id,
        "new_status": status.value
    }


@router.delete("/screening/resumes/{resume_id}")
async def delete_resume(resume_id: int):
    """
    删除简历记录
    
    Args:
        resume_id: 简历ID
        
    Returns:
        deleted: 是否删除成功
    """
    resume = await ScreeningResume.get_or_none(id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    await resume.delete()
    
    return {
        "deleted": True,
        "resume_id": resume_id
    }


@router.get("/screening/stats")
async def get_screening_stats():
    """
    获取简历筛选统计信息
    
    Returns:
        total: 总简历数
        pending: 待筛选数
        passed: 已通过数
        rejected: 已拒绝数
        by_degree: 按学位统计
    """
    total = await ScreeningResume.all().count()
    pending = await ScreeningResume.filter(screening_status=ScreeningStatusEnum.PENDING.value).count()
    passed = await ScreeningResume.filter(screening_status=ScreeningStatusEnum.PASSED.value).count()
    rejected = await ScreeningResume.filter(screening_status=ScreeningStatusEnum.REJECTED.value).count()
    
    # 按学位统计
    by_degree = {}
    for degree in DegreeEnum:
        count = await ScreeningResume.filter(extracted_degree=degree.value).count()
        by_degree[degree.value] = count
    
    return {
        "total": total,
        "pending": pending,
        "passed": passed,
        "rejected": rejected,
        "by_degree": by_degree
    }