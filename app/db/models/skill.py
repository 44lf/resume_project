from tortoise import models, fields


class Skill(models.Model):
    id = fields.BigIntField(pk=True)

    # 技能名称
    name = fields.CharField(max_length=128, unique=True)

    # 入库时间
    at_time = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "skills"
        indexes = [
            ("name",),
        ]
