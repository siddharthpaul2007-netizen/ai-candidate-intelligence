# AI Candidate Intelligence

> An evidence-grounded multi-agent AI system for structured candidate evaluation, debate, and hiring recommendations.

## Overview

AI Candidate Intelligence is a multi-agent candidate evaluation system designed to analyze a candidate's resume and transcript from multiple independent perspectives.

Instead of relying on a single AI evaluation, the system uses four specialized AI personas:

- **Technical Agent** — evaluates technical skills, depth, and technical evidence.
- **HR / Culture Agent** — evaluates communication, teamwork, professionalism, and behavioral evidence.
- **Hiring Manager Agent** — evaluates overall role fit and hiring suitability.
- **Skeptic Agent** — identifies contradictions, unsupported claims, exaggeration, and potential red flags.

Each agent first produces an **independent evaluation** without seeing the conclusions of the other agents. The agents then enter a structured debate where they can challenge, defend, or revise their positions.

A separate final reasoning stage considers the evidence, agent opinions, debate, confidence, and unresolved disagreements to produce the final recommendation.

---

## Core Workflow

```text
Resume + Transcript + Job Requirements
                  │
                  ▼
        ┌─────────────────────┐
        │ Candidate Profile   │
        │      Builder        │
        └──────────┬──────────┘
                   │
                   ▼
            Evidence Layer
                   │
                   ▼
       ┌───────────┼───────────┐
       │           │           │
       ▼           ▼           ▼
   Technical      HR       Hiring Manager
     Agent       Agent          Agent
       │           │             │
       └───────────┼─────────────┘
                   │
             Skeptic Agent
                   │
                   ▼
        Independent Opinions
                   │
                   ▼
            Debate Engine
                   │
                   ▼
          Opinion Revisions
                   │
                   ▼
          Final Decision Engine
                   │
                   ▼
             Final Report
