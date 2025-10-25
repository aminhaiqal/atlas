from tortoise.models import Model
from tortoise import fields

class CdePCommittee(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    committeeId = fields.CharField(max_length=255, unique=True)
    url = fields.CharField(max_length=2083, null=True)  # URLs stored as CharField
    chamber = fields.CharField(max_length=2, null=True)
    type = fields.CharField(max_length=255, null=True)
    legislature = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "parliament_committees"

class CommitteeMembership(Model):
    id = fields.IntField(pk=True)
    deputy = fields.ForeignKeyField('models.Deputy', related_name='committee_memberships', on_delete=fields.CASCADE)
    committee = fields.ForeignKeyField('models.CdePCommittee', related_name='memberships', on_delete=fields.CASCADE)
    position = fields.CharField(max_length=255)

    class Meta:
        table = "stakeholder_management_committeemembership"
