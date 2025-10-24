from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field


class ProposalDocument(BaseModel):
    id: int
    name: Optional[str] = None
    url: Optional[HttpUrl] = None


class ProposalProcedure(BaseModel):
    id: int
    date: Optional[str] = None  # ISO date
    action: str
    short_action: Optional[str] = None
    chamber: str
    termen: Optional[str] = None  # ISO date
    attachment: List[ProposalDocument] = Field(default_factory=list)


class ProposalInitiator(BaseModel):
    id: int
    name: str
    position: str
    party: str
    is_main: bool
    photo_url: Optional[HttpUrl] = None
    deputy_id: List[int] = Field(default_factory=list)


class ProposalConsult(BaseModel):
    id: int
    name: str
    link: Optional[HttpUrl] = None


class ProposalOverview(BaseModel):
    id: int
    summary: str
    categories: List[str] = Field(default_factory=list)


class ProposalDetails(BaseModel):
    title: str
    idp: Optional[int] = None
    senate_registration_number: Optional[str] = None
    first_senate_registration_number: Optional[str] = None
    cdep_registration_number: Optional[str] = None
    government_registration_number: Optional[str] = None
    first_chamber: str
    initiative: str
    opinion: Optional[str] = None
    urgent_procedure: Optional[str] = None
    status: Optional[str] = None
    status_cdep: Optional[str] = None
    status_senate: Optional[str] = None
    law_character: Optional[str] = None
    deadline: Optional[str] = None
    year_issue: Optional[int] = None
    active: bool
    published: bool
    senate_active: bool
    cdep_active: bool
    promulgare: str
    matching_title: Optional[str] = None


class SerializedProposal(BaseModel):
    proposal_id: int
    created_at: str
    updated_at: Optional[str] = None
    proposal: ProposalDetails
    initiators: List[ProposalInitiator] = Field(default_factory=list)
    consults: List[ProposalConsult] = Field(default_factory=list)
    overview: ProposalOverview
    procedures: List[ProposalProcedure] = Field(default_factory=list)
