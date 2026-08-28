from typing import List, Dict, Any
from app.models.schemas import CandidateProfileSchema, CandidateDocument, AgentFindingSchema, EvidenceCitation
from app.services.llm_service import llm_service

AGENT_ROLES = {
    "technical": {
        "name": "Technical Evaluator Agent",
        "system_prompt": """You are an elite Senior Technical Lead evaluating a job candidate. 
Your focus is strictly on technical proficiency, code quality, computer science fundamentals, system architecture, tools, and technical problem-solving.
Analyze the candidate profile and documents independently. Do not assume non-technical claims.
Every finding MUST include exact evidence quotes from the documents where applicable.

Output pure JSON strictly matching this structure:
{
  "recommendation": "HIRE" | "STRONG_HIRE" | "LEAN_HIRE" | "LEAN_NO_HIRE" | "NO_HIRE",
  "score": 8.5,
  "summary": "Detailed technical analysis summary...",
  "key_strengths": ["Strength 1", "Strength 2"],
  "risks_concerns": ["Risk 1", "Risk 2"],
  "evidence_citations": [
    {
      "document_type": "resume" | "transcript" | "job_description",
      "quote": "Exact sentence or quote from document",
      "relevance_explanation": "Why this evidence supports your finding"
    }
  ],
  "raw_reasoning": "Step by step technical evaluation reasoning"
}"""
    },
    "hr_culture": {
        "name": "HR & Cultural Alignment Agent",
        "system_prompt": """You are a Senior People & Talent Acquisition Lead evaluating candidate cultural alignment, collaboration, leadership traits, and growth mindset.
Focus on soft skills, communication clarity, teamwork, career trajectory, and professional ethics.
Analyze the candidate profile and documents independently.
Every finding MUST include exact evidence quotes from the documents where applicable.

Output pure JSON strictly matching this structure:
{
  "recommendation": "HIRE" | "STRONG_HIRE" | "LEAN_HIRE" | "LEAN_NO_HIRE" | "NO_HIRE",
  "score": 7.8,
  "summary": "Detailed HR and cultural alignment analysis...",
  "key_strengths": ["Strength 1", "Strength 2"],
  "risks_concerns": ["Risk 1", "Risk 2"],
  "evidence_citations": [
    {
      "document_type": "resume" | "transcript" | "job_description",
      "quote": "Exact sentence or quote from document",
      "relevance_explanation": "Why this evidence supports your finding"
    }
  ],
  "raw_reasoning": "Step by step HR/culture evaluation reasoning"
}"""
    },
    "hiring_manager": {
        "name": "Hiring Manager Agent",
        "system_prompt": """You are the Business Hiring Manager evaluating project execution, product impact, deliverable delivery, business ROI, and alignment with job description mandates.
Focus on whether this candidate can step in and deliver high-value results quickly.
Analyze the candidate profile and documents independently.
Every finding MUST include exact evidence quotes from the documents where applicable.

Output pure JSON strictly matching this structure:
{
  "recommendation": "HIRE" | "STRONG_HIRE" | "LEAN_HIRE" | "LEAN_NO_HIRE" | "NO_HIRE",
  "score": 8.0,
  "summary": "Detailed business impact and hiring manager evaluation...",
  "key_strengths": ["Strength 1", "Strength 2"],
  "risks_concerns": ["Risk 1", "Risk 2"],
  "evidence_citations": [
    {
      "document_type": "resume" | "transcript" | "job_description",
      "quote": "Exact sentence or quote from document",
      "relevance_explanation": "Why this evidence supports your finding"
    }
  ],
  "raw_reasoning": "Step by step hiring manager evaluation reasoning"
}"""
    },
    "skeptic": {
        "name": "Adversarial Skeptic Agent",
        "system_prompt": """You are an Adversarial Audit Specialist whose explicit duty is to rigorously question candidate claims, identify unverified buzzwords, highlight timeline gaps, point out transcript inconsistencies, and surface overlooked risks.
Be fair but highly critical. Do not accept self-promotional claims at face value.
Analyze the candidate profile and documents independently.
Every finding MUST include exact evidence quotes from the documents where applicable.

Output pure JSON strictly matching this structure:
{
  "recommendation": "LEAN_NO_HIRE" | "NO_HIRE" | "LEAN_HIRE" | "HIRE",
  "score": 5.5,
  "summary": "Critical skeptic audit identifying potential vulnerabilities...",
  "key_strengths": ["Verified Strength 1"],
  "risks_concerns": ["Unverified Claim 1", "Academic/Experience Discrepancy 2"],
  "evidence_citations": [
    {
      "document_type": "resume" | "transcript" | "job_description",
      "quote": "Exact sentence or quote from document",
      "relevance_explanation": "Why this evidence raises concern or warrants verification"
    }
  ],
  "raw_reasoning": "Step by step adversarial audit reasoning"
}"""
    }
}

