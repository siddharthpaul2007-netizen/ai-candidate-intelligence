import pytest
from app.models.schemas import CandidateProfileSchema, AgentFindingSchema, EvidenceCitation, OpinionRevisionSchema

from app.services.final_decision import generate_final_decision


def _make_finding(agent_type, agent_name, score, recommendation, risks=None, citations=None):
    """Helper to create an AgentFindingSchema with minimal boilerplate."""
    return AgentFindingSchema(
        agent_type=agent_type,
        agent_name=agent_name,
        recommendation=recommendation,
        score=score,
        summary=f"{agent_name} evaluation completed.",
        key_strengths=["Strength A"],
        risks_concerns=risks or [],
        evidence_citations=citations or [],
        raw_reasoning=f"{agent_name} reasoning."
    )


def _make_profile(name="Test Candidate", skills=None):
    return CandidateProfileSchema(
        candidate_name=name,
        summary="Test summary",
        skills_extracted=skills or ["Python"],
        experience_years="5 years",
        education_summary="B.S. CS"
    )


def test_final_decision_not_simple_average():
    """The final score must NOT equal the arithmetic average of agent scores."""
    profile = _make_profile()

    findings = [
        _make_finding("technical", "Technical Evaluator Agent", 9.0, "STRONG_HIRE",
                       citations=[EvidenceCitation(document_type="resume", quote="Built system", relevance_explanation="High skill")]),
        _make_finding("hiring_manager", "Hiring Manager Agent", 9.0, "STRONG_HIRE"),
        _make_finding("hr_culture", "HR & Cultural Alignment Agent", 8.0, "HIRE"),
        _make_finding("skeptic", "Adversarial Skeptic Agent", 4.0, "LEAN_NO_HIRE",
                       risks=["Missing scale proof"]),
    ]

    simple_average = (9.0 + 9.0 + 8.0 + 4.0) / 4.0  # 7.5

    decision = generate_final_decision(profile, findings, [], [])

    assert decision.final_recommendation in ["STRONG_HIRE", "HIRE", "LEAN_HIRE"]
    assert decision.consensus_score != simple_average, \
        f"Final score {decision.consensus_score} must not equal simple average {simple_average}"
    assert len(decision.key_tradeoffs) > 0
    assert "technical_vs_skeptic" in decision.disagreement_matrix


def test_different_agent_scores_produce_different_final_scores():
    """Two candidate profiles with different agent scores must produce different final scores."""
    profile_a = _make_profile("Candidate Alpha", ["Python", "FastAPI", "React"])
    findings_a = [
        _make_finding("technical", "Technical Evaluator Agent", 8.8, "STRONG_HIRE",
                       citations=[EvidenceCitation(document_type="resume", quote="Async FastAPI", relevance_explanation="Match")]),
        _make_finding("hiring_manager", "Hiring Manager Agent", 8.7, "STRONG_HIRE"),
        _make_finding("hr_culture", "HR & Cultural Alignment Agent", 7.5, "HIRE"),
        _make_finding("skeptic", "Adversarial Skeptic Agent", 7.2, "LEAN_HIRE",
                       risks=["Verify P99 metrics"]),
    ]

    profile_b = _make_profile("Candidate Beta", ["Java", "Spring Boot"])
    findings_b = [
        _make_finding("technical", "Technical Evaluator Agent", 4.8, "NO_HIRE",
                       risks=["Tech stack mismatch", "No Python experience"]),
        _make_finding("hiring_manager", "Hiring Manager Agent", 4.5, "NO_HIRE",
                       risks=["Long onboarding"]),
        _make_finding("hr_culture", "HR & Cultural Alignment Agent", 6.2, "LEAN_HIRE"),
        _make_finding("skeptic", "Adversarial Skeptic Agent", 3.8, "NO_HIRE",
                       risks=["Core stack gap", "Delivery risk"]),
    ]

    decision_a = generate_final_decision(profile_a, findings_a, [], [])
    decision_b = generate_final_decision(profile_b, findings_b, [], [])

    assert decision_a.consensus_score != decision_b.consensus_score, \
        f"Candidates with different agents must get different scores: A={decision_a.consensus_score}, B={decision_b.consensus_score}"
    assert decision_a.consensus_score > decision_b.consensus_score, \
        "Stronger candidate should score higher"


