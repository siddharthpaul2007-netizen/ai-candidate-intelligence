"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { CandidateDocument } from "@/types/evaluation";

interface Props {
  evaluationId: number | null;
  documents: CandidateDocument[];
  onUploadSuccess: () => void;
  onRunDemo: (candidate?: string) => void;
  onRunProcessing: (evalId?: number) => void;
  onCreateEvaluation: () => Promise<number | null>;
  isProcessing: boolean;
}

// ── Sub-component: mode toggle (File / Paste) at module scope ──
const ModeToggle = ({
  mode,
  onChange,
}: { mode: "file" | "text"; onChange: (m: "file" | "text") => void }) => (
  <div className="flex items-center bg-muted/40 p-0.5 rounded-lg border border-border/80 text-[11px] font-medium">
    <button
      type="button"
      onClick={() => onChange("text")}
      className={`px-3 py-1 rounded-md transition-all ${
        mode === "text"
          ? "bg-foreground text-background font-semibold shadow-xs"
          : "text-muted-foreground hover:text-foreground"
      }`}
    >
      Paste Text
    </button>
    <button
      type="button"
      onClick={() => onChange("file")}
      className={`px-3 py-1 rounded-md transition-all ${
        mode === "file"
          ? "bg-foreground text-background font-semibold shadow-xs"
          : "text-muted-foreground hover:text-foreground"
      }`}
    >
      Upload File
    </button>
  </div>
);

