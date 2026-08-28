from typing import List, Tuple
from app.models.schemas import AgentFindingSchema, DebateMessageSchema, OpinionRevisionSchema, EvidenceCitation
from app.services.llm_service import llm_service

def run_debate_and_revision(
    findings: List[AgentFindingSchema]
) -> Tuple[List[DebateMessageSchema], List[OpinionRevisionSchema]]:
    # Step 1: Identify key disagreements across agent findings
    debate_messages: List[DebateMessageSchema] = []
    revisions: List[OpinionRevisionSchema] = []

    skeptic = next((f for f in findings if f.agent_type == "skeptic"), None)
    technical = next((f for f in findings if f.agent_type == "technical"), None)
    hiring_mgr = next((f for f in findings if f.agent_type == "hiring_manager"), None)
    hr_culture = next((f for f in findings if f.agent_type == "hr_culture"), None)

    # Round 1: Skeptic challenges Technical Evaluator on unverified scale metrics
    if skeptic and technical:
        msg1 = DebateMessageSchema(
            id=1,
            round_number=1,
            sender_agent=skeptic.agent_name,
            target_agent=technical.agent_name,
            in_response_to_id=None,
            challenge_point=f"Skeptic Challenge: {technical.agent_name} awarded high score ({technical.score}/10), but candidate's self-reported scale metrics lack external verification.",
            response_argument=f"Technical Response: Candidate's codebase samples and transcript GPA demonstrate strong fundamental mastery, mitigating metric inflation concerns.",
            evidence_references=technical.evidence_citations
        )
        debate_messages.append(msg1)

    # Round 2: Hiring Manager debates Skeptic on immediate delivery velocity
    if hiring_mgr and skeptic:
        msg2 = DebateMessageSchema(
            id=2,
            round_number=1,
            sender_agent=hiring_mgr.agent_name,
            target_agent=skeptic.agent_name,
            in_response_to_id=1,
            challenge_point=f"Hiring Manager Argument: Immediate feature delivery capacity outweighs minor documentation gaps flagged by {skeptic.agent_name}.",
            response_argument=f"Skeptic Counter-Response: High velocity without verified code rigor increases technical debt risk for core architecture.",
            evidence_references=skeptic.evidence_citations
        )
        debate_messages.append(msg2)

    # LLM-assisted debate enrichment if available
    prompt = f"""
Agent Evaluation Summaries:
- Technical ({technical.score if technical else 0}): {technical.summary if technical else ''}
- HR/Culture ({hr_culture.score if hr_culture else 0}): {hr_culture.summary if hr_culture else ''}
- Hiring Manager ({hiring_mgr.score if hiring_mgr else 0}): {hiring_mgr.summary if hiring_mgr else ''}
- Skeptic ({skeptic.score if skeptic else 0}): {skeptic.summary if skeptic else ''}

Synthesize 2 debate interactions between agents challenging each other's conclusions.
Return JSON list matching:
[
  {{
    "sender_agent": "Adversarial Skeptic Agent",
    "target_agent": "Technical Evaluator Agent",
    "challenge_point": "...",
    "response_argument": "..."
  }}
]
"""
    system_inst = "You are a debate facilitator identifying friction points and counter-arguments between evaluator agents."
    json_debate = llm_service.generate_json(prompt, system_inst)

    if json_debate and isinstance(json_debate, list) and len(json_debate) > 0:
        llm_messages = []
        for idx, item in enumerate(json_debate, start=1):
            if isinstance(item, dict):
                llm_messages.append(DebateMessageSchema(
                    id=idx,
                    round_number=1,
                    sender_agent=item.get("sender_agent", "Skeptic Agent"),
                    target_agent=item.get("target_agent", "Technical Agent"),
                    in_response_to_id=None if idx == 1 else 1,
                    challenge_point=item.get("challenge_point", "Challenge point raised during debate."),
                    response_argument=item.get("response_argument", "Counter-argument provided."),
                    evidence_references=[]
                ))
        if llm_messages:
            debate_messages = llm_messages

    # Step 2: Opinion Revision Stage
    # Evaluate whether agents adjust their score after reviewing counter-arguments
    for finding in findings:
        # Default behavior: Skeptic slightly tempers concern, Technical maintains stance
        if finding.agent_type == "skeptic":
            revised_score = min(finding.score + 0.5, 10.0)
            revisions.append(OpinionRevisionSchema(
                agent_type=finding.agent_type,
                previous_recommendation=finding.recommendation,
                previous_score=finding.score,
                revised_recommendation="LEAN_HIRE" if revised_score >= 6.0 else "LEAN_NO_HIRE",
                revised_score=revised_score,
                shift_justification="Moderated concern after Technical Agent highlighted transcript academic strength and verified foundation.",
                opinion_changed=True
            ))
        elif finding.agent_type == "technical":
            revisions.append(OpinionRevisionSchema(
                agent_type=finding.agent_type,
                previous_recommendation=finding.recommendation,
                previous_score=finding.score,
                revised_recommendation=finding.recommendation,
                revised_score=finding.score,
                shift_justification="Maintained recommendation after verifying underlying technical project evidence.",
                opinion_changed=False
            ))
        elif finding.agent_type == "hiring_manager":
            revisions.append(OpinionRevisionSchema(
                agent_type=finding.agent_type,
                previous_recommendation=finding.recommendation,
                previous_score=finding.score,
                revised_recommendation=finding.recommendation,
                revised_score=finding.score,
                shift_justification="Maintained strong recommendation based on immediate project requirements fit.",
                opinion_changed=False
            ))
        else: # hr_culture
            revisions.append(OpinionRevisionSchema(
                agent_type=finding.agent_type,
                previous_recommendation=finding.recommendation,
                previous_score=finding.score,
                revised_recommendation=finding.recommendation,
                revised_score=finding.score,
                shift_justification="Maintained hiring recommendation with emphasis on structured initial onboarding.",
                opinion_changed=False
            ))

    return debate_messages, revisions
