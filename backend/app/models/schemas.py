from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON
from pydantic import BaseModel

# DB Models
class Evaluation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    position_title: str
    status: str = Field(default="created") # created, processing, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CandidateDocument(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    evaluation_id: int = Field(foreign_key="evaluation.id")
    doc_type: str # resume, transcript, job_description
    filename: str
    content_text: str

class CandidateProfileDB(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    evaluation_id: int = Field(foreign_key="evaluation.id")
    candidate_name: str
    summary: str
    skills_extracted: List[str] = Field(default=[], sa_column=Column(JSON))
    experience_years: str
    education_summary: str
    raw_profile_json: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

class AgentFindingDB(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    evaluation_id: int = Field(foreign_key="evaluation.id")
    agent_type: str # technical, hr_culture, hiring_manager, skeptic
    agent_name: str
    recommendation: str # HIRE, NO_HIRE, STRONG_HIRE, LEAN_HIRE, LEAN_NO_HIRE
    score: float
    summary: str
    key_strengths: List[str] = Field(default=[], sa_column=Column(JSON))
    risks_concerns: List[str] = Field(default=[], sa_column=Column(JSON))
    evidence_citations: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    raw_reasoning: str

class DebateMessageDB(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    evaluation_id: int = Field(foreign_key="evaluation.id")
    round_number: int = Field(default=1)
    sender_agent: str
    target_agent: str
    in_response_to_id: Optional[int] = None
    challenge_point: str
    response_argument: str
    evidence_references: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))

class OpinionRevisionDB(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    evaluation_id: int = Field(foreign_key="evaluation.id")
    agent_type: str
    previous_recommendation: str
    previous_score: float
    revised_recommendation: str
    revised_score: float
    shift_justification: str
    opinion_changed: bool = False

class FinalDecisionDB(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    evaluation_id: int = Field(foreign_key="evaluation.id")
    final_recommendation: str
    consensus_score: float
    synthesis_summary: str
    key_tradeoffs: List[str] = Field(default=[], sa_column=Column(JSON))
    disagreement_matrix: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    core_justification: str


# Pydantic Schemas for API Requests & Responses
class EvaluationCreate(BaseModel):
    title: str
    position_title: str

class EvidenceCitation(BaseModel):
    document_type: str
    quote: str
    relevance_explanation: str

class AgentFindingSchema(BaseModel):
    agent_type: str
    agent_name: str
    recommendation: str
    score: float
    summary: str
    key_strengths: List[str]
    risks_concerns: List[str]
    evidence_citations: List[EvidenceCitation]
    raw_reasoning: str

class CandidateProfileSchema(BaseModel):
    candidate_name: str
    summary: str
    skills_extracted: List[str]
    experience_years: str
    education_summary: str

class DebateMessageSchema(BaseModel):
    id: Optional[int] = None
    round_number: int
    sender_agent: str
    target_agent: str
    in_response_to_id: Optional[int] = None
    challenge_point: str
    response_argument: str
    evidence_references: List[EvidenceCitation]

class OpinionRevisionSchema(BaseModel):
    agent_type: str
    previous_recommendation: str
    previous_score: float
    revised_recommendation: str
    revised_score: float
    shift_justification: str
    opinion_changed: bool

class FinalDecisionSchema(BaseModel):
    final_recommendation: str
    consensus_score: float
    synthesis_summary: str
    key_tradeoffs: List[str]
    disagreement_matrix: Dict[str, Any]
    core_justification: str

class EvaluationFullResponse(BaseModel):
    evaluation: Evaluation
    documents: List[CandidateDocument]
    profile: Optional[CandidateProfileSchema] = None
    findings: List[AgentFindingSchema] = []
    debate_rounds: List[DebateMessageSchema] = []
    revisions: List[OpinionRevisionSchema] = []
    final_decision: Optional[FinalDecisionSchema] = None
