from tortoise import models, fields


class ScreeningResume(models.Model):
    id = fields.BigIntField(pk=True)

    # 简历原文件（MinIO）
    file_object_key = fields.CharField(max_length=512)

    # 抽取出的关键信息（从简历里提取）
    extracted_name = fields.CharField(max_length=64, null=True)
    extracted_school = fields.CharField(max_length=255, null=True)
    extracted_major = fields.CharField(max_length=255, null=True)
    extracted_degree = fields.CharField(max_length=64, null=True)
    extracted_grad_year = fields.IntField(null=True)
    extracted_phone = fields.CharField(max_length=32, null=True)
    extracted_email = fields.CharField(max_length=128, null=True)
    extracted_skills = fields.JSONField(null=True)
    # 简历中拆分出的图片（MinIO 对象键列表）
    image_object_keys = fields.JSONField(null=True)

    # 状态：未筛选 / 已筛选
    is_screened = fields.BooleanField(default=False)

    # 命中的筛选条件 id 列表
    matched_condition_ids = fields.JSONField(null=True)

    # 入库时间
    at_time = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "screening_resumes"
        indexes = [
            ("is_screened", "at_time"),
            ("extracted_name",),
            ("extracted_school",),
            ("extracted_major",),
        ]
