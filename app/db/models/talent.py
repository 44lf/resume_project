from tortoise import models, fields


class Talent(models.Model):
    id = fields.BigIntField(pk=True)                 # 编号

    name = fields.CharField(max_length=64)           # 姓名
    gender = fields.CharField(max_length=8, null=True)  # 性别

    school = fields.CharField(max_length=255, null=True)  # 学校
    major = fields.CharField(max_length=255, null=True)   # 专业
    degree = fields.CharField(max_length=64, null=True)   # 学位
    grad_year = fields.IntField(null=True)                # 毕业时间（年）

    phone = fields.CharField(max_length=32, null=True)    # 手机
    email = fields.CharField(max_length=128, null=True)   # 邮箱

    resume_object_key = fields.CharField(max_length=512)  # 简历来源（MinIO）

    at_time = fields.DatetimeField(auto_now_add=True)     # 加入时间

    class Meta:
        table = "talents"
