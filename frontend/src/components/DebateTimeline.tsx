"use client";

import React, { useState } from "react";
import { DebateMessage } from "@/types/evaluation";

interface Props {
  debateRounds: DebateMessage[];
}

function getAgentColor(name: string): { badge: string; text: string } {
  const n = name.toLowerCase();
  if (n.includes("technical")) return { badge: "border-blue-500/40 text-blue-400 bg-blue-500/10", text: "text-blue-400" };
  if (n.includes("skeptic")) return { badge: "border-rose-500/40 text-rose-400 bg-rose-500/10", text: "text-rose-400" };
  if (n.includes("hiring")) return { badge: "border-emerald-500/40 text-emerald-400 bg-emerald-500/10", text: "text-emerald-400" };
  if (n.includes("hr") || n.includes("culture")) return { badge: "border-violet-500/40 text-violet-400 bg-violet-500/10", text: "text-violet-400" };
  return { badge: "border-border text-foreground bg-muted/40", text: "text-foreground" };
}

export const DebateTimeline: React.FC<Props> = ({ debateRounds }) => {
  const [expandedAll, setExpandedAll] = useState<boolean>(true);

  if (!debateRounds || debateRounds.length === 0) {
    return (
      <div className="p-12 text-center border border-dashed border-border/80 rounded-2xl bg-card/40 text-xs text-muted-foreground">
        No adversarial debate exchanges generated. Execute an evaluation session to observe agent challenges.
      </div>
    );
  }

  // Group messages by round
  const rounds = debateRounds.reduce<Record<number, DebateMessage[]>>((acc, msg) => {
    acc[msg.round_number] = acc[msg.round_number] || [];
    acc[msg.round_number].push(msg);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-foreground">Multi-Agent Adversarial Debate & Disagreement Stage</h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            Inter-agent cross-examinations challenging assumptions and auditing metric validity.
          </p>
        </div>
        <button
          onClick={() => setExpandedAll(!expandedAll)}
          className="text-xs text-muted-foreground hover:text-foreground font-mono"
        >
          {expandedAll ? "Collapse Details" : "Expand All"}
        </button>
      </div>

      <div className="space-y-6">
        {Object.entries(rounds).map(([roundNum, messages]) => (
          <div key={roundNum} className="space-y-4">
            {/* Round Indicator */}
            <div className="flex items-center gap-3">
              <span className="font-mono text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full bg-primary/10 border border-primary/30 text-primary">
                Round {roundNum} Challenge Phase
              </span>
              <div className="h-px flex-1 bg-border/60" />
            </div>

            {/* Messages in this Round */}
            <div className="grid grid-cols-1 gap-4 pl-0 sm:pl-4 border-l-2 border-primary/20 space-y-2">
              {messages.map((msg, idx) => {
                const sender = getAgentColor(msg.sender_agent);
                const target = getAgentColor(msg.target_agent);

                return (
                  <div
                    key={msg.id ?? idx}
                    className="rounded-2xl border border-border/80 bg-card/90 backdrop-blur-sm p-5 space-y-4 shadow-xs"
                  >
                    {/* Interrogation Header */}
                    <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border/60 pb-3">
                      <div className="flex flex-wrap items-center gap-2 text-xs">
                        <span className={`font-mono font-bold px-2 py-0.5 rounded border ${sender.badge}`}>
                          {msg.sender_agent}
                        </span>
                        <span className="text-muted-foreground font-medium">interrogated</span>
                        <span className={`font-mono font-bold px-2 py-0.5 rounded border ${target.badge}`}>
                          {msg.target_agent}
                        </span>
                      </div>

                      {msg.in_response_to_id && (
                        <span className="text-[10px] font-mono text-muted-foreground bg-muted/40 px-2 py-0.5 rounded border border-border/40">
                          In reply to #{msg.in_response_to_id}
                        </span>
                      )}
                    </div>

                    {/* Challenge Point */}
                    <div className="space-y-1.5">
                      <span className="font-mono text-[10px] font-bold uppercase tracking-wider text-rose-400 block">
                        Adversarial Challenge Point
                      </span>
                      <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-foreground/90 leading-relaxed">
                        {msg.challenge_point}
                      </div>
                    </div>

                    {/* Response Argument */}
                    <div className="space-y-1.5">
                      <span className="font-mono text-[10px] font-bold uppercase tracking-wider text-blue-400 block">
                        Defense & Counter-Argument
                      </span>
                      <div className="p-3.5 rounded-xl bg-blue-500/10 border border-blue-500/30 text-xs text-foreground/90 leading-relaxed">
                        {msg.response_argument}
                      </div>
                    </div>

                    {/* Referenced Evidence Citations */}
                    {msg.evidence_references && msg.evidence_references.length > 0 && expandedAll && (
                      <div className="space-y-1.5 pt-2 border-t border-border/40">
                        <span className="font-mono text-[10px] font-bold uppercase tracking-wider text-muted-foreground block">
                          Referenced Document Citations
                        </span>
                        <div className="space-y-1.5">
                          {msg.evidence_references.map((ev, i) => (
                            <div
                              key={i}
                              className="p-2.5 rounded-lg bg-background/60 border border-border/40 text-[11px] font-mono text-foreground/80 space-y-1"
                            >
                              <span className="text-[9px] uppercase font-bold text-primary mr-2">
                                [{ev.document_type}]
                              </span>
                              <span className="italic">&quot;{ev.quote}&quot;</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
