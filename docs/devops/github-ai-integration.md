# GitHub AI Integration & DevOps Automation Plan

## Overview

This document outlines the comprehensive integration strategy for combining our file-based planning documentation system with GitHub's native project management tools, automated workflows, and AI-powered development assistance through Claude Code integration.

## Architecture

### Current Planning System (Source of Truth)
```
planning/
 stories/           # User stories (S-000 to S-015)
    S-000-environment-setup.md
    S-001-create-subject.md
    ...
 tasks/            # Implementation tasks (T-000 to T-015)
    T-000-environment-setup.md
    T-001-create-subject.md
    ...
 backlog.md        # Epic overview and sprint planning
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

## Prerequisites & Setup Requirements

###  GitHub CLI Authentication

**CRITICAL**: Before running any automation scripts, you must authenticate GitHub CLI with proper permissions.

#### Initial Setup (One-time)

```bash
# Install GitHub CLI (if not already installed)
# macOS:
brew install gh
# Ubuntu/Debian:
sudo apt install gh
# Windows: Download from https://cli.github.com/

# Authenticate with full permissions
gh auth login
```

**Authentication Flow:**
1. Choose: **GitHub.com**
2. Choose: **HTTPS** (recommended)
3. Choose: **Yes** - Authenticate Git with GitHub credentials
4. Choose: **Login with a web browser**
5. Follow browser authentication and **authorize all requested permissions**

#### Required Permissions

The GitHub token needs these scopes for full automation:
-  **repo** - Full repository access
-  **read:org** - Read organization membership
-  **project** - Manage GitHub Projects
-  **write:discussion** - Create discussions
-  **gist** - Create gists

#### Verify Authentication

```bash
# Check authentication status
gh auth status

# Should show something like:
#  Logged in to github.com account username (keyring)
# - Token scopes: 'gist', 'project', 'read:org', 'repo'

# Test repository access
gh repo view
```

###  Common Authentication Issues & Solutions

| Error | Cause | Complete Solution |
|-------|-------|-------------------|
| `HTTP 401: Bad credentials` | Invalid/expired token | `unset GH_TOKEN && gh auth login --scopes "repo,read:org,project,gist,workflow"` |
| `Missing project scope` | Token lacks project permissions | Re-authenticate and grant ALL permissions in browser |
| `Validation Failed (HTTP 422)` | Label format error (fixed v2.0+) | Update to latest automation scripts |
| `Authentication failed for Git` | HTTPS credential issues | `git remote set-url origin git@github.com:user/repo.git` |
| `Repository not found` | Token lacks repo access | Verify repository name and re-authenticate |
| `GraphQL createProjectV2 failed` | Missing project scope | Include `project` in scopes: `--scopes "repo,read:org,project,gist,workflow"` |

###  Complete Authentication Reset Procedure

**When automation fails with authentication errors:**

```bash
# Step 1: Clean slate - remove all conflicting tokens
unset GH_TOKEN
unset GITHUB_TOKEN
gh auth logout

# Step 2: Fresh authentication with all required scopes
gh auth login --scopes "repo,read:org,project,gist,workflow"
# Choose: GitHub.com → HTTPS → Yes → Login with browser
# IMPORTANT: Grant ALL permissions in browser

# Step 3: Verify authentication is working
gh auth status
# Must show:  Token scopes: 'gist', 'project', 'read:org', 'repo', 'workflow'

# Step 4: Test basic API access
gh api user --jq '.login'  # Should return your username

# Step 5: Switch Git remote to SSH for reliable operations
git remote set-url origin git@github.com:nestorwheelock/osint-AI-framework.git

# Step 6: Run automation
./scripts/setup-github-project.sh --repo nestorwheelock/osint-AI-framework
```

###  Manual Fallback Options

If automation fails due to authentication issues, you can manually:

1. **Create GitHub Project**: Use GitHub web interface → Your repositories → Projects → New project
2. **Create Labels**: Repository → Issues → Labels → New label
3. **Create Issues**: Repository → Issues → New issue
4. **Configure Settings**: Repository → Settings → General

## Integration Components

### 1. Automated Project Setup & Issue Generation

**Purpose**: Complete GitHub project automation from initial setup through ongoing sync
**Scripts**:
- `scripts/setup-github-project.sh` - Initial project setup
- `scripts/setup-github-automation.py` - Advanced Python automation
- `scripts/sync-github-projects.py` - Bidirectional sync

#### GitHub Project Setup Automation
The `setup-github-project.sh` script automates the complete initial setup:

```bash
# Auto-setup with current repository
./scripts/setup-github-project.sh

# Custom setup with options
./scripts/setup-github-project.sh \
  --repo owner/repo-name \
  --project-name "My Custom Project" \
  --dry-run

# Test what would be done
./scripts/setup-github-project.sh --dry-run --verbose
```

**Automated Setup Features**:
- **Repository Settings**: Configure merge settings, features, and branch protection
- **Label Management**: Create standardized labels for types, priorities, and sizes
- **GitHub Project Creation**: Set up project board with recommended fields
- **Issue Generation**: Convert all user stories to GitHub issues
- **Milestone Setup**: Create project milestones and roadmap

#### Bidirectional File ↔ GitHub Sync

**Core Workflow**: Files are the source of truth, but GitHub Projects enable client collaboration

```mermaid
graph LR
    A[AI Creates Stories] --> B[Story Files]
    B --> C[GitHub Issues]
    C --> D[GitHub Projects GUI]
    D --> E[Client Planning]
    E --> F[Sync Back to Files]
    F --> G[AI Next Sprint]
