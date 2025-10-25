from tortoise import fields
from tortoise.models import Model

from src.models import CustomUser

class PolicyCategory(Model):
    id = fields.IntField(pk=True)
    category_name = fields.CharField(max_length=255, unique=True, index=True)

    followed_by: fields.ReverseRelation["CustomUser"]

    class Meta:
        table = "pdf_analyzer_policycategory"

    def __str__(self):
        return self.category_name