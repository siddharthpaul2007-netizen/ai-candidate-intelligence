"use client";

import React from "react";
import { Badge } from "@/components/ui/badge";
import { FinalDecision } from "@/types/evaluation";

interface Props {
  decision: FinalDecision | null;
}

const REC_META: Record<string, { label: string; bgCls: string; textCls: string; borderCls: string; barCls: string }> = {
  STRONG_HIRE:  { label: "STRONG HIRE",  bgCls: "bg-emerald-500/10", textCls: "text-emerald-400", borderCls: "border-emerald-500/40", barCls: "bg-emerald-500" },
  HIRE:         { label: "HIRE",          bgCls: "bg-green-500/10",   textCls: "text-green-400",   borderCls: "border-green-500/40",   barCls: "bg-green-500"   },
  LEAN_HIRE:    { label: "LEAN HIRE",     bgCls: "bg-amber-500/10",   textCls: "text-amber-400",   borderCls: "border-amber-500/40",   barCls: "bg-amber-500"   },
  LEAN_NO_HIRE: { label: "LEAN NO HIRE",  bgCls: "bg-orange-500/10",  textCls: "text-orange-400",  borderCls: "border-orange-500/40",  barCls: "bg-orange-500"  },
  NO_HIRE:      { label: "NO HIRE",       bgCls: "bg-rose-500/10",    textCls: "text-rose-400",    borderCls: "border-rose-500/40",    barCls: "bg-rose-500"    },
};

export const FinalDecisionPanel: React.FC<Props> = ({ decision }) => {
  if (!decision) return null;

  const recKey = decision.final_recommendation;
  const meta = REC_META[recKey] ?? {
    label: recKey,
    bgCls: "bg-muted/20",
    textCls: "text-foreground",
    borderCls: "border-border",
    barCls: "bg-muted",
  };
  const pct = Math.min(100, Math.max(0, Math.round(decision.consensus_score * 10)));

  return (
    <div className="space-y-6">

      {/* ── Hero Executive Recommendation Banner ── */}
      <div className={`rounded-2xl border ${meta.borderCls} ${meta.bgCls} p-6 shadow-sm backdrop-blur-sm relative overflow-hidden`}>
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded border border-primary/40 bg-primary/10 text-primary">
                Executive Synthesis Stage
              </span>
              <span className={`text-xs font-mono font-bold px-2.5 py-0.5 rounded-full border ${meta.borderCls} ${meta.textCls}`}>
                {meta.label}
              </span>
            </div>

            <h2 className="text-xl md:text-2xl font-extrabold tracking-tight text-foreground">
              Multi-Agent Executive Hiring Consensus
            </h2>
            <p className="text-xs md:text-sm text-foreground/80 leading-relaxed">
              {decision.synthesis_summary}
            </p>
          </div>

          {/* Consensus Score Block */}
          <div className="shrink-0 bg-background/80 border border-border/80 rounded-xl p-5 text-right space-y-1.5 shadow-inner">
            <div className="text-[10px] uppercase font-mono tracking-widest text-muted-foreground font-bold leading-none">
              Synthesized Score
            </div>
            <div className="flex items-baseline justify-end gap-1.5">
              <span className={`text-4xl md:text-5xl font-black leading-none ${meta.textCls}`}>
                {decision.consensus_score.toFixed(1)}
              </span>
              <span className="text-sm text-muted-foreground font-normal">/ 10</span>
            </div>
            <div className="h-1.5 w-36 bg-border/80 rounded-full overflow-hidden ml-auto">
              <div className={`h-full rounded-full ${meta.barCls}`} style={{ width: `${pct}%` }} />
            </div>
            <div className="text-[10px] font-mono text-muted-foreground pt-0.5">
              Evidence & Debate Weighted
            </div>
          </div>
        </div>
      </div>

      {/* ── Evidence-Grounded Core Justification ── */}
      <div className="rounded-2xl border border-border/80 bg-card/90 backdrop-blur-sm p-6 space-y-3 shadow-sm">
        <div className="flex items-center justify-between">
          <h4 className="text-xs font-mono uppercase tracking-wider text-muted-foreground font-semibold flex items-center gap-2">
            <span>Evidence-Grounded Consensus Justification</span>
          </h4>
          <span className="text-[11px] text-muted-foreground font-mono">Consensus Derivation</span>
        </div>
        <div className="p-4 rounded-xl bg-background/60 border border-border/60 text-xs md:text-sm text-foreground/90 font-mono leading-relaxed">
          {decision.core_justification}
        </div>
      </div>

      {/* ── Disagreement Matrix & Key Tradeoffs ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Disagreement Matrix */}
        <div className="rounded-2xl border border-border/80 bg-card/90 backdrop-blur-sm p-6 space-y-4 shadow-sm">
          <div className="flex items-center justify-between border-b border-border/60 pb-3">
            <h4 className="text-xs font-mono uppercase tracking-wider text-muted-foreground font-semibold">
              Disagreement Resolution Matrix
            </h4>
            <Badge variant="outline" className="text-[10px] font-mono border-blue-500/40 text-blue-400">
              Resolved & Audited
            </Badge>
          </div>

          <div className="space-y-3 text-xs">
            {Object.entries(decision.disagreement_matrix || {}).map(([key, val], idx) => (
              <div key={idx} className="p-3.5 rounded-xl bg-background/60 border border-border/60 space-y-1">
                <span className="font-mono font-bold text-primary block text-[11px] capitalize tracking-wide">
                  {key.replace(/_/g, " ")}
                </span>
                <p className="text-muted-foreground text-xs leading-relaxed">{val}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Key Tradeoffs */}
        <div className="rounded-2xl border border-border/80 bg-card/90 backdrop-blur-sm p-6 space-y-4 shadow-sm">
          <div className="flex items-center justify-between border-b border-border/60 pb-3">
            <h4 className="text-xs font-mono uppercase tracking-wider text-muted-foreground font-semibold">
              Key Hiring Tradeoffs
            </h4>
            <Badge variant="outline" className="text-[10px] font-mono border-amber-500/40 text-amber-400">
              Executive Review
            </Badge>
          </div>

          <ul className="space-y-3 text-xs">
            {(decision.key_tradeoffs || []).map((tradeoff, idx) => (
              <li key={idx} className="flex items-start gap-3 p-3.5 rounded-xl bg-background/60 border border-border/60">
                <span className="text-amber-400 text-sm font-bold shrink-0 mt-0.5">⚖</span>
                <span className="text-foreground/90 leading-relaxed text-xs">{tradeoff}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};
