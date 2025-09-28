# OSINT Framework

A TDD-friendly scaffold for a web scraping + AI analysis platform designed for Open Source Intelligence (OSINT) research.

## 🤖 AI-Assisted Development

This project is designed to work seamlessly with **Claude Code** for AI-assisted development:

- **Structured Planning**: Complete project planning framework with PRDs, design docs, and user stories
- **Claude-Ready Tasks**: Granular task breakdowns that Claude can execute independently
- **Test-Driven Development**: Built-in TDD approach with pytest and Playwright testing
- **Documentation-First**: Human and machine-readable documentation structure

### Working with Claude

The project includes a complete workflow for AI-assisted development:

1. **Planning Layer** (`/planning/`): Machine-friendly task lists and user stories
2. **Documentation** (`/docs/`): Human-readable design and product requirements
3. **Execution**: Give Claude specific story links and let it work autonomously
4. **Traceability**: Built-in templates ensure all decisions are documented

## Stack
- **Backend:** Django + Django REST Framework + pytest
- **Workers:** Celery + Redis (placeholders)
- **DB:** Postgres (psycopg placeholder)
- **E2E:** Playwright (Node) for UI & flow tests
- **CI:** GitHub Actions runs pytest and Playwright

> Start by pushing this repo to GitHub, then open issues using the included templates.


## Quick start

```bash
# Backend (dev)
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .[dev]
uvicorn app.main:app --reload

# Run tests
pytest -q

# Frontend E2E (requires Node 18+)
cd ../frontend
npm install
npx playwright install
npx playwright test
```

Where everything goes (repo layout)

Use docs at the root (not inside src). If you ever add code later, it can live in src/ or packages/, but your planning layer is separate and stable.

/docs/                 ← human-readable source of truth
  /product/            ← PRDs (problem → users → success metrics)
  /design/             ← architecture/design docs & ADRs
  /rfcs/               ← proposals needing review/decision
  /runbooks/           ← ops/how-to, “how to run X locally”
  /qa/                 ← test plans, acceptance criteria
  /glossary.md         ← shared terms

/planning/             ← machine-friendly planning
  roadmap.md           ← quarter/epic goals
  backlog.md           ← prioritized list with links to stories
  stories/             ← one file per user story (short)
  tasks/               ← granular task lists/checklists
  release-notes/       ← what shipped this week

/standards/
  conventions.md       ← naming, labels, branching, commit style
  architecture.md      ← system overview diagram + principles

# (optional later)
/src/                  ← code (or /packages/<service>/src in a monorepo)
/scripts/              ← helper scripts if you add automation someday


TL;DR: docs/ is for thinking/deciding; planning/ is for execution units Claude can consume; src/ (if/when it exists) is for code.

Workflow (end-to-end)

Idea → PRD → Design → Stories → Issues → Execution

Write the PRD (/docs/product/<project>.md)
Keep it short: problem, users, scope, success metrics, out-of-scope.

Write the Design (/docs/design/<project>.md)
High-level architecture, constraints, alternatives, risks, and a “work breakdown” section that mirrors the stories you’ll create.

Author the Stories (one file per story in /planning/stories/)
Each story is small, with acceptance criteria and a “definition of done.”

Break down into Tasks (/planning/tasks/<story-id>.md)
A simple checklist Claude can follow. Link back to the story and design doc.

Create Issues
Copy/paste each story/task into a GitHub issue. (If you later want automation, you can do that—but you said no code, so we’ll keep it manual and consistent.)

Have Claude execute
Give Claude the links to the design doc + specific story issue. Ask it to work story-by-story, and to update the issue with progress notes, test steps, and any questions.

Lightweight templates (copy/paste)
1) PRD (Product Requirements)

# <Project Name> — PRD
## Problem
## Users & Use Cases
## Goals / Success Metrics
- e.g., “Reduce X by 20%…”
## Scope (In)
## Out of Scope
## Constraints & Assumptions
## Rollout & Risks
## Links
- Design: /docs/design/<project>.md
- Stories: /planning/backlog.md

2) Design Doc
# <Project Name> — Design
## Context
## Proposed Architecture
## Data/Integrations
## Trade-offs & Alternatives
## Security/Privacy
## Observability
## Work Breakdown (map to stories)
- S-101: <title>
- S-102: <title>
## Open Questions
3) User Story
# S-101 — <Concise title>
**As a** <user/persona>  
**I want** <capability>  
**So that** <value>

## Acceptance Criteria
- [ ] When <condition>, <observable result>
- [ ] …

## Definition of Done
- [ ] Code, tests, docs updated
- [ ] Telemetry/alerts configured
- [ ] Demo GIF or screenshot attached

## Dependencies
- Design section: <anchor link>
- Related story: S-102

## Links
- PRD: /docs/product/<project>.md
- Design: /docs/design/<project>.md

4) Task Checklist (for a story)
# T-101 — Tasks for S-101
- [ ] Confirm requirements against PRD (link)
- [ ] Draft interface/schema (attach snippet)
- [ ] Implement feature flag / config toggle
- [ ] Add unit/integ tests covering ACs
- [ ] Update /runbooks/<topic>.md
- [ ] Self-QA using test plan /docs/qa/<project>.md
- [ ] Open PR; request review from @owner

- **S-101**: <title> — Priority: High — Estimate: 3d
  Links: [Story](/planning/stories/S-101.md) · [Design](/docs/design/<project>.md)

How to make Claude effective

Always provide links: PRD + Design + specific Story. Avoid giving it the entire repo at once.

Bounded scope: “Work only on S-101. If you need info, ask; don’t invent dependencies.”

Use the ACs as tests: Ask Claude to show how each acceptance criterion was satisfied (even if it’s reasoning or commands, not code).

Require artifacts: “Reply with: (1) plan, (2) assumptions, (3) risks, (4) open questions, (5) step-by-step execution checklist.”

Traceability: In the issue, have Claude paste a short “Decision log” section when it makes choices so humans can review later.

Labels & hygiene (keeps GitHub tidy)

Use a small, consistent set:

type:story, type:task, type:bug

status:ready, status:in-progress, status:blocker, status:review, status:done

area:frontend, area:backend, area:infra, etc.

Milestones = releases or sprints.

Where “src” fits (if/when you add code)

Greenfield app: src/ at the repo root.

Monorepo: packages/<service>/src per service/package.

Either way, docs and planning stay put at the top-level so product/design don’t move if code is reorganized.

## 🚀 Getting Started with Claude Code

### Quick Claude Commands

Paste these commands to get Claude working on specific tasks:

**For new features:**
```
Read /docs/product/<project>.md and /docs/design/<project>.md. Then open /planning/stories/S-101.md. Confirm the acceptance criteria, list assumptions/questions, and produce a numbered execution plan for S-101 only. Do not start any other story. When you're done, update the S-101 issue with a status note and any blockers.
```

**For project setup:**
```
Set up the development environment by following the backend and frontend setup instructions. Run all tests to ensure everything works. Report any setup issues or missing dependencies.
```

**For testing:**
```
Run the complete test suite (backend pytest + frontend Playwright). Fix any failing tests and ensure all acceptance criteria are met. Document any test coverage gaps.
```

### Project Structure for AI Development

This framework is optimized for Claude Code workflows:

- 📋 **Issue Templates**: Standardized GitHub issue templates for consistent task definition
- 🎯 **Bounded Scope**: Each story/task is self-contained with clear acceptance criteria
- 🔗 **Linked Artifacts**: PRDs, designs, and stories are cross-referenced for context
- ✅ **Definition of Done**: Clear completion criteria for every task
- 📊 **Progress Tracking**: Built-in status updates and decision logging
