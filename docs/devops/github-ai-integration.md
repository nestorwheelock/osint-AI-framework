# GitHub AI Integration & DevOps Automation Plan

## Overview

This document outlines the comprehensive integration strategy for combining our file-based planning documentation system with GitHub's native project management tools, automated workflows, and AI-powered development assistance through Claude Code integration.

## Architecture

### Current Planning System (Source of Truth)
```
planning/
├── stories/           # User stories (S-000 to S-015)
│   ├── S-000-environment-setup.md
│   ├── S-001-create-subject.md
│   └── ...
├── tasks/            # Implementation tasks (T-000 to T-015)
│   ├── T-000-environment-setup.md
│   ├── T-001-create-subject.md
│   └── ...
└── backlog.md        # Epic overview and sprint planning
```

### GitHub Integration Layer
```
GitHub Issues     ←→    Task Files (T-*.md)
     ↓
GitHub Projects   ←→    Epic Planning (backlog.md + stories)
     ↓
GitHub Actions    ←→    Automated Workflows
     ↓
Claude Code       ←→    AI-Assisted Development
```

## Integration Components

### 1. Automated Issue Generation

**Purpose**: Convert task markdown files into trackable GitHub Issues
**Workflow**: `.github/workflows/sync-tasks-to-issues.yml`

#### Features:
- **Auto-Detection**: Monitors changes to `planning/tasks/T-*.md` files
- **Smart Labeling**: Automatically applies priority, component, and type labels
- **Bidirectional Sync**: Keeps issues updated when task files change
- **Duplicate Prevention**: Checks for existing issues before creating new ones
- **Force Recreation**: Manual trigger to rebuild all issues

#### Label Classification:
```yaml
Priority Labels:
  - priority-highest  # S-000 (Infrastructure)
  - priority-high     # S-001-010, S-015 (Core features)
  - priority-medium   # S-011-014 (Enhancements)

Component Labels:
  - backend      # FastAPI, Python, database
  - frontend     # React, TypeScript, UI
  - database     # PostgreSQL, schema, migrations
  - devops       # Docker, CI/CD, infrastructure
  - integration  # Cross-component features

Type Labels:
  - task            # All generated from task files
  - infrastructure  # S-000 related
  - foundation      # S-001-003 core setup
  - data-processing # S-004-006 content pipeline
  - core-features   # S-007-010 main functionality
  - enhancement     # S-011-014 advanced features
```

#### Issue Template Structure:
```markdown
[T-XXX-task-name] Task Title

<!-- Auto-generated from planning/tasks/T-XXX-task-name.md -->

[Full task markdown content]

---

**Task File**: `planning/tasks/T-XXX-task-name.md`
**Story Reference**: S-XXX - Story Name
**Estimated Hours**: XX-XX hours

> This issue was automatically generated from the task breakdown file.
> Updates to the task file will sync to this issue.
```

### 2. GitHub Projects Configuration

**Purpose**: Provide high-level epic management and sprint planning
**Setup**: Manual configuration through GitHub web interface

#### Project Structure:
- **Views**: Board, Table, Timeline, Roadmap
- **Custom Fields**:
  - Story Points (1, 2, 3, 5, 8, 13)
  - Epic (S-000 through S-015)
  - Sprint (Pre-Sprint, Sprint 1-5)
  - Component (Infrastructure, Backend, Frontend, Database, DevOps)
  - Estimated Hours (from task files)

#### Automated Workflows:
- **Status Transitions**: Auto-move issues through Todo → In Progress → Done
- **Auto-Assignment**: Assign to project when labeled with 'task'
- **Sprint Planning**: Filter and group by custom fields
- **Dependency Tracking**: Visual representation of story dependencies

### 3. Claude Code Integration

**Purpose**: AI-powered development assistance and code review
**Setup**: Claude Code GitHub Actions + project-specific configuration

#### Configuration Files:

##### CLAUDE.md (Repository Root)
```markdown
# OSINT Framework - Claude Code Guidelines

## Project Overview
AI-assisted OSINT research platform using FastAPI, React, PostgreSQL, and Docker.

## Code Style & Standards
- Backend: FastAPI with SQLAlchemy ORM, pytest for testing
- Frontend: React with TypeScript, Playwright for E2E testing
- Database: PostgreSQL with Alembic migrations
- Security: NEVER include author attribution in code or commits

## AI Coding Briefs
Reference the planning/tasks/T-*.md files for detailed implementation guidance.
Each task includes specific AI coding briefs with constraints and test requirements.

## Test-Driven Development
Always write tests first, then implement minimal code to pass.
Maintain >95% code coverage for all new features.

## Security Requirements
- No AI attribution in code, comments, or commits
- Follow security guidelines in planning documentation
- Implement proper input validation and sanitization
```

##### .github/workflows/claude-code-integration.yml
```yaml
name: Claude Code Integration

on:
  issue_comment:
    types: [created]
  pull_request:
    types: [opened, synchronize]

jobs:
  claude-assistance:
    if: contains(github.event.comment.body, '@claude') || github.event_name == 'pull_request'
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Claude Code Action
        uses: anthropics/claude-code-action@v1
        with:
          anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
          max-tokens: 4000
          model: claude-3-5-sonnet-20241022
```