export const DocumentUploadModal: React.FC<Props> = ({
  documents,
  onRunDemo,
  onRunProcessing,
  onCreateEvaluation,
  isProcessing,
}) => {
  const [selectedCandidate, setSelectedCandidate] = useState<string>("custom");

  const [jdMode, setJdMode] = useState<"file" | "text">("text");
  const [jdText, setJdText] = useState<string>("");
  const [jdFile, setJdFile] = useState<File | null>(null);

  const [resumeMode, setResumeMode] = useState<"file" | "text">("text");
  const [resumeText, setResumeText] = useState<string>("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);

  const [transcriptMode, setTranscriptMode] = useState<"file" | "text">("text");
  const [transcriptText, setTranscriptText] = useState<string>("");
  const [transcriptFile, setTranscriptFile] = useState<File | null>(null);

  const [uploading, setUploading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [statusMsg, setStatusMsg] = useState<string>("");

  const handleStartEvaluation = async () => {
    setError("");
    setStatusMsg("");

    if (selectedCandidate === "A" || selectedCandidate === "B") {
      onRunDemo(selectedCandidate);
      return;
    }

    const hasJd = (jdMode === "file" && jdFile) || (jdMode === "text" && jdText.trim());
    const hasResume = (resumeMode === "file" && resumeFile) || (resumeMode === "text" && resumeText.trim());
    const hasTranscript = (transcriptMode === "file" && transcriptFile) || (transcriptMode === "text" && transcriptText.trim());

    if (!hasJd || !hasResume || !hasTranscript) {
      setError("All three inputs are required: 1. Job Description, 2. Candidate Resume, and 3. Interview Transcript.");
      return;
    }

    setUploading(true);
    try {
      setStatusMsg("Creating new evaluation session…");
      const freshEvalId = await onCreateEvaluation();
      if (!freshEvalId) {
        setError("Failed to create a new evaluation session. Please try again.");
        return;
      }

      setStatusMsg("Uploading Job Description…");
      const formDataJd = new FormData();
      formDataJd.append("doc_type", "job_description");
      if (jdMode === "file" && jdFile) formDataJd.append("file", jdFile);
      else formDataJd.append("text_content", jdText);
      const jdRes = await fetch(`http://127.0.0.1:8000/api/evaluations/${freshEvalId}/upload`, { method: "POST", body: formDataJd });
      if (!jdRes.ok) throw new Error("Failed to upload Job Description");

      setStatusMsg("Uploading Resume…");
      const formDataResume = new FormData();
      formDataResume.append("doc_type", "resume");
      if (resumeMode === "file" && resumeFile) formDataResume.append("file", resumeFile);
      else formDataResume.append("text_content", resumeText);
      const resumeRes = await fetch(`http://127.0.0.1:8000/api/evaluations/${freshEvalId}/upload`, { method: "POST", body: formDataResume });
      if (!resumeRes.ok) throw new Error("Failed to upload Resume");

      setStatusMsg("Uploading Interview Transcript…");
      const formDataTranscript = new FormData();
      formDataTranscript.append("doc_type", "transcript");
      if (transcriptMode === "file" && transcriptFile) formDataTranscript.append("file", transcriptFile);
      else formDataTranscript.append("text_content", transcriptText);
      const transcriptRes = await fetch(`http://127.0.0.1:8000/api/evaluations/${freshEvalId}/upload`, { method: "POST", body: formDataTranscript });
      if (!transcriptRes.ok) throw new Error("Failed to upload Interview Transcript");

      setStatusMsg("Running multi-agent evaluation pipeline…");
      onRunProcessing(freshEvalId);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Upload error";
      setError(msg);
    } finally {
      setUploading(false);
      setStatusMsg("");
    }
  };

  return (
    <div className="space-y-6">

      {/* ── Source Selection Cards ── */}
      <div className="rounded-2xl border border-border/80 bg-card/90 backdrop-blur-sm p-6 space-y-4 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border/60 pb-3">
          <div>
            <h3 className="text-sm font-bold text-foreground">Select Evaluation Data Source</h3>
            <p className="text-xs text-muted-foreground">Choose a verified challenge preset or upload custom candidate documents.</p>
          </div>
          <span className="text-[11px] font-mono text-muted-foreground">3 Documents Required</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
          {/* Custom Upload Card */}
          <button
            type="button"
            onClick={() => setSelectedCandidate("custom")}
            className={`text-left p-4 rounded-xl border transition-all relative ${
              selectedCandidate === "custom"
                ? "border-primary/80 bg-primary/10 ring-2 ring-primary/20 shadow-xs"
                : "border-border/80 bg-background/50 hover:bg-muted/30 hover:border-border"
            }`}
          >
            <div className="flex items-start justify-between gap-2 mb-2">
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${selectedCandidate === "custom" ? "bg-primary animate-pulse" : "bg-muted"}`} />
                <span className="text-xs font-bold text-foreground">Custom Candidate Upload</span>
              </div>
              <Badge variant="outline" className="text-[10px] border-primary/40 text-primary">Custom</Badge>
            </div>
            <p className="text-[11px] text-muted-foreground leading-relaxed">
              Upload or paste Job Description, Resume, and Interview Transcript for your own candidate.
            </p>
          </button>

          {/* Demo A Card */}
          <button
            type="button"
            onClick={() => setSelectedCandidate("A")}
            className={`text-left p-4 rounded-xl border transition-all relative ${
              selectedCandidate === "A"
                ? "border-emerald-500/80 bg-emerald-500/10 ring-2 ring-emerald-500/20 shadow-xs"
                : "border-border/80 bg-background/50 hover:bg-muted/30 hover:border-border"
            }`}
          >
            <div className="flex items-start justify-between gap-2 mb-2">
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${selectedCandidate === "A" ? "bg-emerald-400 animate-pulse" : "bg-muted"}`} />
                <span className="text-xs font-bold text-foreground">Demo A: Alex Vance</span>
              </div>
              <Badge variant="outline" className="text-[10px] border-emerald-500/40 text-emerald-400">Strong Fit</Badge>
            </div>
            <p className="text-[11px] text-muted-foreground leading-relaxed">
              4 yrs exp. Verified async FastAPI microservices and latency optimization in transcript.
            </p>
          </button>

          {/* Demo B Card */}
          <button
            type="button"
            onClick={() => setSelectedCandidate("B")}
            className={`text-left p-4 rounded-xl border transition-all relative ${
              selectedCandidate === "B"
                ? "border-amber-500/80 bg-amber-500/10 ring-2 ring-amber-500/20 shadow-xs"
                : "border-border/80 bg-background/50 hover:bg-muted/30 hover:border-border"
            }`}
          >
            <div className="flex items-start justify-between gap-2 mb-2">
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${selectedCandidate === "B" ? "bg-amber-400 animate-pulse" : "bg-muted"}`} />
                <span className="text-xs font-bold text-foreground">Demo B: Jordan Lee</span>
              </div>
              <Badge variant="outline" className="text-[10px] border-amber-500/40 text-amber-400">Risk Gap</Badge>
            </div>
            <p className="text-[11px] text-muted-foreground leading-relaxed">
              6 yrs lead title. Resume claims 10M scale, but interview transcript reveals hands-off management.
            </p>
          </button>
        </div>
      </div>

      {/* ── Custom 3-Document Input Dossier ── */}
      {selectedCandidate === "custom" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-mono uppercase tracking-wider text-muted-foreground font-semibold">
              Required Document Dossier (3 Inputs)
            </h4>
            <span className="text-[11px] text-muted-foreground">Supported formats: PDF, DOCX, TXT or Direct Text</span>
          </div>

          {/* 01 Job Description */}
          <div className="rounded-xl border border-border/80 bg-card/90 p-4 space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2.5">
                <span className="font-mono text-xs font-black px-2 py-0.5 rounded-md bg-blue-500/15 border border-blue-500/30 text-blue-400">
                  01
                </span>
                <div>
                  <span className="text-xs font-bold text-foreground">Job Description</span>
                  <span className="text-[11px] text-muted-foreground ml-2 hidden sm:inline">
                    Position specifications, mandatory skills & responsibilities
                  </span>
                </div>
              </div>
              <ModeToggle mode={jdMode} onChange={setJdMode} />
            </div>

            {jdMode === "file" ? (
              <Input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={(e) => setJdFile(e.target.files?.[0] || null)}
                className="h-10 text-xs bg-background/60"
              />
            ) : (
              <textarea
                rows={3}
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                placeholder="Paste Job Description specifications, mandatory technical requirements, and core responsibilities…"
                className="w-full rounded-lg border border-input bg-background/60 p-3 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary leading-relaxed"
              />
            )}
          </div>

          {/* 02 Candidate Resume */}
          <div className="rounded-xl border border-border/80 bg-card/90 p-4 space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2.5">
                <span className="font-mono text-xs font-black px-2 py-0.5 rounded-md bg-indigo-500/15 border border-indigo-500/30 text-indigo-400">
                  02
                </span>
                <div>
                  <span className="text-xs font-bold text-foreground">Candidate Resume / CV</span>
                  <span className="text-[11px] text-muted-foreground ml-2 hidden sm:inline">
                    Work history, technical skills, and educational background
                  </span>
                </div>
              </div>
              <ModeToggle mode={resumeMode} onChange={setResumeMode} />
            </div>

            {resumeMode === "file" ? (
              <Input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                className="h-10 text-xs bg-background/60"
              />
            ) : (
              <textarea
                rows={3}
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste candidate resume content including work experience, skill breakdown, and accomplishments…"
                className="w-full rounded-lg border border-input bg-background/60 p-3 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary leading-relaxed"
              />
            )}
          </div>

          {/* 03 Interview Transcript */}
          <div className="rounded-xl border border-border/80 bg-card/90 p-4 space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2.5">
                <span className="font-mono text-xs font-black px-2 py-0.5 rounded-md bg-violet-500/15 border border-violet-500/30 text-violet-400">
                  03
                </span>
                <div>
                  <span className="text-xs font-bold text-foreground">Interview Transcript</span>
                  <span className="text-[11px] text-muted-foreground ml-2 hidden sm:inline">
                    Technical Q&A responses and dialogue transcript
                  </span>
                </div>
              </div>
              <ModeToggle mode={transcriptMode} onChange={setTranscriptMode} />
            </div>

            {transcriptMode === "file" ? (
              <Input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={(e) => setTranscriptFile(e.target.files?.[0] || null)}
                className="h-10 text-xs bg-background/60"
              />
            ) : (
              <textarea
                rows={3}
                value={transcriptText}
                onChange={(e) => setTranscriptText(e.target.value)}
                placeholder="Paste technical interview transcript with candidate dialogue, Q&A responses, and architectural answers…"
                className="w-full rounded-lg border border-input bg-background/60 p-3 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary leading-relaxed"
              />
            )}
          </div>
        </div>
      )}

      {/* ── Start Action Bar ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl border border-border/80 bg-card/90 backdrop-blur-sm shadow-sm">
        <div className="text-xs text-muted-foreground">
          {selectedCandidate === "A" && (
            <span>Evaluating <strong className="text-foreground">Candidate A (Alex Vance)</strong> — Strong fit with verified async FastAPI skills.</span>
          )}
          {selectedCandidate === "B" && (
            <span>Evaluating <strong className="text-foreground">Candidate B (Jordan Lee)</strong> — Adversarial test testing resume vs transcript gap.</span>
          )}
          {selectedCandidate === "custom" && (
            <span>Will create an isolated evaluation, parse all 3 inputs, and trigger the 4-agent debate consensus pipeline.</span>
          )}
        </div>

        <Button
          size="lg"
          onClick={handleStartEvaluation}
          disabled={isProcessing || uploading}
          className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs px-8 h-10 shadow-sm shrink-0 transition-all"
        >
          {isProcessing || uploading ? (
            <span className="flex items-center gap-2">
              <span className="h-3.5 w-3.5 rounded-full border-2 border-white/30 border-t-white animate-spin" />
              Running Multi-Agent Pipeline…
            </span>
          ) : (
            "⚡ Start Multi-Agent Evaluation"
          )}
        </Button>
      </div>

      {/* Status or Error Notifications */}
      {statusMsg && (
        <div className="text-xs text-blue-400 bg-blue-500/10 border border-blue-500/30 rounded-xl px-4 py-3 font-medium animate-pulse">
          {statusMsg}
        </div>
      )}
      {error && (
        <div className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/30 rounded-xl px-4 py-3 font-medium">
          {error}
        </div>
      )}

      {/* ── Parsed Documents Repository ── */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between">
          <h4 className="text-xs font-mono uppercase tracking-wider text-muted-foreground font-semibold">
            Parsed Documents in Active Session ({documents.length})
          </h4>
          <span className="text-[11px] text-muted-foreground font-mono">Isolated Context Preserved</span>
        </div>

        {documents.length === 0 ? (
          <div className="p-8 rounded-xl border border-dashed border-border/80 text-center text-xs text-muted-foreground bg-card/30">
            No documents in the current session. Choose a demo preset or upload your 3 custom documents to begin.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
            {documents.map((doc, idx) => {
              const isJd = doc.doc_type.toLowerCase().includes("job_description") || doc.doc_type.toLowerCase() === "jd";
              const isResume = doc.doc_type.toLowerCase().includes("resume") || doc.doc_type.toLowerCase() === "cv";
              const isTranscript = doc.doc_type.toLowerCase().includes("transcript");

              const badgeColor = isJd
                ? "border-blue-500/40 text-blue-400 bg-blue-500/10"
                : isResume
                ? "border-indigo-500/40 text-indigo-400 bg-indigo-500/10"
                : isTranscript
                ? "border-purple-500/40 text-purple-400 bg-purple-500/10"
                : "border-border text-foreground";

              return (
                <div key={idx} className="p-4 rounded-xl border border-border/80 bg-card/80 space-y-2.5 shadow-xs">
                  <div className="flex items-center justify-between">
                    <Badge variant="outline" className={`text-[10px] uppercase font-mono ${badgeColor}`}>
                      {doc.doc_type.replace("_", " ").toUpperCase()}
                    </Badge>
                    <span className="text-[10px] text-muted-foreground font-mono">Parsed ✓</span>
                  </div>
                  <div className="font-semibold text-xs text-foreground truncate">{doc.filename}</div>
                  <p className="text-[11px] text-muted-foreground italic font-mono bg-background/60 p-2.5 rounded-lg border border-border/40 line-clamp-3 leading-relaxed">
                    &quot;{doc.content_text.slice(0, 180)}…&quot;
                  </p>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
