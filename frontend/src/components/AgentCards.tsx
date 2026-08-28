"use client";

import React, { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AgentFinding, EvidenceCitation } from "@/types/evaluation";

interface Props {
  findings: AgentFinding[];
  onSelectEvidence?: (citation: EvidenceCitation) => void;
}

const AGENT_CONFIG: Record<string, { label: string; role: string; badgeCls: string; borderAccent: string; scoreBar: string }> = {
  technical: {
    label: "TECHNICAL EVALUATOR",
    role: "Senior Technical Lead · Code & CS Fundamentals",
    badgeCls: "border-blue-500/40 text-blue-400 bg-blue-500/10",
    borderAccent: "border-l-blue-500",
    scoreBar: "bg-blue-500",
  },
  hiring_manager: {
    label: "HIRING MANAGER",
    role: "Business Lead · Delivery Velocity & ROI",
    badgeCls: "border-emerald-500/40 text-emerald-400 bg-emerald-500/10",
    borderAccent: "border-l-emerald-500",
    scoreBar: "bg-emerald-500",
  },
  hr_culture: {
    label: "HR & CULTURE",
    role: "People & Talent Lead · Collaboration & Growth",
    badgeCls: "border-violet-500/40 text-violet-400 bg-violet-500/10",
    borderAccent: "border-l-violet-500",
    scoreBar: "bg-violet-500",
  },
  skeptic: {
    label: "ADVERSARIAL SKEPTIC",
    role: "Audit Specialist · Unverified Claims & Risk Discovery",
    badgeCls: "border-rose-500/40 text-rose-400 bg-rose-500/10",
    borderAccent: "border-l-rose-500",
    scoreBar: "bg-rose-500",
  },
};

const REC_BADGE: Record<string, string> = {
  STRONG_HIRE:  "border-emerald-500/40 text-emerald-400 bg-emerald-500/10",
  HIRE:         "border-green-500/40 text-green-400 bg-green-500/10",
  LEAN_HIRE:    "border-amber-500/40 text-amber-400 bg-amber-500/10",
  LEAN_NO_HIRE: "border-orange-500/40 text-orange-400 bg-orange-500/10",
  NO_HIRE:      "border-rose-500/40 text-rose-400 bg-rose-500/10",
};

