from tortoise import models, fields


class TalentSkill(models.Model):
    id = fields.BigIntField(pk=True)

    # 人才编号
    talent_id = fields.BigIntField()

    # 技能编号
    skill_id = fields.BigIntField()

    # 入库时间
    at_time = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "talent_skills"
        unique_together = (("talent_id", "skill_id"),)
        indexes = [
            ("talent_id",),
            ("skill_id",),
        ]
