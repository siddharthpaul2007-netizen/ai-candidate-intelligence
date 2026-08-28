from typing import List, Dict
from app.models.schemas import CandidateDocument, CandidateProfileSchema
from app.services.llm_service import llm_service

def build_candidate_profile(documents: List[CandidateDocument]) -> CandidateProfileSchema:
    resume_text = ""
    transcript_text = ""
    job_desc_text = ""

    for doc in documents:
        dtype = doc.doc_type.lower()
        if dtype in ["resume", "cv"]:
            resume_text += f"\n[{doc.filename}]\n{doc.content_text}\n"
        elif dtype in ["transcript", "interview_transcript", "interview"]:
            transcript_text += f"\n[{doc.filename}]\n{doc.content_text}\n"
        elif dtype in ["job_description", "job_description_requirements", "jd"]:
            job_desc_text += f"\n[{doc.filename}]\n{doc.content_text}\n"

    prompt = f"""
Analyze the following candidate evaluation documents and create a neutral, factual candidate profile.

JOB DESCRIPTION:
{job_desc_text[:3000]}

CANDIDATE RESUME:
{resume_text[:3000]}

CANDIDATE INTERVIEW TRANSCRIPT:
{transcript_text[:3000]}

Return JSON strictly matching this schema:
{{
  "candidate_name": "Full Name",
  "summary": "Objective, concise overview of candidate background, resume highlights, and interview transcript performance.",
  "skills_extracted": ["Skill 1", "Skill 2", "Skill 3"],
  "experience_years": "X years",
  "education_summary": "Degree, Major, Institution, GPA (if available)"
}}
"""
    system_instruction = "You are a neutral candidate profile extraction system. Output pure JSON summarizing evidence from Job Description, Candidate Resume, and Interview Transcript without bias or evaluation."
    json_result = llm_service.generate_json(prompt, system_instruction)

    if json_result and isinstance(json_result, dict) and "candidate_name" in json_result:
        return CandidateProfileSchema(
            candidate_name=json_result.get("candidate_name", "Candidate"),
            summary=json_result.get("summary", "Extracted profile from candidate documents."),
            skills_extracted=json_result.get("skills_extracted", []),
            experience_years=json_result.get("experience_years", "Not specified"),
            education_summary=json_result.get("education_summary", "Not specified")
        )

    # Dynamic heuristic parser if LLM API is unavailable
    resume_lines = [line.strip() for line in resume_text.split("\n") if line.strip() and not line.strip().startswith("[")]
    candidate_name = resume_lines[0] if resume_lines else "Evaluated Candidate"

    combined_text = (resume_text + " " + transcript_text).lower()

    # Dynamic tech skill extraction
    all_tech_keywords = [
        "Python", "FastAPI", "Django", "Flask", "Java", "Spring Boot", "Spring", "JavaScript", "TypeScript",
        "React", "Node.js", "Express", "Angular", "Vue", "PostgreSQL", "MySQL", "MongoDB", "Redis",
        "Docker", "Kubernetes", "AWS", "Kafka", "GraphQL", "REST APIs", "C++", "C#", ".NET", "Go"
    ]
    found_skills = [s for s in all_tech_keywords if s.lower() in combined_text]
    if not found_skills:
        found_skills = ["Software Engineering", "Application Development", "Technical Problem Solving"]

    # Dynamic experience extraction
    import re
    exp_years = "Not specified"
    exp_match = re.search(r"(\d+\+?\s*(?:years?|yrs?)(?:\s*of\s*experience)?)", combined_text, re.IGNORECASE)
    if exp_match:
        exp_years = exp_match.group(1).title()

    # Dynamic education extraction
    edu_summary = "Computer Science / Technical Field"
    if "b.s." in combined_text or "bachelor" in combined_text or "b.sc" in combined_text:
        edu_summary = "Bachelor of Science (B.S.) Degree"
    elif "m.s." in combined_text or "master" in combined_text:
        edu_summary = "Master of Science (M.S.) Degree"

    return CandidateProfileSchema(
        candidate_name=candidate_name,
        summary=f"Candidate profile dynamically parsed from {len(documents)} document(s): Resume, Interview Transcript, and Job Description.",
        skills_extracted=found_skills,
        experience_years=exp_years,
        education_summary=edu_summary
    )


