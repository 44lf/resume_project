from typing import Optional, Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.db.models.selection import ScreeningCondition

router = APIRouter()


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


@router.post("/screening/conditions", response_model=ConditionOut)
async def create_condition(payload: ConditionCreate):
    condition = await ScreeningCondition.create(**payload.model_dump())
    return condition


@router.put("/screening/conditions/{condition_id}", response_model=ConditionOut)
async def update_condition(condition_id: int, payload: ConditionUpdate):
    condition = await ScreeningCondition.get_or_none(id=condition_id, is_deleted=False)
    if not condition:
        raise HTTPException(status_code=404, detail="筛选条件不存在")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(condition, field, value)
    await condition.save()
    return condition


@router.delete("/screening/conditions/{condition_id}")
async def delete_condition(condition_id: int):
    condition = await ScreeningCondition.get_or_none(id=condition_id, is_deleted=False)
    if not condition:
        raise HTTPException(status_code=404, detail="筛选条件不存在")
    condition.is_deleted = True
    condition.status = "inactive"
    await condition.save()
    return {"status": "deleted"}


class ConditionListOut(BaseModel):
    total: int
    items: list[ConditionOut]


@router.get("/screening/conditions", response_model=ConditionListOut)
async def list_conditions(
    status: Optional[str] = Query(None, description="过滤状态：active/inactive"),
    include_deleted: bool = Query(False, description="是否包含已删除"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    qs = ScreeningCondition.all()
    if status:
        qs = qs.filter(status=status)
    if not include_deleted:
        qs = qs.filter(is_deleted=False)

    total = await qs.count()
    records = await qs.order_by("-created_at").offset((page - 1) * page_size).limit(page_size)
    return {
        "total": total,
        "items": records,
    }