def test_hr_and_hiring_manager_influence_final_score():
    """Changing only HR and Hiring Manager scores must change the final score."""
    profile = _make_profile()

    base_findings = [
        _make_finding("technical", "Technical Evaluator Agent", 7.0, "HIRE"),
        _make_finding("skeptic", "Adversarial Skeptic Agent", 6.0, "LEAN_HIRE"),
    ]

    # Variant 1: Strong HR + strong HM
    findings_strong = base_findings + [
        _make_finding("hiring_manager", "Hiring Manager Agent", 9.0, "STRONG_HIRE"),
        _make_finding("hr_culture", "HR & Cultural Alignment Agent", 8.5, "STRONG_HIRE"),
    ]

    # Variant 2: Weak HR + weak HM (same tech + skeptic)
    findings_weak = base_findings + [
        _make_finding("hiring_manager", "Hiring Manager Agent", 4.0, "NO_HIRE"),
        _make_finding("hr_culture", "HR & Cultural Alignment Agent", 4.0, "NO_HIRE"),
    ]

    decision_strong = generate_final_decision(profile, findings_strong, [], [])
    decision_weak = generate_final_decision(profile, findings_weak, [], [])

    assert decision_strong.consensus_score != decision_weak.consensus_score, \
        f"HR/HM changes must affect score: strong={decision_strong.consensus_score}, weak={decision_weak.consensus_score}"
    assert decision_strong.consensus_score > decision_weak.consensus_score


def test_debate_revisions_influence_final_score():
    """Post-debate opinion revisions must influence the final score."""
    profile = _make_profile()
    findings = [
        _make_finding("technical", "Technical Evaluator Agent", 7.5, "HIRE"),
        _make_finding("hiring_manager", "Hiring Manager Agent", 7.0, "HIRE"),
        _make_finding("hr_culture", "HR & Cultural Alignment Agent", 7.0, "HIRE"),
        _make_finding("skeptic", "Adversarial Skeptic Agent", 5.0, "LEAN_NO_HIRE"),
    ]

    # Without revisions
    decision_no_rev = generate_final_decision(profile, findings, [], [])

    # With positive revision (skeptic moderated upward)
    revisions = [
        OpinionRevisionSchema(
            agent_type="skeptic",
            previous_recommendation="LEAN_NO_HIRE",
            previous_score=5.0,
            revised_recommendation="LEAN_HIRE",
            revised_score=6.5,
            shift_justification="Technical evidence addressed concerns.",
            opinion_changed=True
        )
    ]
    decision_with_rev = generate_final_decision(profile, findings, [], revisions)

    assert decision_with_rev.consensus_score != decision_no_rev.consensus_score, \
        f"Revisions must affect score: with={decision_with_rev.consensus_score}, without={decision_no_rev.consensus_score}"
    assert decision_with_rev.consensus_score > decision_no_rev.consensus_score, \
        "Positive revision (skeptic upward) should increase final score"


def test_no_fixed_score_bands():
    """Verify that scores like 8.5, 6.8, 5.4, 4.2 are NOT the only possible outputs."""
    profile = _make_profile()

    # Generate scores for many different agent score combinations
    test_cases = [
        (8.8, 8.2, 8.0, 5.8),
        (7.4, 7.8, 7.1, 6.5),
        (6.2, 7.0, 6.5, 4.8),
        (9.5, 9.0, 8.5, 8.0),
        (5.5, 5.2, 6.2, 5.0),
        (3.5, 4.0, 5.0, 3.0),
    ]

    scores = set()
    for tech, hm, hr, skeptic in test_cases:
        findings = [
            _make_finding("technical", "Technical Evaluator Agent", tech, "HIRE"),
            _make_finding("hiring_manager", "Hiring Manager Agent", hm, "HIRE"),
            _make_finding("hr_culture", "HR & Cultural Alignment Agent", hr, "HIRE"),
            _make_finding("skeptic", "Adversarial Skeptic Agent", skeptic, "LEAN_HIRE"),
        ]
        decision = generate_final_decision(profile, findings, [], [])
        scores.add(decision.consensus_score)

    old_fixed_bands = {8.5, 6.8, 5.4, 4.2}
    assert len(scores) == len(test_cases), \
        f"Each distinct input set must produce a distinct score. Got {len(scores)} unique scores from {len(test_cases)} inputs: {sorted(scores)}"
    assert not scores.issubset(old_fixed_bands), \
        f"Scores must not all fall within old fixed bands. Got: {sorted(scores)}"


