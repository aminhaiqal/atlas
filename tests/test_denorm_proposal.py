import pytest
import asyncio
from tortoise import Tortoise
from src.models import (
    LegislativeProposal,
    LegislativeConsult,
    LegislativeProcedure,
    ProcedureDocument,
    LegislativeProposalDenorm,
)
from src.tasks.denorm_proposal import serialized_proposal


# --- Initialize Tortoise synchronously at import ---
async def init_db():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["src.models"]})
    await Tortoise.generate_schemas()


# Run the async init before any tests
asyncio.run(init_db())


# --- Helper fixture to clean DB before each test ---
@pytest.fixture(autouse=True)
async def clean_db():
    await LegislativeProposalDenorm.all().delete()
    await LegislativeProposal.all().delete()
    yield


# --- Your tests ---
@pytest.mark.asyncio
async def test_create_denorm():
    proposal = await LegislativeProposal.create(
        title="Test Proposal",
        first_chamber="CDEP",
        initiative="Government",
        active=True,
        published=True,
        senate_active=True,
        cdep_active=True,
        promulgare="N/A",
    )
    await LegislativeConsult.create(
        legislative_proposal=proposal,
        proposal=proposal,
        name="Test Consult",
        link="https://example.com",
    )
    procedure = await LegislativeProcedure.create(
        legislative_proposal=proposal,
        proposal=proposal,
        date="2025-01-01",
        action="Initial Action",
        short_action="Init",
        chamber="CDEP",
    )
    await ProcedureDocument.create(
        legislative_procedure=procedure,
        procedure=procedure,
        name="Doc 1",
        link="https://example.com/doc1",
    )

    data = await serialized_proposal(proposal.id)
    denorm = await LegislativeProposalDenorm.get(proposal=proposal)

    assert denorm.payload["proposal_id"] == proposal.id
    assert denorm.notified is False
    assert data["proposal"]["title"] == "Test Proposal"


@pytest.mark.asyncio
async def test_update_denorm_checksum():
    proposal = await LegislativeProposal.get(title="Test Proposal")
    denorm = await LegislativeProposalDenorm.get(proposal=proposal)

    proposal.initiative = "Parliament"
    await proposal.save()

    updated_data = await serialized_proposal(proposal.id)
    updated_denorm = await LegislativeProposalDenorm.get(proposal=proposal)

    assert updated_denorm.checksum != denorm.checksum
    assert updated_denorm.notified is False


@pytest.mark.asyncio
async def test_no_change_denorm():
    proposal = await LegislativeProposal.get(title="Test Proposal")
    denorm_before = await LegislativeProposalDenorm.get(proposal=proposal)

    await serialized_proposal(proposal.id)
    denorm_after = await LegislativeProposalDenorm.get(proposal=proposal)

    assert denorm_before.checksum == denorm_after.checksum