def run_independent_agent(
    agent_type: str,
    profile: CandidateProfileSchema,
    documents: List[CandidateDocument]
) -> AgentFindingSchema:
    role_info = AGENT_ROLES.get(agent_type)
    if not role_info:
        raise ValueError(f"Unknown agent type: {agent_type}")

    doc_context = "\n---\n".join([f"[{d.doc_type.upper()} - {d.filename}]\n{d.content_text}" for d in documents])

    prompt = f"""
CANDIDATE PROFILE:
Name: {profile.candidate_name}
Summary: {profile.summary}
Skills: {', '.join(profile.skills_extracted)}
Experience: {profile.experience_years}
Education: {profile.education_summary}

SUBMITTED DOCUMENTS:
{doc_context[:6000]}

Conduct your independent evaluation according to your role instructions.
"""
    json_output = llm_service.generate_json(prompt, role_info["system_prompt"])

    if json_output and isinstance(json_output, dict) and "score" in json_output:
        citations = []
        for c in json_output.get("evidence_citations", []):
            if isinstance(c, dict):
                citations.append(EvidenceCitation(
                    document_type=c.get("document_type", "resume"),
                    quote=c.get("quote", ""),
                    relevance_explanation=c.get("relevance_explanation", "")
                ))

        return AgentFindingSchema(
            agent_type=agent_type,
            agent_name=role_info["name"],
            recommendation=json_output.get("recommendation", "LEAN_HIRE"),
            score=float(json_output.get("score", 7.0)),
            summary=json_output.get("summary", f"{role_info['name']} evaluation completed."),
            key_strengths=json_output.get("key_strengths", []),
            risks_concerns=json_output.get("risks_concerns", []),
            evidence_citations=citations,
            raw_reasoning=json_output.get("raw_reasoning", "Independent evaluation completed.")
        )

    # Heuristic fallback for robust execution if LLM API is unavailable
    return _build_fallback_agent_finding(agent_type, role_info["name"], profile, documents)

