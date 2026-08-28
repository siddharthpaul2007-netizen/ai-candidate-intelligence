export interface EvidenceCitation {
  document_type: string;
  quote: string;
  relevance_explanation: string;
}

export interface CandidateProfile {
  candidate_name: string;
  summary: string;
  skills_extracted: string[];
  experience_years: string;
  education_summary: string;
}

export interface AgentFinding {
  agent_type: "technical" | "hr_culture" | "hiring_manager" | "skeptic" | string;
  agent_name: string;
  recommendation: "STRONG_HIRE" | "HIRE" | "LEAN_HIRE" | "LEAN_NO_HIRE" | "NO_HIRE" | string;
  score: number;
  summary: string;
  key_strengths: string[];
  risks_concerns: string[];
  evidence_citations: EvidenceCitation[];
  raw_reasoning: string;
}

export interface DebateMessage {
  id?: number;
  round_number: number;
  sender_agent: string;
  target_agent: string;
  in_response_to_id?: number | null;
  challenge_point: string;
  response_argument: string;
  evidence_references: EvidenceCitation[];
}

export interface OpinionRevision {
  agent_type: string;
  previous_recommendation: string;
  previous_score: number;
  revised_recommendation: string;
  revised_score: number;
  shift_justification: string;
  opinion_changed: boolean;
}

export interface FinalDecision {
  final_recommendation: "STRONG_HIRE" | "HIRE" | "LEAN_HIRE" | "LEAN_NO_HIRE" | "NO_HIRE" | string;
  consensus_score: number;
  synthesis_summary: string;
  key_tradeoffs: string[];
  disagreement_matrix: Record<string, string>;
  core_justification: string;
}

export interface CandidateDocument {
  id?: number;
  evaluation_id: number;
  doc_type: string;
  filename: string;
  content_text: string;
}

export interface EvaluationData {
  evaluation: {
    id: number;
    title: string;
    position_title: string;
    status: string;
    created_at: string;
  };
  documents: CandidateDocument[];
  profile: CandidateProfile | null;
  findings: AgentFinding[];
  debate_rounds: DebateMessage[];
  revisions: OpinionRevision[];
  final_decision: FinalDecision | null;
}
