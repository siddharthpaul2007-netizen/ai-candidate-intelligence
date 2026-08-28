"use client";

import React, { useState } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { CandidateHeader } from "@/components/CandidateHeader";
import { AgentCards } from "@/components/AgentCards";
import { DebateTimeline } from "@/components/DebateTimeline";
import { OpinionRevisionsView } from "@/components/OpinionRevisionsView";
import { FinalDecisionPanel } from "@/components/FinalDecisionPanel";
import { DocumentUploadModal } from "@/components/DocumentUploadModal";
import { EvaluationData, EvidenceCitation } from "@/types/evaluation";

export default function Home() {
  const [data, setData] = useState<EvaluationData | null>(null);
  const [evaluationId, setEvaluationId] = useState<number | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<string>("documents");
  const [selectedCitation, setSelectedCitation] = useState<EvidenceCitation | null>(null);

  const loadDemoData = async (candidate: string = "A") => {
    setLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/evaluations/demo?candidate=${candidate}`, { method: "POST" });
      if (res.ok) {
        const json: EvaluationData = await res.json();
        setData(json);
        setEvaluationId(json.evaluation.id);
        setActiveTab("executive");
      }
    } catch (e) {
      console.error("Failed to load demo evaluation:", e);
    } finally {
      setLoading(false);
    }
  };

  const createNewEvaluation = async (): Promise<number | null> => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/evaluations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: "New Candidate Evaluation",
          position_title: "Senior Full-Stack Software Engineer"
        })
      });
      if (res.ok) {
        const evalObj = await res.json();
        setEvaluationId(evalObj.id);
        setData({
          evaluation: evalObj,
          documents: [],
          profile: null,
          findings: [],
          debate_rounds: [],
          revisions: [],
          final_decision: null
        });
        return evalObj.id;
      }
    } catch (e) {
      console.error("Failed to create evaluation:", e);
    }
    return null;
  };

  const runProcessing = async (overrideEvalId?: number) => {
    const evalId = overrideEvalId || evaluationId;
    if (!evalId) return;
    setLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/evaluations/${evalId}/process`, {
        method: "POST"
      });
      if (res.ok) {
        const updatedData: EvaluationData = await res.json();
        setData(updatedData);
        setEvaluationId(evalId);
        setActiveTab("executive");
      }
    } catch (e) {
      console.error("Failed to process evaluation:", e);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCitation = (citation: EvidenceCitation) => {
    setSelectedCitation(citation);
    setActiveTab("documents");
  };

  const hasResults = !!data?.profile;

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans">

      {/* ── Top Enterprise Navigation Bar ── */}
      <header className="sticky top-0 z-50 border-b border-border/80 bg-background/90 backdrop-blur-md px-6 py-3 transition-all">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
          {/* Workspace Branding */}
          <div className="flex items-center gap-3.5">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-zinc-700 via-zinc-800 to-zinc-950 border border-white/15 flex items-center justify-center shadow-inner shrink-0">
              <span className="text-xs font-black text-white tracking-wider font-mono">CI</span>
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <span className="font-bold text-sm tracking-tight text-foreground">
                  Candidate Intelligence Workspace
                </span>
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-mono font-medium border border-emerald-500/30 text-emerald-400 bg-emerald-500/10">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  System Active
                </span>
              </div>
              <p className="text-[11px] text-muted-foreground hidden sm:block">
                Multi-Agent Adversarial Consensus · Isolated Evaluators · Evidence Grounding
              </p>
            </div>
          </div>

          {/* Quick-load Challenge Presets */}
          <div className="flex items-center gap-2 shrink-0">
            <div className="hidden lg:flex items-center text-[11px] text-muted-foreground mr-1">
              Presets:
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => loadDemoData("A")}
              disabled={loading}
              className="text-xs h-8 px-3 border-border/80 bg-card/60 hover:bg-card hover:border-emerald-500/50 hover:text-emerald-300 transition-all font-medium"
            >
              {loading ? "Running…" : "Demo A (Alex Vance)"}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => loadDemoData("B")}
              disabled={loading}
              className="text-xs h-8 px-3 border-border/80 bg-card/60 hover:bg-card hover:border-amber-500/50 hover:text-amber-300 transition-all font-medium"
            >
              {loading ? "Running…" : "Demo B (Jordan Lee)"}
            </Button>
          </div>
        </div>
      </header>

      {/* ── Main Workspace ── */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 md:px-6 py-6 space-y-6">

        {/* Evaluation Pipeline Progress Banner */}
        {loading && (
          <div className="flex items-center justify-between gap-4 px-5 py-3 rounded-xl border border-primary/30 bg-primary/5 text-xs text-primary shadow-sm animate-pulse">
            <div className="flex items-center gap-3">
              <span className="h-4 w-4 rounded-full border-2 border-primary/30 border-t-primary animate-spin" />
              <span className="font-semibold">Executing Multi-Agent Evaluation & Adversarial Debate Pipeline…</span>
            </div>
            <span className="text-[11px] text-muted-foreground font-mono">Synthesizing 4 Isolated Evaluator Streams</span>
          </div>
        )}

        {/* Hero Candidate / Empty State Centerpiece */}
        <CandidateHeader
          profile={data?.profile || null}
          finalDecision={data?.final_decision || null}
          positionTitle={data?.evaluation?.position_title || "Senior Full-Stack Engineer"}
          onSelectDemoA={() => loadDemoData("A")}
          onSelectDemoB={() => loadDemoData("B")}
          onSwitchToUpload={() => setActiveTab("documents")}
        />

        {/* Workspace Segmented Navigation */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="h-11 w-full bg-card/80 backdrop-blur-sm border border-border/80 rounded-xl p-1 grid grid-cols-2 md:grid-cols-5 gap-1 shadow-xs">
            <TabsTrigger
              value="executive"
              className="h-full text-xs font-semibold rounded-lg data-[state=active]:bg-foreground/10 data-[state=active]:text-foreground data-[state=active]:shadow-xs transition-all flex items-center justify-center gap-1.5"
            >
              <span>Executive Synthesis</span>
              {data?.final_decision && (
                <span className="h-2 w-2 rounded-full bg-emerald-400" />
              )}
            </TabsTrigger>

            <TabsTrigger
              value="agents"
              className="h-full text-xs font-semibold rounded-lg data-[state=active]:bg-foreground/10 data-[state=active]:text-foreground data-[state=active]:shadow-xs transition-all flex items-center justify-center gap-1.5"
            >
              <span>4 Evaluators</span>
              {hasResults && (
                <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-muted text-muted-foreground font-mono">
                  {data?.findings.length}
                </span>
              )}
            </TabsTrigger>

            <TabsTrigger
              value="debate"
              className="h-full text-xs font-semibold rounded-lg data-[state=active]:bg-foreground/10 data-[state=active]:text-foreground data-[state=active]:shadow-xs transition-all flex items-center justify-center gap-1.5"
            >
              <span>Adversarial Debate</span>
              {hasResults && (
                <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-muted text-muted-foreground font-mono">
                  {data?.debate_rounds.length}
                </span>
              )}
            </TabsTrigger>

            <TabsTrigger
              value="revisions"
              className="h-full text-xs font-semibold rounded-lg data-[state=active]:bg-foreground/10 data-[state=active]:text-foreground data-[state=active]:shadow-xs transition-all flex items-center justify-center gap-1.5"
            >
              <span>Opinion Revisions</span>
              {hasResults && (
                <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-muted text-muted-foreground font-mono">
                  {data?.revisions.length}
                </span>
              )}
            </TabsTrigger>

            <TabsTrigger
              value="documents"
              className="h-full text-xs font-semibold rounded-lg data-[state=active]:bg-foreground/10 data-[state=active]:text-foreground data-[state=active]:shadow-xs transition-all flex items-center justify-center gap-1.5"
            >
              <span>Document Repository</span>
              {hasResults && (
                <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-muted text-muted-foreground font-mono">
                  {data?.documents.length}
                </span>
              )}
            </TabsTrigger>
          </TabsList>

          {/* Tab 1: Executive Synthesis */}
          <TabsContent value="executive" className="space-y-6 mt-0 outline-hidden">
            {!data?.final_decision ? (
              <div className="p-12 text-center border border-dashed border-border/80 rounded-xl bg-card/40 space-y-3">
                <div className="text-sm font-semibold text-foreground">No Evaluation Synthesized Yet</div>
                <p className="text-xs text-muted-foreground max-w-md mx-auto">
                  Run an evaluation on a candidate profile by selecting a pre-seeded demo or uploading custom Job Description, Resume, and Transcript documents.
                </p>
                <div className="pt-2 flex justify-center gap-3">
                  <Button size="sm" variant="outline" onClick={() => loadDemoData("A")}>Load Candidate A</Button>
                  <Button size="sm" onClick={() => setActiveTab("documents")}>Upload Documents</Button>
                </div>
              </div>
            ) : (
              <FinalDecisionPanel decision={data.final_decision} />
            )}
          </TabsContent>

          {/* Tab 2: Four Independent Evaluator Agents */}
          <TabsContent value="agents" className="space-y-6 mt-0 outline-hidden">
            <AgentCards
              findings={data?.findings || []}
              onSelectEvidence={handleSelectCitation}
            />
          </TabsContent>

          {/* Tab 3: Debate & Disagreements */}
          <TabsContent value="debate" className="space-y-6 mt-0 outline-hidden">
            <DebateTimeline debateRounds={data?.debate_rounds || []} />
          </TabsContent>

          {/* Tab 4: Opinion Revisions */}
          <TabsContent value="revisions" className="space-y-6 mt-0 outline-hidden">
            <OpinionRevisionsView revisions={data?.revisions || []} />
          </TabsContent>

          {/* Tab 5: Document Repository & Custom Upload */}
          <TabsContent value="documents" className="space-y-6 mt-0 outline-hidden">
            {selectedCitation && (
              <div className="p-4 rounded-xl border border-primary/40 bg-primary/10 space-y-2 shadow-sm animate-fadeIn">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-primary text-primary-foreground font-mono">
                      Selected Evidence Reference
                    </span>
                    <span className="text-xs font-semibold text-foreground capitalize">
                      Source: {selectedCitation.document_type}
                    </span>
                  </div>
                  <button
                    onClick={() => setSelectedCitation(null)}
                    className="text-xs text-muted-foreground hover:text-foreground px-2 py-1 rounded"
                  >
                    Dismiss Highlight ✕
                  </button>
                </div>
                <p className="text-xs italic font-mono bg-background/80 px-3.5 py-2.5 rounded-lg border border-border text-foreground leading-relaxed">
                  &quot;{selectedCitation.quote}&quot;
                </p>
                <p className="text-[11px] text-muted-foreground">{selectedCitation.relevance_explanation}</p>
              </div>
            )}

            <DocumentUploadModal
              evaluationId={evaluationId}
              documents={data?.documents || []}
              onUploadSuccess={() => runProcessing()}
              onRunDemo={loadDemoData}
              onRunProcessing={runProcessing}
              onCreateEvaluation={createNewEvaluation}
              isProcessing={loading}
            />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
