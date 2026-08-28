"use client";

import React from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CandidateProfile, FinalDecision } from "@/types/evaluation";

interface Props {
  profile: CandidateProfile | null;
  finalDecision: FinalDecision | null;
  positionTitle: string;
  onSelectDemoA?: () => void;
  onSelectDemoB?: () => void;
  onSwitchToUpload?: () => void;
}

const REC_CONFIG: Record<string, { label: string; badgeCls: string; barCls: string; strokeCls: string; sub: string }> = {
  STRONG_HIRE:  {
    label: "STRONG HIRE",
    badgeCls: "bg-emerald-500/15 border-emerald-500/40 text-emerald-400 shadow-xs shadow-emerald-500/10",
    barCls: "bg-emerald-500",
    strokeCls: "stroke-emerald-500",
    sub: "High Consensus · Verified Technical Depth",
  },
  HIRE: {
    label: "HIRE",
    badgeCls: "bg-green-500/15 border-green-500/40 text-green-400",
    barCls: "bg-green-500",
    strokeCls: "stroke-green-500",
    sub: "Consensus Approved · Low Risk",
  },
  LEAN_HIRE: {
    label: "LEAN HIRE",
    badgeCls: "bg-amber-500/15 border-amber-500/40 text-amber-400",
    barCls: "bg-amber-500",
    strokeCls: "stroke-amber-500",
    sub: "Conditional Consensus · Verify Metrics",
  },
  LEAN_NO_HIRE: {
    label: "LEAN NO HIRE",
    badgeCls: "bg-orange-500/15 border-orange-500/40 text-orange-400",
    barCls: "bg-orange-500",
    strokeCls: "stroke-orange-500",
    sub: "Critical Gaps Detected · Execution Concerns",
  },
  NO_HIRE: {
    label: "NO HIRE",
    badgeCls: "bg-rose-500/15 border-rose-500/40 text-rose-400 shadow-xs shadow-rose-500/10",
    barCls: "bg-rose-500",
    strokeCls: "stroke-rose-500",
    sub: "Adversarial Consensus · Mismatched Mandate",
  },
  PENDING: {
    label: "EVALUATION IN PROGRESS",
    badgeCls: "bg-muted/40 border-border text-muted-foreground",
    barCls: "bg-muted",
    strokeCls: "stroke-muted",
    sub: "Awaiting Pipeline Completion",
  },
};

