import pytest
from app.models.schemas import CandidateProfileSchema, CandidateDocument
from app.services.agents import run_independent_agent

def test_independent_agent_isolation():
    profile = CandidateProfileSchema(
        candidate_name="Test Candidate",
        summary="Test summary",
        skills_extracted=["Python", "FastAPI"],
        experience_years="5 years",
        education_summary="B.S. CS"
    )
    docs = [
        CandidateDocument(
            evaluation_id=1,
            doc_type="resume",
            filename="resume.pdf",
            content_text="Experienced engineer proficient in Python microservices."
        )
    ]

    # Run technical agent
    tech_finding = run_independent_agent("technical", profile, docs)
    assert tech_finding.agent_type == "technical"
    assert tech_finding.score >= 1.0 and tech_finding.score <= 10.0
    assert len(tech_finding.evidence_citations) > 0

    # Run skeptic agent
    skeptic_finding = run_independent_agent("skeptic", profile, docs)
    assert skeptic_finding.agent_type == "skeptic"
    assert skeptic_finding.agent_name == "Adversarial Skeptic Agent"
    assert len(skeptic_finding.evidence_citations) > 0

    # Verify agent outputs are distinct and independent
    assert tech_finding.agent_type != skeptic_finding.agent_type
