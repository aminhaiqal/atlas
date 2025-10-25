from typing import TYPE_CHECKING
from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:
    from src.models.category import PolicyCategory
    
class CustomUser(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    secondary_email = fields.CharField(max_length=255, null=True)
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)
    company = fields.CharField(max_length=50, null=True)
    profile_picture = fields.CharField(max_length=500, null=True)
    preferred_timezone = fields.CharField(max_length=50, default='Europe/Bucharest')

    # Role and permission fields
    is_superuser = fields.BooleanField(default=False)
    is_company_admin = fields.BooleanField(default=False)
    is_company_member = fields.BooleanField(default=True)
    
    # Security and tracking fields
    password_changed_at = fields.DatetimeField(null=True)

    # Followed entities
    followed_categories: fields.ManyToManyRelation["PolicyCategory"] = fields.ManyToManyField(
        "models.PolicyCategory", 
        related_name="followed_by",
        through="authentication_customuser_followed_categories",
        forward_key="policycategory_id",
        backward_key="customuser_id"
    )
    followed_deputies = fields.JSONField(null=True)
    followed_executiveStk = fields.JSONField(null=True)
    notificationPreferences = fields.JSONField(default=dict)
    pptx_folder = fields.CharField(max_length=50, null=True)

    class Meta:
        table = "authentication_customuser"

    @property
    def full_name(self) -> str:
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"
