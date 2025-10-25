import json
import hashlib
from typing import Optional, List
from tortoise.transactions import in_transaction
from src.models.proposal import LegislativeProposal, LegislativeProposalDenorm
from src.schemas.proposal import SerializedProposal
import structlog

logger = structlog.get_logger()


async def serialized_proposal(
    proposal_id: Optional[int] = None,
) -> Optional[SerializedProposal]:
    """
    Serialize a LegislativeProposal into structured JSON and persist it into
    LegislativeProposalDenorm.
    Only updates the record if the checksum (SHA256) changes.
    """
    async with in_transaction():
        if proposal_id:
            proposal = (
                await LegislativeProposal.filter(id=proposal_id)
                .prefetch_related(
                    "procedures__documents",
                    "consults",
                    "initiators__deputies",
                    "overview__categories",
                )
                .first()
            )
            if not proposal:
                raise Exception(f"No LegislativeProposal found with ID {proposal_id}.")
            proposals = [proposal]
        else:
            proposals = (
                await LegislativeProposal.filter(active=True)
                .prefetch_related(
                    "procedures__documents",
                    "consults",
                    "initiators__deputies",
                    "overview__categories",
                )
                .order_by("-updated_at")
            )

        for proposal in proposals:
            has_procedures = await proposal.procedures.all().count()
            has_consults = await proposal.consults.all().count()
            if not has_procedures or not has_consults:
                logger.info("skip_proposal_missing_data", proposal_id=proposal.id)
                continue

            initiators: List[dict] = [
                {
                    "id": initiator.id,
                    "name": initiator.name,
                    "position": initiator.position,
                    "party": initiator.party,
                    "is_main": initiator.is_main,
                    "photo_url": initiator.photo_url,
                    "deputy_id": [
                        deputy.id async for deputy in initiator.deputies.all()
                    ],
                }
                async for initiator in proposal.initiators.all()
            ]

            consults: List[dict] = [
                {
                    "id": consult.id,
                    "name": consult.name,
                    "link": consult.link,
                }
                async for consult in proposal.consults.all()
            ]

            procedures: List[dict] = []
            async for procedure in proposal.procedures.all().order_by("-date"):
                documents = [
                    {
                        "id": doc.id,
                        "name": doc.name,
                        "url": doc.link,
                    }
                    async for doc in procedure.documents.all()
                ]
                procedures.append(
                    {
                        "id": procedure.id,
                        "date": procedure.date.isoformat() if procedure.date else None,
                        "action": procedure.action,
                        "short_action": procedure.short_action,
                        "chamber": procedure.chamber,
                        "termen": procedure.termen.isoformat() if procedure.termen else None,
                        "attachment": documents,
                    }
                )

            latest_overview = (
                await proposal.overview.all().order_by("-created_at").first()
            )
            overview: dict = (
                {
                    "id": latest_overview.id,
                    "summary": latest_overview.summary,
                    "categories": [
                        cat.category_name
                        async for cat in latest_overview.categories.all()
                    ],
                }
                if latest_overview
                else {"id": 0, "summary": "", "categories": []}
            )

            oldest_procedure = await proposal.procedures.all().order_by("date").first()
            latest_procedure = await proposal.procedures.all().order_by("-date").first()

            created_at = (
                oldest_procedure.date.isoformat()
                if oldest_procedure
                else proposal.created_at.isoformat()
            )
            latest_action_date = (
                latest_procedure.date.isoformat() if latest_procedure else None
            )

            proposal_data: dict = {
                "proposal_id": proposal.id,
                "created_at": created_at,
                "updated_at": latest_action_date,
                "proposal": {
                    "title": proposal.title,
                    "idp": proposal.idp,
                    "senate_registration_number": proposal.senate_registration_number,
                    "first_senate_registration_number": proposal.first_senate_registration_number,
                    "cdep_registration_number": proposal.cdep_registration_number,
                    "government_registration_number": proposal.government_registration_number,
                    "first_chamber": proposal.first_chamber,
                    "initiative": proposal.initiative,
                    "opinion": proposal.opinion,
                    "urgent_procedure": proposal.urgent_procedure,
                    "status": proposal.status,
                    "status_cdep": proposal.status_cdep,
                    "status_senate": proposal.status_senate,
                    "law_character": proposal.law_character,
                    "deadline": proposal.deadline,
                    "year_issue": proposal.year_issue,
                    "active": proposal.active,
                    "published": proposal.published,
                    "senate_active": proposal.senate_active,
                    "cdep_active": proposal.cdep_active,
                    "promulgare": proposal.promulgare,
                    "matching_title": proposal.matching_title,
                },
                "initiators": initiators,
                "consults": consults,
                "overview": overview,
                "procedures": procedures,
            }

            # Compute checksum
            payload_json = json.dumps(proposal_data, sort_keys=True)
            checksum = hashlib.sha256(payload_json.encode()).hexdigest()

            denorm, created = await LegislativeProposalDenorm.get_or_create(
                proposal=proposal,
                defaults={
                    "payload": proposal_data,
                    "checksum": checksum,
                    "notified": False,
                },
            )

            if not created and denorm.checksum != checksum:
                denorm.payload = proposal_data
                denorm.checksum = checksum
                denorm.notified = False
                await denorm.save()
                logger.info("updated_denorm", proposal_id=proposal.id)
            elif created:
                logger.info("created_denorm", proposal_id=proposal.id)
            else:
                logger.info("no_change_detected", proposal_id=proposal.id)

            return proposal_data
