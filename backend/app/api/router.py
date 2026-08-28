from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select
from app.db.database import get_session
from app.models.schemas import (
    Evaluation, CandidateDocument, CandidateProfileDB, AgentFindingDB,
    DebateMessageDB, OpinionRevisionDB, FinalDecisionDB,
    EvaluationCreate, EvaluationFullResponse, CandidateProfileSchema,
    AgentFindingSchema, DebateMessageSchema, OpinionRevisionSchema, FinalDecisionSchema
)
from app.services.document_parser import extract_document_text
from app.services.profile_builder import build_candidate_profile
from app.services.agents import run_independent_agent
from app.services.debate_engine import run_debate_and_revision
from app.services.final_decision import generate_final_decision

router = APIRouter()

@router.post("/evaluations", response_model=Evaluation)
def create_evaluation(payload: EvaluationCreate, session: Session = Depends(get_session)):
    evaluation = Evaluation(
        title=payload.title,
        position_title=payload.position_title,
        status="created"
    )
    session.add(evaluation)
    session.commit()
    session.refresh(evaluation)
    return evaluation

@router.post("/evaluations/{evaluation_id}/upload", response_model=CandidateDocument)
async def upload_document(
    evaluation_id: int,
    doc_type: str = Form(...), # resume, transcript, job_description
    file: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None),
    session: Session = Depends(get_session)
):
    evaluation = session.get(Evaluation, evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    normalized_type = doc_type.lower().strip()
    if file:
        content_bytes = await file.read()
        extracted_text = extract_document_text(file.filename, content_bytes)
        filename = file.filename
    elif text_content and text_content.strip():
        extracted_text = text_content.strip()
        filename = f"{normalized_type}.txt"
    else:
        raise HTTPException(status_code=400, detail="Either file upload or text content must be provided.")

    doc = CandidateDocument(
        evaluation_id=evaluation_id,
        doc_type=normalized_type,
        filename=filename,
        content_text=extracted_text
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)
    return doc

@router.post("/evaluations/{evaluation_id}/process", response_model=EvaluationFullResponse)
def process_evaluation(evaluation_id: int, session: Session = Depends(get_session)):
    evaluation = session.get(Evaluation, evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    documents = session.exec(select(CandidateDocument).where(CandidateDocument.evaluation_id == evaluation_id)).all()
    if not documents:
        raise HTTPException(status_code=400, detail="No documents uploaded for this evaluation. Please upload Job Description, Resume, and Interview Transcript before processing.")


    # Clear previous evaluation outputs for this evaluation_id to prevent stale data mixing
    session.exec(select(CandidateProfileDB).where(CandidateProfileDB.evaluation_id == evaluation_id)).all()
    for existing_p in session.exec(select(CandidateProfileDB).where(CandidateProfileDB.evaluation_id == evaluation_id)):
        session.delete(existing_p)
    for existing_f in session.exec(select(AgentFindingDB).where(AgentFindingDB.evaluation_id == evaluation_id)):
        session.delete(existing_f)
    for existing_d in session.exec(select(DebateMessageDB).where(DebateMessageDB.evaluation_id == evaluation_id)):
        session.delete(existing_d)
    for existing_r in session.exec(select(OpinionRevisionDB).where(OpinionRevisionDB.evaluation_id == evaluation_id)):
        session.delete(existing_r)
    for existing_dec in session.exec(select(FinalDecisionDB).where(FinalDecisionDB.evaluation_id == evaluation_id)):
        session.delete(existing_dec)
    session.commit()

    evaluation.status = "processing"
    session.add(evaluation)
    session.commit()

    # Step 1: Candidate Profile Construction
    profile_schema = build_candidate_profile(documents)
    
    # Save profile to DB
    profile_db = CandidateProfileDB(
        evaluation_id=evaluation_id,
        candidate_name=profile_schema.candidate_name,
        summary=profile_schema.summary,
        skills_extracted=profile_schema.skills_extracted,
        experience_years=profile_schema.experience_years,
        education_summary=profile_schema.education_summary,
        raw_profile_json=profile_schema.model_dump()
    )
    session.add(profile_db)
    session.commit()

    # Step 2: Four Independent Evaluator Agents (Isolated contexts)
    agent_types = ["technical", "hr_culture", "hiring_manager", "skeptic"]
    findings_schemas: List[AgentFindingSchema] = []

    for agent_type in agent_types:
        finding_schema = run_independent_agent(agent_type, profile_schema, documents)
        findings_schemas.append(finding_schema)

        finding_db = AgentFindingDB(
            evaluation_id=evaluation_id,
            agent_type=finding_schema.agent_type,
            agent_name=finding_schema.agent_name,
            recommendation=finding_schema.recommendation,
            score=finding_schema.score,
            summary=finding_schema.summary,
            key_strengths=finding_schema.key_strengths,
            risks_concerns=finding_schema.risks_concerns,
            evidence_citations=[c.model_dump() for c in finding_schema.evidence_citations],
            raw_reasoning=finding_schema.raw_reasoning
        )
        session.add(finding_db)

    session.commit()

    # Step 3: Debate Stage & Opinion Revisions
    debate_schemas, revision_schemas = run_debate_and_revision(findings_schemas)

    for msg in debate_schemas:
        msg_db = DebateMessageDB(
            evaluation_id=evaluation_id,
            round_number=msg.round_number,
            sender_agent=msg.sender_agent,
            target_agent=msg.target_agent,
            in_response_to_id=msg.in_response_to_id,
            challenge_point=msg.challenge_point,
            response_argument=msg.response_argument,
            evidence_references=[c.model_dump() for c in msg.evidence_references]
        )
        session.add(msg_db)

    for rev in revision_schemas:
        rev_db = OpinionRevisionDB(
            evaluation_id=evaluation_id,
            agent_type=rev.agent_type,
            previous_recommendation=rev.previous_recommendation,
            previous_score=rev.previous_score,
            revised_recommendation=rev.revised_recommendation,
            revised_score=rev.revised_score,
            shift_justification=rev.shift_justification,
            opinion_changed=rev.opinion_changed
        )
        session.add(rev_db)

    session.commit()

    # Step 4: Final Decision Synthesis
    final_decision_schema = generate_final_decision(
        profile_schema, findings_schemas, debate_schemas, revision_schemas
    )

    final_db = FinalDecisionDB(
        evaluation_id=evaluation_id,
        final_recommendation=final_decision_schema.final_recommendation,
        consensus_score=final_decision_schema.consensus_score,
        synthesis_summary=final_decision_schema.synthesis_summary,
        key_tradeoffs=final_decision_schema.key_tradeoffs,
        disagreement_matrix=final_decision_schema.disagreement_matrix,
        core_justification=final_decision_schema.core_justification
    )
    session.add(final_db)

    evaluation.status = "completed"
    session.add(evaluation)
    session.commit()
    session.refresh(evaluation)

    return get_evaluation_detail(evaluation_id, session)

@router.get("/evaluations/{evaluation_id}", response_model=EvaluationFullResponse)
def get_evaluation_detail(evaluation_id: int, session: Session = Depends(get_session)):
    evaluation = session.get(Evaluation, evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    docs = session.exec(select(CandidateDocument).where(CandidateDocument.evaluation_id == evaluation_id)).all()
    
    # Get latest profile and decision if multiple exist
    profiles = session.exec(select(CandidateProfileDB).where(CandidateProfileDB.evaluation_id == evaluation_id)).all()
    profile_db = profiles[-1] if profiles else None

    findings_db = session.exec(select(AgentFindingDB).where(AgentFindingDB.evaluation_id == evaluation_id)).all()
    debate_db = session.exec(select(DebateMessageDB).where(DebateMessageDB.evaluation_id == evaluation_id)).all()
    revisions_db = session.exec(select(OpinionRevisionDB).where(OpinionRevisionDB.evaluation_id == evaluation_id)).all()
    
    decisions = session.exec(select(FinalDecisionDB).where(FinalDecisionDB.evaluation_id == evaluation_id)).all()
    final_db = decisions[-1] if decisions else None


    profile_schema = CandidateProfileSchema(
        candidate_name=profile_db.candidate_name,
        summary=profile_db.summary,
        skills_extracted=profile_db.skills_extracted,
        experience_years=profile_db.experience_years,
        education_summary=profile_db.education_summary
    ) if profile_db else None

    findings_schemas = [
        AgentFindingSchema(
            agent_type=f.agent_type,
            agent_name=f.agent_name,
            recommendation=f.recommendation,
            score=f.score,
            summary=f.summary,
            key_strengths=f.key_strengths,
            risks_concerns=f.risks_concerns,
            evidence_citations=f.evidence_citations,
            raw_reasoning=f.raw_reasoning
        ) for f in findings_db
    ]

    debate_schemas = [
        DebateMessageSchema(
            id=d.id,
            round_number=d.round_number,
            sender_agent=d.sender_agent,
            target_agent=d.target_agent,
            in_response_to_id=d.in_response_to_id,
            challenge_point=d.challenge_point,
            response_argument=d.response_argument,
            evidence_references=d.evidence_references
        ) for d in debate_db
    ]

    revisions_schemas = [
        OpinionRevisionSchema(
            agent_type=r.agent_type,
            previous_recommendation=r.previous_recommendation,
            previous_score=r.previous_score,
            revised_recommendation=r.revised_recommendation,
            revised_score=r.revised_score,
            shift_justification=r.shift_justification,
            opinion_changed=r.opinion_changed
        ) for r in revisions_db
    ]

    final_schema = FinalDecisionSchema(
        final_recommendation=final_db.final_recommendation,
        consensus_score=final_db.consensus_score,
        synthesis_summary=final_db.synthesis_summary,
        key_tradeoffs=final_db.key_tradeoffs,
        disagreement_matrix=final_db.disagreement_matrix,
        core_justification=final_db.core_justification
    ) if final_db else None

    return EvaluationFullResponse(
        evaluation=evaluation,
        documents=docs,
        profile=profile_schema,
        findings=findings_schemas,
        debate_rounds=debate_schemas,
        revisions=revisions_schemas,
        final_decision=final_schema
    )

@router.get("/evaluations", response_model=List[Evaluation])
def list_evaluations(session: Session = Depends(get_session)):
    return session.exec(select(Evaluation)).all()

@router.post("/evaluations/demo", response_model=EvaluationFullResponse)
def seed_demo_evaluation(candidate: str = "A", session: Session = Depends(get_session)):
    cand = candidate.upper().strip() if candidate else "A"
    
    if cand == "B":
        title = "Senior Full-Stack Engineer Evaluation - Candidate B (Jordan Lee)"
    else:
        title = "Senior Full-Stack Engineer Evaluation - Candidate A (Alex Vance)"

    eval_obj = Evaluation(
        title=title,
        position_title="Senior Software Engineer",
        status="created"
    )
    session.add(eval_obj)
    session.commit()
    session.refresh(eval_obj)

    if cand == "B":
        doc1 = CandidateDocument(
            evaluation_id=eval_obj.id,
            doc_type="job_description",
            filename="senior_fullstack_engineer_jd.pdf",
            content_text="Position: Senior Full-Stack Engineer\nRequirements:\n- 4+ years of experience with Python (FastAPI/Django), PostgreSQL, React, TypeScript.\n- Strong computer science fundamentals and hands-on system architecture.\n- Track record of shipping high-impact features and collaborating in agile teams."
        )
        doc2 = CandidateDocument(
            evaluation_id=eval_obj.id,
            doc_type="resume",
            filename="jordan_lee_resume.pdf",
            content_text="Jordan Lee\nLead AI & Full-Stack Architect with 6+ years experience mastering enterprise Web3, AI microservices, React, Python, and cloud infrastructure.\nKey Achievements: Scaled global cloud platform to 10M users. Led team of 15 engineers in AI integration. B.S. Information Technology."
        )
        doc3 = CandidateDocument(
            evaluation_id=eval_obj.id,
            doc_type="transcript",
            filename="jordan_lee_interview_transcript.pdf",
            content_text="Candidate Interview Transcript - Jordan Lee\nInterviewer: Can you detail your contribution to scaling the platform to 10M users?\nJordan Lee: I oversaw the overall architecture strategy and managed the team that migrated services to the cloud. I mostly provided high-level vision and coordinated daily standups.\nInterviewer: How did you implement FastAPI and PostgreSQL connection pooling?\nJordan Lee: My team handled the direct implementation code. I recommended best practices and monitored overall system reliability.\nInterviewer: What specific microservice latency improvements were achieved?\nJordan Lee: Overall system uptime was maintained at 99.9%, though specific microservice latencies were tracked by our DevOps team."
        )
    else:
        doc1 = CandidateDocument(
            evaluation_id=eval_obj.id,
            doc_type="job_description",
            filename="senior_fullstack_engineer_jd.pdf",
            content_text="Position: Senior Full-Stack Engineer\nRequirements:\n- 4+ years of experience with Python (FastAPI/Django), PostgreSQL, React, TypeScript.\n- Strong computer science fundamentals and hands-on system architecture.\n- Track record of shipping high-impact features and collaborating in agile teams."
        )
        doc2 = CandidateDocument(
            evaluation_id=eval_obj.id,
            doc_type="resume",
            filename="alex_vance_resume.pdf",
            content_text="Alex Vance\nSenior Software Engineer with 4 years experience building distributed Python/FastAPI microservices and React/TypeScript dashboards. B.S. CS 3.8 GPA. Reduced API latency by 45% at TechCorp."
        )
        doc3 = CandidateDocument(
            evaluation_id=eval_obj.id,
            doc_type="transcript",
            filename="alex_vance_interview_transcript.pdf",
            content_text="Candidate Interview Transcript - Alex Vance\nInterviewer: Can you explain a complex architecture challenge you solved?\nAlex Vance: At TechCorp, our API gateway suffered high latency under peak traffic. I refactored our FastAPI endpoints to use asynchronous database queries with PostgreSQL connection pooling and Redis caching, reducing P99 latency by 45% and handling 10k req/sec.\nInterviewer: How do you handle team technical disagreements?\nAlex Vance: I focus on benchmark evidence. When debating GraphQL vs REST, I built a benchmark prototype comparing query latency and payload size, which persuaded the team to stick with FastAPI REST endpoints."
        )

    session.add(doc1)
    session.add(doc2)
    session.add(doc3)
    session.commit()

    return process_evaluation(eval_obj.id, session)