```

**Sync Commands**:
```bash
# Sync changes from GitHub Project back to files
./scripts/sync-github-projects.py owner/repo --sync-to-files

# Sync file changes to GitHub Project
./scripts/sync-github-projects.py owner/repo --sync-to-github

# Check sync status
./scripts/sync-github-projects.py owner/repo --status
```

#### Features:
- **Smart Story Detection**: Automatically links issues to user story files
- **Metadata Preservation**: Maintains YAML frontmatter with GitHub sync data
- **Intelligent File Generation**: Creates new story files from GitHub-only issues
- **Client-Friendly Planning**: Use GitHub Projects GUI with clients, sync changes back
- **AI-Ready Output**: Updated files ready for next AI development sprint

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
# OSINT AI Framework - Claude Code Guidelines

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

###  Latest Automation Enhancements (v2.0)

#### New Features & Bug Fixes
- ** Fixed Label Parsing**: Resolved shell syntax errors in label creation
- ** GraphQL Project Creation**: Advanced project setup with custom fields
- ** Authentication Recovery**: Comprehensive error handling and fallback methods
- ** Custom Field Automation**: Status, Priority, and Size fields created automatically
- ** Git Authentication**: SSH fallback for reliable repository operations

#### Enhanced Project Field Setup
The automation now automatically creates these custom fields:

**Status Field (Single Select)**:
-  Backlog (Gray)
-  Ready (Yellow)
-  In Progress (Blue)
-  Review (Orange)
-  Done (Green)

**Priority Field (Single Select)**:
-  High (Red)
-  Medium (Yellow)
-  Low (Green)

**Size Field (Single Select)**:
-  Small (Green) - 1-2 days
-  Medium (Yellow) - 3-5 days
-  Large (Red) - 1+ weeks

### Detailed Script Operations

#### What setup-github-project.sh v2.0 Does Step-by-Step

**Repository Configuration:**
```bash
# Enables GitHub features
gh api -X PATCH repos/OWNER/REPO -f has_issues=true
gh api -X PATCH repos/OWNER/REPO -f has_projects=true
gh api -X PATCH repos/OWNER/REPO -f has_wiki=false

# Sets merge policies (squash-only workflow)
gh api -X PATCH repos/OWNER/REPO -f allow_squash_merge=true
gh api -X PATCH repos/OWNER/REPO -f allow_merge_commit=false
gh api -X PATCH repos/OWNER/REPO -f allow_rebase_merge=false
gh api -X PATCH repos/OWNER/REPO -f delete_branch_on_merge=true
```

**Label Creation (15 standardized labels):**
- **Type Labels**: `type:feature`, `type:bug`, `type:docs`, `type:refactor`, `type:infrastructure`
- **Priority Labels**: `priority:high`, `priority:medium`, `priority:low`
- **Size Labels**: `size:small` (1-2 days), `size:medium` (3-5 days), `size:large` (1+ weeks)
- **Workflow Labels**: `ai-assisted`, `ready-for-dev`, `blocked`, `needs-review`

**Enhanced Project Creation (v2.0):**
```bash
# Method 1: Advanced GraphQL-based creation with custom fields
USER_ID=$(gh api user --jq '.node_id')
PROJECT_DATA=$(gh api graphql -f query='
mutation($title: String!, $ownerId: ID!) {
  createProjectV2(input: {ownerId: $ownerId, title: $title}) {
    projectV2 {
      id
      number
      url
    }
  }
}' -f title="Project Name" -f ownerId="$USER_ID")

# Automatically creates custom fields:
# - Status (Backlog, Ready, In Progress, Review, Done)
# - Priority (High, Medium, Low)
# - Size (Small, Medium, Large)

# Method 2: Fallback to CLI if GraphQL fails
gh project create --title "Project Name" --owner "@me"

# Saves project metadata for future operations
echo "PROJECT_NUMBER" > .github-project-number
echo "PROJECT_ID" > .github-project-id
```

**Issue Generation:**
- Scans `planning/stories/S-*.md` files
- Extracts title from first heading or filename
- Creates GitHub issue with story content
- Applies appropriate labels (`ai-assisted`, `type:feature`, `ready-for-dev`)
- Links back to original story file

#### What sync-github-projects.py Does

**File-to-GitHub Sync:**
1. Reads all user story files in `planning/stories/`
2. Parses YAML frontmatter for metadata
3. Creates/updates corresponding GitHub issues
4. Maintains links between files and issues

**GitHub-to-File Sync:**
1. Fetches GitHub Project items via GraphQL API
2. Extracts issue data including custom fields
3. Updates YAML frontmatter in story files
4. Creates new story files for GitHub-only issues
5. Preserves file structure and AI-readable format

**Sync Metadata Storage:**
- Stores sync history in `.github/project-sync/last_sync.json`
- Tracks changes for conflict resolution
- Maintains file-to-issue mapping

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
