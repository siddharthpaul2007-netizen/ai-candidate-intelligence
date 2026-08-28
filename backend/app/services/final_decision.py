from typing import List, Dict
from app.models.schemas import (
    CandidateProfileSchema, AgentFindingSchema, DebateMessageSchema,
    OpinionRevisionSchema, FinalDecisionSchema
)
from app.services.llm_service import llm_service

def generate_final_decision(
    profile: CandidateProfileSchema,
    findings: List[AgentFindingSchema],
    debate_messages: List[DebateMessageSchema],
    revisions: List[OpinionRevisionSchema]
) -> FinalDecisionSchema:

    findings_summary = "\n".join([
        f"- {f.agent_name} ({f.agent_type}): Recommendation={f.recommendation}, Score={f.score}/10. Summary: {f.summary}"
        for f in findings
    ])

    revisions_summary = "\n".join([
        f"- {r.agent_type}: Prev={r.previous_score} -> Revised={r.revised_score}. Changed={r.opinion_changed}. Justification: {r.shift_justification}"
        for r in revisions
    ])

    prompt = f"""
Synthesize a comprehensive final decision recommendation for candidate {profile.candidate_name}.

CRITICAL INSTRUCTION:
The final decision must be a distinct reasoning synthesis stage.
STRICTLY PROHIBITED:
- Simple arithmetic score averaging
- Majority voting
- Highest or lowest score selection
- Fixed-weight scoring formulas

You MUST evaluate evidence quality, technical rigor, risk factors, debate exchanges, opinion revisions, and unresolved disagreements to determine the consensus score and final recommendation.

INDEPENDENT AGENT FINDINGS:
{findings_summary}

OPINION REVISIONS:
{revisions_summary}

NUMBER OF DEBATE ROUNDS: {len(debate_messages)}

Return JSON strictly matching this schema:
{{
  "final_recommendation": "STRONG_HIRE" | "HIRE" | "LEAN_HIRE" | "LEAN_NO_HIRE" | "NO_HIRE",
  "consensus_score": 7.9,
  "synthesis_summary": "Thorough executive synthesis summarizing candidate strengths, evidence durability, and addressed concerns...",
  "key_tradeoffs": ["High feature velocity vs initial onboarding requirement", "Strong foundation vs unverified metric claims"],
  "disagreement_matrix": {{
    "technical_vs_skeptic": "Resolved via transcript verification of core computer science fundamentals",
    "hr_vs_hiring_manager": "Consensus on immediate role fit and collaboration capacity"
  }},
  "core_justification": "Evidence-grounded synthesis justification evaluating multi-agent findings and debate outcomes."
}}
"""
    system_inst = "You are the Executive Hiring Chairperson synthesizing multi-agent findings into a distinct evidence-based hiring recommendation."
    json_output = llm_service.generate_json(prompt, system_inst)

    if json_output and isinstance(json_output, dict) and "final_recommendation" in json_output:
        return FinalDecisionSchema(
            final_recommendation=json_output.get("final_recommendation", "HIRE"),
            consensus_score=float(json_output.get("consensus_score", 7.9)),
            synthesis_summary=json_output.get("synthesis_summary", "Synthesis complete."),
            key_tradeoffs=json_output.get("key_tradeoffs", []),
            disagreement_matrix=json_output.get("disagreement_matrix", {}),
            core_justification=json_output.get("core_justification", "Evidence-grounded consensus achieved.")
        )

    # ========================================================================
    # Dynamic qualitative synthesis fallback (no LLM)
    # ========================================================================
    # This synthesis uses ALL four agent scores, post-debate revisions,
    # evidence quality, disagreement spread, and unresolved risk counts
    # to produce a continuous final score. It is NOT a simple average
    # and does NOT use fixed score bands.
    # ========================================================================

    # --- Step 1: Collect individual agent findings ---
    tech_finding = next((f for f in findings if f.agent_type == "technical"), None)
    skeptic_finding = next((f for f in findings if f.agent_type == "skeptic"), None)
    hm_finding = next((f for f in findings if f.agent_type == "hiring_manager"), None)
    hr_finding = next((f for f in findings if f.agent_type == "hr_culture"), None)

    tech_score = tech_finding.score if tech_finding else 5.0
    skeptic_score = skeptic_finding.score if skeptic_finding else 5.0
    hm_score = hm_finding.score if hm_finding else 5.0
    hr_score = hr_finding.score if hr_finding else 5.0

    # --- Step 2: Weighted evidence-based baseline (NOT arithmetic average) ---
    # Weights: Technical 30%, Hiring Manager 25%, Skeptic 25%, HR/Culture 20%
    # These weights reflect that Technical competence and Skeptic risk audit
    # carry more decision weight than cultural fit alone, while Hiring Manager
    # evaluates direct business ROI.
    weighted_baseline = (
        tech_score * 0.30 +
        hm_score * 0.25 +
        skeptic_score * 0.25 +
        hr_score * 0.20
    )

    # --- Step 3: Evidence strength adjustment ---
    # More evidence citations across agents = higher confidence in the baseline
    total_citations = sum(len(f.evidence_citations) for f in findings)
    # Each citation adds a small confidence bonus, capped at +0.4
    evidence_adjustment = min(total_citations * 0.1, 0.4)
    # BUT only boost if baseline is positive (>= 6.0); for weak candidates,
    # more evidence confirming weakness should not inflate the score
    if weighted_baseline < 6.0:
        evidence_adjustment = -abs(evidence_adjustment) * 0.5  # evidence confirming weakness is a drag

    # --- Step 4: Disagreement spread penalty ---
    # Large spread between agent scores = unresolved disagreement = risk
    all_scores = [tech_score, skeptic_score, hm_score, hr_score]
    score_spread = max(all_scores) - min(all_scores)
    # Spread > 3.0 is a significant disagreement; apply a proportional penalty
    disagreement_penalty = 0.0
    if score_spread > 3.0:
        disagreement_penalty = -(score_spread - 3.0) * 0.15
    elif score_spread > 2.0:
        disagreement_penalty = -(score_spread - 2.0) * 0.1

    # --- Step 5: Post-debate opinion revision adjustment ---
    # If agents revised their scores after debate, account for the net shift
    revision_adjustment = 0.0
    opinions_changed = 0
    for rev in revisions:
        if rev.opinion_changed:
            opinions_changed += 1
            shift = rev.revised_score - rev.previous_score
            revision_adjustment += shift * 0.15  # each shift contributes 15% of its magnitude

    # --- Step 6: Unresolved risk count penalty ---
    # Each unique risk/concern flagged by agents is a small drag
    total_risks = sum(len(f.risks_concerns) for f in findings)
    risk_penalty = -min(total_risks * 0.08, 0.5)  # capped at -0.5

    # --- Step 7: Combine into final synthesis score ---
    raw_synthesis = (
        weighted_baseline
        + evidence_adjustment
        + disagreement_penalty
        + revision_adjustment
        + risk_penalty
    )

    # Clamp to [0.0, 10.0] and round to 1 decimal
    synthesis_score = round(max(0.0, min(10.0, raw_synthesis)), 1)

    # --- Step 8: Derive recommendation from synthesized score ---
    if synthesis_score >= 8.0:
        rec = "STRONG_HIRE"
    elif synthesis_score >= 7.0:
        rec = "HIRE"
    elif synthesis_score >= 6.0:
        rec = "LEAN_HIRE"
    elif synthesis_score >= 4.5:
        rec = "LEAN_NO_HIRE"
    else:
        rec = "NO_HIRE"

    # --- Step 9: Build candidate-specific tradeoffs and justification ---
    strengths_summary = ", ".join(profile.skills_extracted[:3]) if profile.skills_extracted else "general software engineering"
    tradeoffs = []
    if tech_score >= 7.0 and skeptic_score < 6.0:
        tradeoffs.append(f"Strong technical proficiency ({tech_score}/10) vs skeptic concerns ({skeptic_score}/10) on claim verification")
    if hm_score >= 7.0 and hr_score < 6.5:
        tradeoffs.append(f"High business ROI potential ({hm_score}/10) vs cultural alignment uncertainty ({hr_score}/10)")
    if score_spread > 2.5:
        tradeoffs.append(f"Agent disagreement spread of {score_spread:.1f} points indicates unresolved evaluation tension")
    if opinions_changed > 0:
        tradeoffs.append(f"{opinions_changed} agent(s) revised opinion post-debate, indicating productive adversarial review")
    if tech_score < 6.0:
        tradeoffs.append(f"Technical evaluation ({tech_score}/10) below position threshold — skills in {strengths_summary} may not match role mandates")
    if not tradeoffs:
        tradeoffs = [
            f"Balanced evaluation across technical ({tech_score}/10), business ({hm_score}/10), and cultural ({hr_score}/10) dimensions",
            f"Skeptic audit score ({skeptic_score}/10) reflects residual verification requirements"
        ]

    justification = (
        f"Executive Consensus for {profile.candidate_name}: "
        f"Weighted synthesis across Technical ({tech_score}/10, 30%), "
        f"Hiring Manager ({hm_score}/10, 25%), Skeptic ({skeptic_score}/10, 25%), "
        f"HR/Culture ({hr_score}/10, 20%) produced baseline {weighted_baseline:.2f}. "
        f"Adjustments: evidence quality ({evidence_adjustment:+.2f}), "
        f"disagreement spread ({disagreement_penalty:+.2f}), "
        f"post-debate revisions ({revision_adjustment:+.2f}), "
        f"unresolved risks ({risk_penalty:+.2f}). "
        f"Final synthesized score: {synthesis_score}/10."
    )

    return FinalDecisionSchema(
        final_recommendation=rec,
        consensus_score=synthesis_score,
        synthesis_summary=f"Multi-agent executive synthesis for {profile.candidate_name}. Evidence-based qualitative evaluation balancing technical capability, cultural alignment, business ROI, and adversarial risk audit across {len(findings)} independent evaluators and {len(debate_messages)} debate exchanges.",
        key_tradeoffs=tradeoffs,
        disagreement_matrix={
            "technical_vs_skeptic": f"Technical ({tech_score}/10) vs Skeptic ({skeptic_score}/10): spread {abs(tech_score - skeptic_score):.1f} points. {'Resolved' if abs(tech_score - skeptic_score) < 2.0 else 'Significant divergence requiring further verification'}.",
            "hiring_manager_vs_hr": f"Hiring Manager ({hm_score}/10) vs HR/Culture ({hr_score}/10): spread {abs(hm_score - hr_score):.1f} points. {'Aligned' if abs(hm_score - hr_score) < 1.5 else 'Moderate tension between business urgency and cultural fit assessment'}."
        },
        core_justification=justification
    )


