from tortoise import fields
from tortoise.models import Model


class Deputy(Model):
    id = fields.IntField(pk=True)
    idm = fields.IntField(null=True)
    name = fields.CharField(max_length=255, null=True)
    normalized_name = fields.CharField(max_length=255, null=True, index=True)
    group = fields.CharField(max_length=255, null=True)
    legislature = fields.CharField(max_length=255, null=True)
    circumscription = fields.CharField(max_length=255, null=True)
    profile_link = fields.CharField(max_length=500, null=True)
    member_from = fields.DateField(null=True)
    member_until = fields.DateField(null=True)
    profile = fields.JSONField(null=True)
    search_vector = fields.TextField(null=True)
    
    assigned_committees = fields.ManyToManyField(
        "models.CdePCommittee", related_name="assigned_deputies", blank=True
    )

    committee_membership = fields.ManyToManyField(
        "models.CdePCommittee",
        related_name="deputies_ctte_membership",
        through="committeemembership",  # lowercase class name by default
        blank=True
    )

    active = fields.BooleanField(default=True)
    chamber = fields.CharField(max_length=255, null=True)
    bio = fields.TextField(null=True)
    standing_bureau = fields.CharField(max_length=255, null=True)
    birthday = fields.DateField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "deputies_list"