def test_three_materially_different_candidates():
    """Three candidates with materially different profiles must produce three different final scores."""
    # Candidate A: Strong match
    profile_a = _make_profile("Alice Strong", ["Python", "FastAPI", "PostgreSQL"])
    findings_a = [
        _make_finding("technical", "Technical Evaluator Agent", 8.8, "STRONG_HIRE",
                       citations=[EvidenceCitation(document_type="transcript", quote="I built async FastAPI", relevance_explanation="Direct match")]),
        _make_finding("hiring_manager", "Hiring Manager Agent", 8.7, "STRONG_HIRE"),
        _make_finding("hr_culture", "HR & Cultural Alignment Agent", 7.5, "HIRE"),
        _make_finding("skeptic", "Adversarial Skeptic Agent", 7.2, "LEAN_HIRE",
                       risks=["Verify metrics"]),
    ]

    # Candidate B: Moderate match
    profile_b = _make_profile("Bob Moderate", ["JavaScript", "Node.js", "MongoDB"])
    findings_b = [
        _make_finding("technical", "Technical Evaluator Agent", 6.5, "LEAN_HIRE",
                       citations=[EvidenceCitation(document_type="resume", quote="Node.js APIs", relevance_explanation="Partial match")]),
        _make_finding("hiring_manager", "Hiring Manager Agent", 6.8, "LEAN_HIRE"),
        _make_finding("hr_culture", "HR & Cultural Alignment Agent", 7.0, "HIRE"),
        _make_finding("skeptic", "Adversarial Skeptic Agent", 5.5, "LEAN_NO_HIRE",
                       risks=["No Python experience", "Different paradigm"]),
    ]

    # Candidate C: Weak match
    profile_c = _make_profile("Charlie Weak", ["Java", "Spring Boot"])
    findings_c = [
        _make_finding("technical", "Technical Evaluator Agent", 4.8, "NO_HIRE",
                       risks=["Major stack mismatch"]),
        _make_finding("hiring_manager", "Hiring Manager Agent", 4.5, "NO_HIRE",
                       risks=["Cannot deliver immediately"]),
        _make_finding("hr_culture", "HR & Cultural Alignment Agent", 6.2, "LEAN_HIRE"),
        _make_finding("skeptic", "Adversarial Skeptic Agent", 3.8, "NO_HIRE",
                       risks=["Core gap", "Delivery risk", "Misaligned stack"]),
    ]

    decision_a = generate_final_decision(profile_a, findings_a, [], [])
    decision_b = generate_final_decision(profile_b, findings_b, [], [])
    decision_c = generate_final_decision(profile_c, findings_c, [], [])

    all_scores = [decision_a.consensus_score, decision_b.consensus_score, decision_c.consensus_score]
    assert len(set(all_scores)) == 3, \
        f"Three different candidates must produce three different scores. Got: {all_scores}"
    assert decision_a.consensus_score > decision_b.consensus_score > decision_c.consensus_score, \
        f"Scores must reflect candidate strength ordering: A={decision_a.consensus_score}, B={decision_b.consensus_score}, C={decision_c.consensus_score}"

    print(f"\n3-Candidate Dynamic Scoring Results:")
    print(f"  Alice Strong:   {decision_a.consensus_score}/10 ({decision_a.final_recommendation})")
    print(f"  Bob Moderate:   {decision_b.consensus_score}/10 ({decision_b.final_recommendation})")
    print(f"  Charlie Weak:   {decision_c.consensus_score}/10 ({decision_c.final_recommendation})")
