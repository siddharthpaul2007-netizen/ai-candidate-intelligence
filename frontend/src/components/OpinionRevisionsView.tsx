"use client";

import React from "react";
import { Badge } from "@/components/ui/badge";
import { OpinionRevision } from "@/types/evaluation";

interface Props {
  revisions: OpinionRevision[];
}

const AGENT_BORDER: Record<string, string> = {
  technical: "border-l-blue-500",
  hiring_manager: "border-l-emerald-500",
  hr_culture: "border-l-violet-500",
  skeptic: "border-l-rose-500",
};

export const OpinionRevisionsView: React.FC<Props> = ({ revisions }) => {
  if (!revisions || revisions.length === 0) {
    return (
      <div className="p-12 text-center border border-dashed border-border/80 rounded-2xl bg-card/40 text-xs text-muted-foreground">
        No post-debate opinion revisions recorded. Run an evaluation session to see stance transformations.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-foreground">Post-Debate Opinion Revisions</h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            Tracks original evaluator stances versus revised positions following adversarial challenges.
          </p>
        </div>
        <Badge variant="outline" className="text-[10px] font-mono text-muted-foreground">
          {revisions.filter((r) => r.opinion_changed).length} Revisions Shifted
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {revisions.map((rev, idx) => {
          const delta = rev.revised_score - rev.previous_score;
          const deltaAbs = Math.abs(delta);
          const deltaSign = delta > 0 ? "▲ +" : delta < 0 ? "▼ -" : "— ";
          const deltaCls = delta > 0 ? "text-emerald-400" : delta < 0 ? "text-rose-400" : "text-muted-foreground";
          const borderCls = AGENT_BORDER[rev.agent_type] ?? "border-l-border";

          return (
            <div
              key={idx}
              className={`rounded-2xl border border-border/80 bg-card/90 backdrop-blur-sm border-l-4 ${borderCls} p-5 space-y-4 shadow-sm`}
            >
              {/* Header */}
              <div className="flex items-center justify-between border-b border-border/60 pb-3">
                <div className="font-bold text-sm text-foreground capitalize">
                  {rev.agent_type.replace(/_/g, " ")} Evaluator Stance
                </div>
                {rev.opinion_changed ? (
                  <Badge className="bg-amber-500/15 border-amber-500/40 text-amber-400 font-mono text-[10px]">
                    ● Opinion Shifted Post-Debate
                  </Badge>
                ) : (
                  <Badge variant="outline" className="text-[10px] font-mono text-muted-foreground">
                    Position Maintained
                  </Badge>
                )}
              </div>

              {/* Before -> After Transformation Block */}
              <div className="flex items-center justify-between p-4 rounded-xl bg-background/60 border border-border/60">
                {/* Initial Stance */}
                <div className="space-y-1 text-center flex-1">
                  <div className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
                    Initial Score
                  </div>
                  <div className="text-xl font-black font-mono text-foreground">
                    {rev.previous_score.toFixed(1)}
                  </div>
                  <div className="text-[10px] font-mono text-muted-foreground">
                    {rev.previous_recommendation.replace(/_/g, " ")}
                  </div>
                </div>

                {/* Arrow / Shift Delta */}
                <div className="px-4 text-center shrink-0">
                  <div className={`text-xs font-mono font-bold ${deltaCls}`}>
                    {deltaSign}{deltaAbs > 0 ? deltaAbs.toFixed(1) : ""}
                  </div>
                  <div className="text-muted-foreground text-xs">➔</div>
                </div>

                {/* Revised Stance */}
                <div className="space-y-1 text-center flex-1">
                  <div className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
                    Revised Score
                  </div>
                  <div className={`text-xl font-black font-mono ${rev.opinion_changed ? "text-amber-400" : "text-foreground"}`}>
                    {rev.revised_score.toFixed(1)}
                  </div>
                  <div className="text-[10px] font-mono text-foreground font-semibold">
                    {rev.revised_recommendation.replace(/_/g, " ")}
                  </div>
                </div>
              </div>

              {/* Shift Justification */}
              <div className="space-y-1.5">
                <span className="font-mono text-[10px] font-bold uppercase tracking-wider text-muted-foreground block">
                  Post-Debate Stance Justification
                </span>
                <p className="text-xs text-foreground/90 italic leading-relaxed bg-background/60 p-3 rounded-xl border border-border/40">
                  &quot;{rev.shift_justification}&quot;
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
