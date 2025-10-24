from tortoise.models import Model
from tortoise import fields

from src.models.timestamp import TimeStampedMixin

class LegislativeProposal(Model, TimeStampedMixin):
    id = fields.IntField(pk=True)
    title = fields.TextField()
    normalized_title = fields.CharField(max_length=2044, null=True, index=True)
    idp = fields.IntField(null=True, unique=True)
    senate_registration_number = fields.CharField(max_length=50, null=True)
    first_senate_registration_number = fields.CharField(max_length=50, null=True)
    cdep_registration_number = fields.CharField(max_length=50, null=True)
    government_registration_number = fields.CharField(max_length=50, null=True)
    first_chamber = fields.CharField(max_length=50)
    initiative = fields.CharField(max_length=255)
    opinion = fields.CharField(max_length=20, null=True)
    urgent_procedure = fields.CharField(max_length=3, null=True)
    status = fields.TextField(null=True)
    status_cdep = fields.TextField(null=True)
    status_senate = fields.TextField(null=True)
    law_character = fields.CharField(max_length=20, null=True)
    deadline = fields.TextField(null=True)
    year_issue = fields.IntField(null=True)
    active = fields.BooleanField(default=True)
    published = fields.BooleanField(default=False)
    senate_active = fields.BooleanField(default=True)
    cdep_active = fields.BooleanField(default=True)
    promulgare = fields.CharField(max_length=50, default="nu")
    matching_title = fields.TextField(null=True)
    latest_procedure_date = fields.DateField(null=True)
    oldest_procedure_date = fields.DateField(null=True)
    
    report_cttee = fields.ManyToManyField(
        "models.CdePCommittee",
        related_name="reporting_proposals",
        through="legislative_proposal_report_cttee",
        forward_key="cdepcommittee_id",
        backward_key="legislativeproposal_id"
    )

    class Meta:
        table = "legislative_proposal"
        
class LegislativeInitiator(Model, TimeStampedMixin):
    id = fields.IntField(pk=True)
    legislative_proposal = fields.ForeignKeyField(
        "models.LegislativeProposal",
        related_name="initiators",
    )
    name = fields.CharField(max_length=255, null=True)
    position = fields.CharField(max_length=255, null=True)
    party = fields.CharField(max_length=255, null=True)
    is_main = fields.BooleanField(default=False)
    deputies = fields.ManyToManyField(
        "models.Deputy",
        related_name="legislative_initiators",
        through="scrape_legislative_legislativeinitiator_deputies",
        forward_key="deputy_id",
        backward_key="legislativeinitiator_id",
    )
    
    class Meta:
        table = "scrape_legislative_legislativeinitiator"

class LegislativeConsult(Model, TimeStampedMixin):
    id = fields.IntField(pk=True)
    legislative_proposal = fields.ForeignKeyField(
        "models.LegislativeProposal",
        related_name="consults",
    )
    name = fields.TextField()
    link = fields.CharField(max_length=500, null=True)
    s3_link = fields.CharField(max_length=500, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "scrape_legislative_legislativeconsult"

class LegislativeSummary(Model, TimeStampedMixin):
    id = fields.IntField(pk=True)
    legislative_proposal = fields.ForeignKeyField(
        "models.LegislativeProposal",
        related_name="overview",
        on_delete=fields.CASCADE
    )
    summary = fields.TextField(null=True)
    categories = fields.ManyToManyField(
        "models.PolicyCategory",
        related_name="summaries",
        through="scrape_legislative_legislativesummary_categories",
        forward_key="policycategory_id",
        backward_key="legislativesummary_id",
    )

    class Meta:
        table = "scrape_legislative_legislativesummary"

class LegislativeProcedure(Model, TimeStampedMixin):
    id = fields.IntField(pk=True)
    legislative_proposal = fields.ForeignKeyField(
        "models.LegislativeProposal",
        related_name="procedures",
    )
    date = fields.DateField(null=True)
    action = fields.TextField()
    chamber = fields.CharField(max_length=10)
    termen = fields.DateField(null=True)
    short_action = fields.TextField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "scrape_legislative_legislativeprocedure"
    
class ProcedureDocument(Model, TimeStampedMixin):
    id = fields.IntField(pk=True)
    legislative_procedure = fields.ForeignKeyField(
        "models.LegislativeProcedure",
        related_name="documents",
        on_delete=fields.CASCADE,
    )
    name = fields.CharField(max_length=255, null=True)
    link = fields.CharField(max_length=500, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "scrape_legislative_proceduredocument"