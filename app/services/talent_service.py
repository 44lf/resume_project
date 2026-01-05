from tortoise.transactions import in_transaction
from typing import Optional
from app.db.models.screening import ScreeningResume
from app.db.models.talent import Talent
from app.db.models.skill import Skill
from app.db.models.talent_skill import TalentSkill

async def screening_to_talent_with_skills(
    screening_id: int,
    skill_names: Optional[list[str]] = None,
) -> Talent:
    async with in_transaction():
        # 1. 查筛查池记录
        screening = await ScreeningResume.get_or_none(id=screening_id)
        if not screening:
            raise ValueError('筛查记录不存在')
        # 2. 防止重复入库
        exists = await Talent.filter(
            source_screening_id=screening.id
        ).exists()
        if exists:
            raise ValueError("该筛查记录已入库")

        skills_from_screening = screening.extracted_skills or []
        skill_names = skill_names if skill_names is not None else skills_from_screening

        # 3. 写入人才表
        talent = await Talent.create(
            name=screening.extracted_name,
            school=screening.extracted_school,
            major=screening.extracted_major,
            degree=screening.extracted_degree,
            grad_year=screening.extracted_grad_year,
            phone=screening.extracted_phone,
            email=screening.extracted_email,
            resume_object_key=screening.file_object_key,
            source_screening_id=screening.id,
        )
        for name in skill_names:
            name = name.strip()
            if not name:
                continue
            skill, _ = await Skill.get_or_create(name=name)
            await TalentSkill.get_or_create(
                talent_id=talent.id,
                skill_id=skill.id,
            )


        # 4. 标记筛查池为已筛选
        screening.is_screened = True
        await screening.save()

        return talent

