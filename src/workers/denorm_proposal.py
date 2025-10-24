from typing import Optional, List, Dict, Any
from tortoise.expressions import Q
from tortoise.transactions import in_transaction
from src.models import (
    LegislativeProposal,
)
from src.schemas import (
    SerializedProposal,
    ProposalDetails,
    ProposalInitiator,
    ProposalConsult,
    ProposalProcedure,
    ProposalDocument,
    ProposalOverview,
)
import structlog

logger = structlog.get_logger()
CACHE_TTL = 60 * 60 * 24  # 1 day

# Assuming Valkey (Redis) client is async
from src.utils.cache import json_cache


async def serialized_proposal(proposal_id: Optional[int] = None) -> Optional[SerializedProposal]:
    """
    Serialize a LegislativeProposal (single or multiple) into a structured format,
    cache the result, and return.
    """
    async with in_transaction():
        if proposal_id:
            proposal = await LegislativeProposal.filter(id=proposal_id).prefetch_related(
                "procedures__documents",
                "consults",
                "initiators__deputies",
                "overview__categories",
            ).first()
            if not proposal:
                raise Exception(f"No LegislativeProposal found with ID {proposal_id}.")
            proposals = [proposal]
        else:
            proposals = await LegislativeProposal.filter(active=True).prefetch_related(
                "procedures__documents",
                "consults",
                "initiators__deputies",
                "overview__categories",
            ).order_by("-updated_at")

        for proposal in proposals:
            # Skip proposals without procedures and consults
            has_procedures = await proposal.procedures.all().count()
            has_consults = await proposal.consults.all().count()
            if not has_procedures or not has_consults:
                continue

            initiators: List[ProposalInitiator] = [
                {
                    "id": initiator.id,
                    "name": initiator.name,
                    "position": initiator.position,
                    "party": initiator.party,
                    "is_main": initiator.is_main,
                    "photo_url": initiator.photo_url,
                    "deputy_id": [deputy.id async for deputy in initiator.deputies.all()],
                }
                async for initiator in proposal.initiators.all()
            ]

            consults: List[ProposalConsult] = [
                {
                    "id": consult.id,
                    "name": consult.name,
                    "link": consult.link,
                }
                async for consult in proposal.consults.all()
            ]

            procedures: List[ProposalProcedure] = []
            async for procedure in proposal.procedures.all().order_by("-date"):
                documents = [
                    ProposalDocument(
                        id=doc.id,
                        name=doc.name,
                        url=doc.link,
                    )
                    async for doc in procedure.documents.all()
                ]
                procedures.append({
                    "id": procedure.id,
                    "date": procedure.date.isoformat() if procedure.date else None,
                    "action": procedure.action,
                    "short_action": procedure.short_action,
                    "chamber": procedure.chamber,
                    "termen": procedure.termen.isoformat() if procedure.termen else None,
                    "attachment": documents,
                })

            latest_overview = await proposal.overview.all().order_by("-created_at").first()
            overview: ProposalOverview = {
                "id": latest_overview.id,
                "summary": latest_overview.summary,
                "categories": [cat.category_name async for cat in latest_overview.categories.all()],
            } if latest_overview else {
                "id": 0,
                "summary": "",
                "categories": []
            }

            oldest_procedure = await proposal.procedures.all().order_by("date").first()
            latest_procedure = await proposal.procedures.all().order_by("-date").first()

            created_at = oldest_procedure.date.isoformat() if oldest_procedure else proposal.created_at.isoformat()
            latest_action_date = latest_procedure.date.isoformat() if latest_procedure else None

            proposal_data: SerializedProposal = {
                "proposal_id": proposal.id,
                "created_at": created_at,
                "updated_at": latest_action_date,
                "proposal": ProposalDetails(**{
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
                }),
                "initiators": initiators,
                "consults": consults,
                "overview": overview,
                "procedures": procedures,
            }

            await json_cache.set(f"proposal:{proposal.id}", proposal_data, ttl=CACHE_TTL)
            logger.info("processed_proposal", proposal_id=proposal.id)

            return proposal_data