#### Usage Patterns:
- **@claude review**: Code review and suggestions
- **@claude implement**: Feature implementation assistance
- **@claude fix**: Bug fixing and debugging
- **@claude test**: Test creation and validation
- **@claude docs**: Documentation updates

### 4. Advanced Automation Workflows

#### A. Auto-Add to Project
```yaml
name: Auto-Add Issues to Project

on:
  issues:
    types: [opened, labeled]

jobs:
  add-to-project:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/add-to-project@v0.5.0
        with:
          project-url: https://github.com/users/USERNAME/projects/PROJECT_NUMBER
          github-token: ${{ secrets.PROJECT_TOKEN }}
          labeled: task
```

#### B. Issue Lifecycle Management
```yaml
name: Issue Lifecycle

on:
  pull_request:
    types: [opened, closed]
  issues:
    types: [closed, reopened]

jobs:
  update-status:
    runs-on: ubuntu-latest
    steps:
      - name: Update Project Status
        # Custom logic to update project fields based on events
```

#### C. Documentation Sync
```yaml
name: Sync Documentation

on:
  push:
    paths:
      - 'planning/**/*.md'
      - 'docs/**/*.md'

jobs:
  update-related-issues:
    runs-on: ubuntu-latest
    steps:
      - name: Update Issue Descriptions
        # Sync changes back to related GitHub Issues
```

## Benefits of This Integration

### 1. Maintains Documentation Quality
- **Source of Truth**: Markdown files remain the authoritative documentation
- **Rich Linking**: Preserves cross-references between stories, tasks, and design docs
- **Version Control**: Full history of planning changes in Git
- **Review Process**: Changes go through PR review before affecting issues

### 2. Enables GitHub Native Features
- **Team Collaboration**: Issues, comments, mentions, assignments
- **Project Management**: Boards, timelines, sprint planning, progress tracking
- **Integration**: Links with PRs, commits, deployments
- **Automation**: Workflows, notifications, status updates

### 3. AI-Powered Development
- **Context-Aware**: Claude has access to full planning documentation
- **Consistent Standards**: AI coding briefs ensure uniform implementation
- **Test-Driven**: Automated test creation and validation
- **Security Compliant**: No attribution requirements enforced

### 4. DevOps Excellence
- **Automated Workflows**: Reduce manual project management overhead
- **Continuous Integration**: Issues automatically track development progress
- **Quality Gates**: Automated testing and review processes
- **Observability**: Clear visibility into epic progress and blockers

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [x] Create task-to-issue sync workflow
- [ ] Set up GitHub Project board
- [ ] Configure automated workflows
- [ ] Test issue generation for all existing tasks

### Phase 2: AI Integration (Week 2)
- [ ] Install Claude Code GitHub Actions
- [ ] Create CLAUDE.md with project guidelines
- [ ] Test @claude mentions and assistance
- [ ] Train team on Claude integration

### Phase 3: Advanced Automation (Week 3)
- [ ] Implement bidirectional sync
- [ ] Set up project lifecycle automation
- [ ] Create custom dashboards and reports
- [ ] Establish monitoring and alerting

### Phase 4: Optimization (Week 4)
- [ ] Refine workflows based on usage
- [ ] Add custom project fields and views
- [ ] Implement advanced AI assistance patterns
- [ ] Document best practices and team guidelines

## Success Metrics

### Automation Efficiency
- **Issue Creation Time**: < 1 minute from task file commit to issue
- **Sync Accuracy**: 100% consistency between files and issues
- **Workflow Reliability**: > 99% successful automation runs

### Development Velocity
- **Planning Overhead**: Reduce manual project management by 75%
- **Development Focus**: Increase coding time vs. administrative tasks
- **Quality Maintenance**: Maintain test coverage and documentation standards

### Team Adoption
- **Tool Usage**: Regular use of @claude mentions and project boards
- **Process Compliance**: Consistent use of task files and issue workflows
- **Feedback Integration**: Continuous improvement based on team input

## Troubleshooting

### Common Issues
1. **Missing Project Token**: Ensure `PROJECT_TOKEN` secret has proper permissions
2. **Workflow Failures**: Check GitHub Actions logs for authentication issues
3. **Label Conflicts**: Verify label names match in repository settings
4. **Claude Rate Limits**: Monitor API usage and implement backoff strategies

### Monitoring
- **GitHub Actions**: Monitor workflow success rates and execution times
- **Issue Sync**: Regular audits of file-to-issue consistency
- **Project Health**: Track completion rates and cycle times
- **AI Usage**: Monitor Claude API usage and effectiveness

## Security Considerations

### Access Control
- **Repository Permissions**: Limit who can modify workflow files
- **Project Access**: Control project board visibility and editing rights
- **API Keys**: Secure storage of Anthropic API keys in GitHub Secrets
- **Automation Scope**: Limit automated actions to necessary operations

### Compliance
- **No Attribution**: Automated enforcement of no-AI-attribution policy
- **Audit Trails**: Full history of automated changes in Git and GitHub
- **Privacy**: Ensure no sensitive data in public issue descriptions
- **Rate Limiting**: Respect API limits and implement proper backoff

This integration plan provides a comprehensive bridge between file-based planning and GitHub's project management ecosystem while maintaining the quality and structure of the existing documentation system.