export const AgentCards: React.FC<Props> = ({ findings, onSelectEvidence }) => {
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  if (findings.length === 0) {
    return (
      <div className="p-12 text-center border border-dashed border-border/80 rounded-2xl bg-card/40 text-xs text-muted-foreground">
        No evaluator findings generated yet. Execute an evaluation session to see multi-agent outputs.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-foreground">Four Independent Evaluator Agents</h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            Isolated evaluator executions without cross-agent context leakage.
          </p>
        </div>
        <Badge variant="outline" className="text-[10px] font-mono text-muted-foreground">
          {findings.length} Isolated Agents
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {findings.map((agent) => {
          const config = AGENT_CONFIG[agent.agent_type] ?? {
            label: agent.agent_type.replace(/_/g, " ").toUpperCase(),
            role: agent.agent_name,
            badgeCls: "border-border text-muted-foreground",
            borderAccent: "border-l-border",
            scoreBar: "bg-primary",
          };
          const recBadgeCls = REC_BADGE[agent.recommendation] ?? "border-border text-foreground";
          const isExpanded = expandedAgent === agent.agent_type;
          const pct = Math.min(100, Math.max(0, Math.round(agent.score * 10)));

          return (
            <div
              key={agent.agent_type}
              className={`rounded-2xl border border-border/80 bg-card/90 backdrop-blur-sm border-l-4 ${config.borderAccent} flex flex-col justify-between shadow-sm overflow-hidden`}
            >
              {/* Agent Header */}
              <div className="p-5 border-b border-border/60 space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className={`text-[10px] font-mono font-bold tracking-wider px-2 py-0.5 rounded border ${config.badgeCls}`}>
                        {config.label}
                      </span>
                    </div>
                    <div className="font-bold text-sm text-foreground">{agent.agent_name}</div>
                    <div className="text-[11px] text-muted-foreground">{config.role}</div>
                  </div>

                  <div className="text-right shrink-0">
                    <div className="text-2xl font-black text-foreground font-mono leading-none">
                      {agent.score.toFixed(1)} <span className="text-xs text-muted-foreground font-normal">/ 10</span>
                    </div>
                    <div className="mt-1.5">
                      <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${recBadgeCls}`}>
                        {agent.recommendation.replace(/_/g, " ")}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Score meter */}
                <div className="h-1.5 w-full bg-border/60 rounded-full overflow-hidden">
                  <div className={`h-full rounded-full ${config.scoreBar} transition-all duration-500`} style={{ width: `${pct}%` }} />
                </div>

                {/* Summary */}
                <p className="text-xs text-foreground/85 leading-relaxed pt-1">
                  {agent.summary}
                </p>
              </div>

              {/* Agent Findings Breakdown */}
              <div className="p-5 space-y-4 text-xs flex-1">
                {/* Strengths */}
                {agent.key_strengths.length > 0 && (
                  <div className="space-y-1.5">
                    <span className="font-mono text-[10px] font-bold uppercase tracking-wider text-emerald-400 block">
                      Verified Strengths
                    </span>
                    <ul className="space-y-1">
                      {agent.key_strengths.map((str, i) => (
                        <li key={i} className="flex items-start gap-2 text-foreground/80 leading-relaxed">
                          <span className="text-emerald-400 font-bold text-xs shrink-0">✓</span>
                          <span>{str}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Risks & Concerns */}
                {agent.risks_concerns.length > 0 && (
                  <div className="space-y-1.5">
                    <span className="font-mono text-[10px] font-bold uppercase tracking-wider text-rose-400 block">
                      Audited Risks & Vulnerabilities
                    </span>
                    <ul className="space-y-1">
                      {agent.risks_concerns.map((risk, i) => (
                        <li key={i} className="flex items-start gap-2 text-foreground/80 leading-relaxed">
                          <span className="text-rose-400 font-bold text-xs shrink-0">⚠</span>
                          <span>{risk}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Evidence Citations */}
                {agent.evidence_citations.length > 0 && (
                  <div className="pt-2 border-t border-border/60 space-y-2">
                    <span className="font-mono text-[10px] font-bold uppercase tracking-wider text-muted-foreground block">
                      Document Evidence Grounding
                    </span>
                    <div className="space-y-2">
                      {agent.evidence_citations.map((cit, idx) => (
                        <div
                          key={idx}
                          onClick={() => onSelectEvidence && onSelectEvidence(cit)}
                          className="group p-3 rounded-xl bg-background/60 hover:bg-background border border-border/60 hover:border-primary/50 cursor-pointer transition-all space-y-1.5 shadow-2xs"
                        >
                          <div className="flex items-center justify-between text-[10px]">
                            <span className="font-mono font-bold uppercase tracking-wide px-1.5 py-0.5 rounded bg-primary/10 text-primary border border-primary/30">
                              {cit.document_type}
                            </span>
                            <span className="text-muted-foreground group-hover:text-primary transition-colors">
                              Trace in Repository →
                            </span>
                          </div>
                          <p className="italic font-mono text-[11px] text-foreground/90 bg-muted/20 p-2 rounded border border-border/40 leading-relaxed">
                            &quot;{cit.quote}&quot;
                          </p>
                          <p className="text-[11px] text-muted-foreground">{cit.relevance_explanation}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Step-by-Step Reasoning Toggle */}
                <div className="pt-2 border-t border-border/60">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-full text-xs h-8 text-muted-foreground hover:text-foreground justify-between"
                    onClick={() => setExpandedAgent(isExpanded ? null : agent.agent_type)}
                  >
                    <span>{isExpanded ? "Hide Step-by-Step Reasoning" : "View Step-by-Step Reasoning"}</span>
                    <span className="font-mono text-[10px]">{isExpanded ? "▲" : "▼"}</span>
                  </Button>
                  {isExpanded && (
                    <div className="mt-2 p-3.5 rounded-xl bg-background/80 border border-border/80 text-[11px] font-mono whitespace-pre-wrap text-foreground/80 max-h-48 overflow-y-auto leading-relaxed">
                      {agent.raw_reasoning}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
