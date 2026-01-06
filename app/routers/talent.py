from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Query

from app.services.talent_service import screening_to_talent_with_skills
from app.db.models.talent import Talent
from app.db.models.skill import Skill
from app.db.models.talent_skill import TalentSkill
from app.models.model_talent import TalentCreateFromScreening, TalentOut, TalentListOut, GraphResponse

router = APIRouter()



@router.post("/talents/from-screening", response_model=TalentOut)
async def create_from_screening(payload: TalentCreateFromScreening):
    talent = await screening_to_talent_with_skills(
        screening_id=payload.screening_id, skill_names=payload.skill_names
    )
    return talent


@router.get("/talents", response_model=TalentListOut)
async def list_talents(
    name: Optional[str] = Query(None),
    school: Optional[str] = Query(None),
    major: Optional[str] = Query(None),
    degree: Optional[str] = Query(None),
    grad_year_min: Optional[int] = Query(None),
    grad_year_max: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    qs = Talent.all()
    if name:
        qs = qs.filter(name__icontains=name)
    if school:
        qs = qs.filter(school__icontains=school)
    if major:
        qs = qs.filter(major__icontains=major)
    if degree:
        qs = qs.filter(degree__icontains=degree)
    if grad_year_min is not None:
        qs = qs.filter(grad_year__gte=grad_year_min)
    if grad_year_max is not None:
        qs = qs.filter(grad_year__lte=grad_year_max)

    total = await qs.count()
    items = await qs.order_by("-at_time").offset((page - 1) * page_size).limit(page_size)
    return {"total": total, "items": items}




@router.get("/talents/graph", response_model=GraphResponse)
async def get_knowledge_graph():
    nodes: list[Dict[str, Any]] = []
    edges: list[Dict[str, Any]] = []

    talents = await Talent.all()
    skills = await Skill.all()
    talent_skills = await TalentSkill.all()

    for t in talents:
        nodes.append({"id": f"talent-{t.id}", "label": t.name or "未命名", "type": "talent"})
    for s in skills:
        nodes.append({"id": f"skill-{s.id}", "label": s.name, "type": "skill"})

    for ts in talent_skills:
        edges.append(
            {
                "source": f"talent-{ts.talent_id}",
                "target": f"skill-{ts.skill_id}",
                "label": "has_skill",
            }
        )

    return {"nodes": nodes, "edges": edges}