export const CandidateHeader: React.FC<Props> = ({
  profile,
  finalDecision,
  positionTitle,
  onSelectDemoA,
  onSelectDemoB,
  onSwitchToUpload,
}) => {
  const score = finalDecision?.consensus_score ?? 0;
  const recKey = finalDecision?.final_recommendation ?? "PENDING";
  const rec = REC_CONFIG[recKey] ?? REC_CONFIG.PENDING;
  const pct = Math.min(100, Math.max(0, Math.round(score * 10)));

  // Elegant empty-state workspace hero
  if (!profile && !finalDecision) {
    return (
      <div className="relative overflow-hidden rounded-2xl border border-border/80 bg-gradient-to-br from-card/90 via-card/50 to-card/90 p-8 shadow-sm backdrop-blur-sm">
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2.5 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full border border-blue-500/30 bg-blue-500/10 text-blue-400 text-xs font-mono">
              <span>●</span> Autonomous Evaluation Engine Ready
            </div>
            <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-foreground">
              Adversarial Multi-Agent Candidate Intelligence
            </h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Synthesizes four isolated AI agents across <span className="text-foreground font-medium">Technical Rigor</span>, <span className="text-foreground font-medium">Business ROI</span>, <span className="text-foreground font-medium">HR/Culture</span>, and <span className="text-foreground font-medium">Adversarial Skeptic Audit</span> with citation-grounded debate.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto shrink-0">
            {onSelectDemoA && (
              <Button
                variant="outline"
                size="sm"
                onClick={onSelectDemoA}
                className="h-10 px-4 border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/10 font-semibold text-xs"
              >
                ⚡ Test Candidate A (Strong Fit)
              </Button>
            )}
            {onSelectDemoB && (
              <Button
                variant="outline"
                size="sm"
                onClick={onSelectDemoB}
                className="h-10 px-4 border-amber-500/40 text-amber-400 hover:bg-amber-500/10 font-semibold text-xs"
              >
                ⚡ Test Candidate B (Risk Pattern)
              </Button>
            )}
            {onSwitchToUpload && (
              <Button
                size="sm"
                onClick={onSwitchToUpload}
                className="h-10 px-5 bg-foreground text-background hover:bg-foreground/90 font-bold text-xs shadow-sm"
              >
                + Upload Custom Files
              </Button>
            )}
          </div>
        </div>

        {/* Workflow Feature Strip */}
        <div className="mt-8 pt-6 border-t border-border/60 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
          <div className="space-y-1">
            <span className="font-mono text-[10px] text-blue-400 font-bold uppercase tracking-wider block">01 · Isolated Evaluators</span>
            <p className="text-muted-foreground">4 agents evaluate candidate without context leakage</p>
          </div>
          <div className="space-y-1">
            <span className="font-mono text-[10px] text-rose-400 font-bold uppercase tracking-wider block">02 · Adversarial Skeptic</span>
            <p className="text-muted-foreground">Rigorous cross-checking of resume vs interview reality</p>
          </div>
          <div className="space-y-1">
            <span className="font-mono text-[10px] text-amber-400 font-bold uppercase tracking-wider block">03 · Debate & Revisions</span>
            <p className="text-muted-foreground">Agent stances challenged and iteratively refined</p>
          </div>
          <div className="space-y-1">
            <span className="font-mono text-[10px] text-emerald-400 font-bold uppercase tracking-wider block">04 · Dynamic Synthesis</span>
            <p className="text-muted-foreground">Continuous consensus score grounded in exact quotes</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-border/80 bg-card/90 backdrop-blur-sm overflow-hidden shadow-sm">
      {/* Top recommendation accent bar */}
      <div className="h-1 w-full bg-border">
        <div
          className={`h-full transition-all duration-700 ${rec.barCls}`}
          style={{ width: `${pct}%` }}
        />
      </div>

      <div className="p-6 space-y-6">
        {/* Candidate Title & Consensus Score Centerpiece */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-border/60">
          {/* Candidate Dossier Header */}
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-foreground">
                {profile?.candidate_name || "Candidate Evaluation"}
              </h1>
              <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold font-mono tracking-wide border ${rec.badgeCls}`}>
                <span>●</span> {rec.label}
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
              <span className="font-semibold text-foreground">{positionTitle}</span>
              <span className="text-border">|</span>
              <span>Experience: <strong className="text-foreground">{profile?.experience_years || "N/A"}</strong></span>
              <span className="text-border">|</span>
              <span className="text-emerald-400 font-medium">{rec.sub}</span>
            </div>
          </div>

          {/* Prominent Radial Consensus Score Widget */}
          {finalDecision && (
            <div className="flex items-center gap-4 bg-background/80 border border-border/80 rounded-xl px-5 py-3.5 shrink-0 shadow-inner">
              <div className="space-y-1">
                <div className="text-[10px] uppercase font-mono tracking-widest text-muted-foreground font-bold leading-none">
                  Consensus Score
                </div>
                <div className="flex items-baseline gap-1.5">
                  <span className="text-3xl md:text-4xl font-black text-foreground tracking-tight leading-none">
                    {score.toFixed(1)}
                  </span>
                  <span className="text-xs text-muted-foreground font-normal">/ 10</span>
                </div>
                <div className="text-[10px] font-mono text-muted-foreground">
                  Continuous multi-agent synthesis
                </div>
              </div>

              {/* High-definition Gauge */}
              <div className="w-16 h-16 relative flex items-center justify-center shrink-0">
                <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
                  <circle
                    cx="18"
                    cy="18"
                    r="14"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="3"
                    className="text-border/60"
                  />
                  <circle
                    cx="18"
                    cy="18"
                    r="14"
                    fill="none"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeDasharray={`${pct * 0.879} 87.96`}
                    className={`${rec.strokeCls} transition-all duration-700`}
                  />
                </svg>
                <span className="absolute text-[11px] font-mono font-bold text-foreground">
                  {pct}%
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Candidate Profile Details Grid */}
        {profile && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 text-sm">
            {/* Background Summary */}
            <div className="lg:col-span-2 space-y-2">
              <div className="text-[11px] uppercase font-mono tracking-wider text-muted-foreground font-semibold flex items-center gap-2">
                <span>Executive Dossier Summary</span>
              </div>
              <p className="text-foreground/90 leading-relaxed text-xs md:text-sm bg-muted/20 border border-border/40 p-4 rounded-xl">
                {profile.summary}
              </p>
            </div>

            {/* Education & Verified Skills */}
            <div className="space-y-4 lg:border-l lg:border-border/60 lg:pl-6">
              {profile.education_summary && (
                <div className="space-y-1">
                  <div className="text-[11px] uppercase font-mono tracking-wider text-muted-foreground font-semibold">
                    Education & Credentials
                  </div>
                  <p className="text-xs font-medium text-foreground bg-muted/30 p-2.5 rounded-lg border border-border/30">
                    {profile.education_summary}
                  </p>
                </div>
              )}

              {profile.skills_extracted.length > 0 && (
                <div className="space-y-2">
                  <div className="text-[11px] uppercase font-mono tracking-wider text-muted-foreground font-semibold">
                    Verified Core Skills ({profile.skills_extracted.length})
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {profile.skills_extracted.map((skill, idx) => (
                      <Badge
                        key={idx}
                        variant="secondary"
                        className="text-[11px] font-normal px-2.5 py-1 bg-muted/60 border border-border/50 text-foreground/90 hover:bg-muted"
                      >
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
