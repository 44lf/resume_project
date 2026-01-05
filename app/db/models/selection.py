from tortoise import fields, models


class ScreeningCondition(models.Model):
    """
    人才筛选条件（支持多状态、多条件组合）。
    """

    id = fields.BigIntField(pk=True)
    name = fields.CharField(max_length=128)
    description = fields.TextField(null=True)

    # 规则配置（JSON），示例：
    # {
    #   "name_keywords": ["张三"],
    #   "schools": ["清华"],
    #   "majors": ["计算机"],
    #   "degrees": ["本科", "硕士"],
    #   "grad_year_min": 2018,
    #   "grad_year_max": 2025
    # }
    criteria = fields.JSONField(null=True)

    status = fields.CharField(max_length=16, default="active")  # active / inactive
    is_deleted = fields.BooleanField(default=False)  # 逻辑删除

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "screening_conditions"
        indexes = [
            ("status", "is_deleted"),
            ("created_at",),
        ]