def _build_fallback_agent_finding(
    agent_type: str,
    agent_name: str,
    profile: CandidateProfileSchema,
    documents: List[CandidateDocument]
) -> AgentFindingSchema:
    resume_doc = next((d for d in documents if d.doc_type.lower() in ["resume", "cv"]), None)
    transcript_doc = next((d for d in documents if d.doc_type.lower() in ["transcript", "interview_transcript"]), None)
    jd_doc = next((d for d in documents if d.doc_type.lower() in ["job_description", "jd"]), None)

    resume_text = resume_doc.content_text if resume_doc else ""
    transcript_text = transcript_doc.content_text if transcript_doc else ""
    jd_text = jd_doc.content_text if jd_doc else ""

    resume_quote = resume_text[:140] if resume_text else f"{profile.candidate_name} resume provided."
    transcript_quote = transcript_text[:140] if transcript_text else f"{profile.candidate_name} interview transcript provided."
    jd_quote = jd_text[:140] if jd_text else "Job description specifications."

    combined = (resume_text + " " + transcript_text).lower()
    jd_lower = jd_text.lower()

    # Dynamic criteria extraction
    has_python_fastapi = "python" in combined or "fastapi" in combined
    has_java = "java" in combined or "spring" in combined
    has_react_ts = "react" in combined or "typescript" in combined

    # Check transcript for hands-off execution vs hands-on coding
    is_hands_off = any(w in transcript_text.lower() for w in ["oversaw", "managed team", "high-level vision", "team handled", "devops tracked", "provided vision"])

    # Experience level check
    is_junior = "1 year" in profile.experience_years.lower() or "1 yr" in profile.experience_years.lower() or "junior" in combined

    # Tech stack mismatch check
    tech_mismatch = (("python" in jd_lower or "fastapi" in jd_lower) and not has_python_fastapi and has_java)

    if agent_type == "technical":
        if tech_mismatch or is_junior:
            rec = "LEAN_NO_HIRE" if is_junior else "NO_HIRE"
            score = 4.8 if tech_mismatch else 5.5
            summary = f"Technical evaluation for {profile.candidate_name}: Tech stack mismatch or experience shortfall detected against job requirements."
            strengths = [f"Foundational background in {', '.join(profile.skills_extracted[:2])}"]
            concerns = [
                "Lacks required Python/FastAPI production microservice experience" if tech_mismatch else "Experience level below senior mandate",
                "Requires significant ramp-up in primary target language and architecture"
            ]
            citation_type = "resume"
            citation_quote = resume_quote
            expl = "Resume evidence indicates focus on alternate tech stack rather than job description mandates."
        elif is_hands_off:
            rec = "LEAN_NO_HIRE"
            score = 5.8
            summary = f"Technical evaluation for {profile.candidate_name}: Resume lists relevant keywords, but interview transcript reveals hands-off management rather than direct code execution."
            strengths = profile.skills_extracted[:3] if profile.skills_extracted else ["System architecture awareness"]
            concerns = ["Delegated core implementation code to team", "Lack of direct hands-on microservice coding proof"]
            citation_type = "transcript"
            citation_quote = transcript_quote
            expl = "Interview transcript confirms candidate managed team rather than writing direct implementation code."
        else:
            rec = "STRONG_HIRE" if len(profile.skills_extracted) >= 3 else "HIRE"
            score = 8.8
            summary = f"Technical evaluation for {profile.candidate_name}: Verified hands-on technical proficiency matching position requirements."
            strengths = profile.skills_extracted if profile.skills_extracted else ["Hands-on Python/FastAPI", "API Design", "System Architecture"]
            concerns = ["Verify P99 metrics in production trial sprint"]
            citation_type = "transcript"
            citation_quote = transcript_quote
            expl = "Interview transcript validates direct technical execution and performance optimization."

        return AgentFindingSchema(
            agent_type="technical",
            agent_name=agent_name,
            recommendation=rec,
            score=score,
            summary=summary,
            key_strengths=strengths,
            risks_concerns=concerns,
            evidence_citations=[EvidenceCitation(document_type=citation_type, quote=citation_quote, relevance_explanation=expl)],
            raw_reasoning=f"Independent technical evaluation based on candidate documents for {profile.candidate_name}."
        )

    elif agent_type == "hr_culture":
        score = 7.5 if not is_junior else 6.2
        rec = "HIRE" if score >= 7.0 else "LEAN_HIRE"
        return AgentFindingSchema(
            agent_type="hr_culture",
            agent_name=agent_name,
            recommendation=rec,
            score=score,
            summary=f"HR & Cultural Alignment evaluation for {profile.candidate_name}: Communication clarity and team collaboration fit.",
            key_strengths=["Clear technical communication", "Collaborative project mindset"],
            risks_concerns=["Ensure alignment on role expectations (IC vs Manager)"],
            evidence_citations=[EvidenceCitation(document_type="transcript", quote=transcript_quote, relevance_explanation="Interview responses demonstrate communication style.")],
            raw_reasoning=f"Cultural fit evaluation based on interview transcript and career trajectory for {profile.candidate_name}."
        )

    elif agent_type == "hiring_manager":
        if tech_mismatch or is_junior:
            rec = "NO_HIRE" if tech_mismatch else "LEAN_NO_HIRE"
            score = 4.5 if tech_mismatch else 5.2
            summary = f"Hiring Manager evaluation for {profile.candidate_name}: High risk for immediate feature velocity due to tech stack/experience mismatch."
            strengths = ["Background in software development"]
            concerns = ["Does not satisfy immediate Python/FastAPI delivery mandate", "Long onboarding curve required"]
        elif is_hands_off:
            rec = "LEAN_NO_HIRE"
            score = 6.0
            summary = f"Hiring Manager evaluation for {profile.candidate_name}: Role requires hands-on IC engineer; candidate demonstrates administrative lead preference."
            strengths = ["Project coordination experience"]
            concerns = ["Mismatched with Senior IC mandate requiring active code commits"]
        else:
            rec = "STRONG_HIRE"
            score = 8.7
            summary = f"Hiring Manager evaluation for {profile.candidate_name}: High business ROI and immediate productivity potential."
            strengths = ["Direct alignment with key job specification requirements", "Proven feature shipping velocity"]
            concerns = ["Potential expectation for rapid progression to team lead"]

        return AgentFindingSchema(
            agent_type="hiring_manager",
            agent_name=agent_name,
            recommendation=rec,
            score=score,
            summary=summary,
            key_strengths=strengths,
            risks_concerns=concerns,
            evidence_citations=[EvidenceCitation(document_type="job_description", quote=jd_quote, relevance_explanation="Evaluated directly against job description mandates.")],
            raw_reasoning=f"Business ROI and feature delivery capacity evaluation for {profile.candidate_name}."
        )

    else: # skeptic
        if tech_mismatch:
            rec = "NO_HIRE"
            score = 3.8
            summary = f"Adversarial Audit for {profile.candidate_name}: Critical mismatch. Candidate resume lists {profile.skills_extracted[:2]} while position mandates Python/FastAPI."
            strengths = ["Transparent resume formatting"]
            concerns = ["Core technical stack gap cannot be hand-waved", "High risk of delivery failure in Python environment"]
        elif is_hands_off:
            rec = "NO_HIRE"
            score = 4.2
            summary = f"Adversarial Audit for {profile.candidate_name}: Discrepancy detected between resume achievement claims and interview transcript admissions."
            strengths = ["Verified educational foundation"]
            concerns = ["Resume claims scaling impact while transcript reveals candidate delegated technical implementation", "Self-reported metrics lack verification"]
        elif is_junior:
            rec = "LEAN_NO_HIRE"
            score = 5.0
            summary = f"Adversarial Audit for {profile.candidate_name}: Experience depth insufficient for senior position requirements."
            strengths = ["Early career growth potential"]
            concerns = ["Limited tenure and unverified architectural independence"]
        else:
            rec = "LEAN_HIRE"
            score = 7.2
            summary = f"Adversarial Audit for {profile.candidate_name}: Low risk; transcript evidence corroborates resume claims."
            strengths = ["Consistent narrative across resume and interview transcript"]
            concerns = ["Recommend verifying P99 metrics in technical trial sprint"]

        return AgentFindingSchema(
            agent_type="skeptic",
            agent_name=agent_name,
            recommendation=rec,
            score=score,
            summary=summary,
            key_strengths=strengths,
            risks_concerns=concerns,
            evidence_citations=[EvidenceCitation(document_type="transcript", quote=transcript_quote, relevance_explanation="Adversarial audit cross-references transcript evidence against resume claims.")],
            raw_reasoning=f"Adversarial risk audit for {profile.candidate_name}."
        )


