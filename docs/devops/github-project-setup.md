# GitHub Project Board Setup Guide

## Overview

This guide provides step-by-step instructions for setting up a GitHub Project board to manage the OSINT LLM Framework development using our file-based planning system integrated with GitHub's native tools.

## Project Creation

### 1. Create New Project
1. Navigate to your GitHub repository
2. Go to "Projects" tab
3. Click "New project"
4. Choose "Table" view as the default
5. Name: "OSINT LLM Framework Epic"
6. Description: "AI-assisted OSINT research platform development tracking"

### 2. Project Configuration

#### Basic Settings
- **Visibility**: Private (recommended for internal development)
- **Access**: Repository collaborators
- **Project URL**: Save this for GitHub Actions configuration

## Custom Fields Configuration

### Priority Field
- **Field Type**: Single select
- **Options**:
  - 🔥 Highest (S-000 Infrastructure)
  - ⭐ High (S-001-010, S-015 Core Features)
  - 📈 Medium (S-011-014 Enhancements)
  - 🔮 Low (Future backlog)

### Epic Field
- **Field Type**: Single select
- **Options**:
  - S-000: Environment Setup
  - S-001: Create Subject
  - S-002: Start Session
  - S-003: Meta-Search
  - S-004: Web Scraping
  - S-005: Text Extraction
  - S-006: Entity Extraction
  - S-007: Labeling System
  - S-008: Export Functionality
  - S-009: Config Management
  - S-010: Ethical Controls
  - S-011: Timeline Assembly
  - S-012: Duplicate Detection
  - S-013: PDF Reports
  - S-014: Job Monitoring
  - S-015: Final Integration

### Sprint Field
- **Field Type**: Single select
- **Options**:
  - Pre-Sprint: Infrastructure
  - Sprint 1: Foundation
  - Sprint 2: Data Collection
  - Sprint 3: Content Processing
  - Sprint 4: Enhanced Features
  - Sprint 5: Production Integration

### Component Field
- **Field Type**: Multi-select
- **Options**:
  - 🏗️ Infrastructure
  - 🔧 Backend
  - 🎨 Frontend
  - 🗄️ Database
  - ⚙️ DevOps
  - 🔌 Integration
  - 📝 Documentation

### Story Points Field
- **Field Type**: Single select
- **Options**:
  - 1 (Simple task, <4 hours)
  - 2 (Small task, 4-8 hours)
  - 3 (Medium task, 1-2 days)
  - 5 (Large task, 2-3 days)
  - 8 (Complex task, 3-5 days)
  - 13 (Epic task, 1+ weeks)

### Estimated Hours Field
- **Field Type**: Number
- **Description**: Estimated implementation time from task files

### Assignee Field
- **Field Type**: People
- **Description**: Team member responsible for implementation

## Views Configuration

### 1. Board View (Default)
- **Layout**: Board
- **Group by**: Status
- **Sort by**: Priority (Highest first)
- **Filter**: All items
- **Columns**:
  - 📋 Todo
  - 🔄 In Progress
  - 👀 In Review
  - ✅ Done

### 2. Epic Overview
- **Layout**: Table
- **Group by**: Epic
- **Sort by**: Epic, then Priority
- **Columns**: Title, Status, Epic, Priority, Component, Story Points, Assignee
- **Filter**: Include all items

### 3. Sprint Planning
- **Layout**: Table
- **Group by**: Sprint
- **Sort by**: Sprint, then Priority
- **Columns**: Title, Status, Sprint, Epic, Story Points, Estimated Hours, Assignee
- **Filter**: Exclude Done items

### 4. Timeline View
- **Layout**: Roadmap
- **Group by**: Epic
- **Start date**: Created date
- **Target date**: Due date (if set)
- **Duration**: Based on story points
- **Filter**: Active sprints only

### 5. Component Breakdown
- **Layout**: Board
- **Group by**: Component
- **Sort by**: Priority
- **Filter**: Current sprint items
- **Columns**: Backend, Frontend, Database, DevOps, Integration

## Built-in Automations

### 1. Auto-add Items
**Workflow Name**: Auto-add tasks to project
**Trigger**: Issues with label "task"
**Action**: Add to project with status "Todo"

**Configuration**:
```yaml
When: Item is added to repository
If: Label equals "task"
Then: Add to project
Set status to: Todo
Set Epic to: [Parse from issue title]
```

### 2. Status Transitions
**Workflow Name**: Auto-update status
**Triggers**:
- Pull request opened → Set status to "In Progress"
- Pull request ready for review → Set status to "In Review"
- Pull request merged → Set status to "Done"
- Issue closed → Set status to "Done"

### 3. Auto-archive Completed
**Workflow Name**: Archive completed items
**Trigger**: Status changed to "Done"
**Condition**: Item has been "Done" for 7 days
**Action**: Archive item

## Integration Setup

### 1. GitHub Actions Configuration

#### Repository Secrets
Add these secrets to your repository settings:
- `PROJECT_TOKEN`: Personal access token with project permissions
- `ANTHROPIC_API_KEY`: Claude API key for AI integration

#### Project URL
Update the project URL in `.github/workflows/sync-tasks-to-issues.yml`:
```yaml
project-url: https://github.com/users/YOUR_USERNAME/projects/PROJECT_NUMBER
```

### 2. Auto-assignment Workflow
Create `.github/workflows/auto-assign-to-project.yml`:

```yaml
name: Auto-assign to Project

on:
  issues:
    types: [opened, labeled]

jobs:
  add-to-project:
    if: contains(github.event.issue.labels.*.name, 'task')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/add-to-project@v0.5.0
        with:
          project-url: YOUR_PROJECT_URL
          github-token: ${{ secrets.PROJECT_TOKEN }}
          labeled: task
```

## Project Management Workflows

### 1. Sprint Planning Process

#### Pre-Sprint Setup
1. Filter view by "Sprint: [Next Sprint]"
2. Review estimated story points vs team capacity
3. Assign team members to issues
4. Set target dates for sprint milestones
5. Verify dependencies are resolved

#### Daily Standups
1. Use "Sprint Planning" view
2. Filter by current sprint
3. Review "In Progress" items
4. Identify blockers and dependencies
5. Update status and assignments

#### Sprint Review
1. Switch to "Epic Overview"
2. Review completed story points
3. Move unfinished items to next sprint
4. Update epic progress
5. Archive completed items

### 2. Epic Tracking

#### Epic Progress Monitoring
1. Use "Epic Overview" view
2. Group by Epic to see completion status
3. Monitor story point burn-down
4. Track dependency completion
5. Review epic-level metrics

#### Cross-Epic Dependencies
1. Use "Timeline View" to visualize dependencies
2. Ensure prerequisite epics are on track
3. Identify potential timeline conflicts
4. Adjust sprint planning accordingly

## Advanced Features

### 1. Custom Insights
Create insights to track:
- **Velocity**: Story points completed per sprint
- **Cycle Time**: Time from Todo to Done
- **Epic Progress**: Completion percentage by epic
- **Component Distribution**: Work distribution across components

### 2. Filtering and Search
Use advanced filters:
- `is:issue label:task assignee:@me`
- `is:open priority:"High" sprint:"Sprint 2"`
- `epic:"S-001" status:"In Progress"`

### 3. Bulk Operations
- Bulk assign story points during planning
- Bulk move items between sprints
- Bulk update component labels
- Bulk archive completed items

## Troubleshooting

### Common Issues

#### Automation Not Working
1. Check repository secrets are set correctly
2. Verify project URL in workflow files
3. Ensure GitHub Actions have proper permissions
4. Review workflow logs for errors

#### Items Not Auto-Adding
1. Verify "task" label is applied to issues
2. Check auto-add workflow configuration
3. Ensure project permissions allow automation
4. Review project settings for label filters

#### Sync Issues with Task Files
1. Check file paths in sync workflow
2. Verify GitHub Actions can read repository files
3. Review task file naming conventions
4. Check for parsing errors in workflow logs

### Performance Optimization

#### Large Project Management
- Archive old completed items regularly
- Use date-based filters for current work
- Create separate views for different time horizons
- Limit API calls in custom automations

#### Team Collaboration
- Set up notification preferences
- Use assignee filters for individual views
- Create component-specific views for specialists
- Implement review assignment automation

## Best Practices

### 1. Consistent Labeling
- Always use "task" label for task issues
- Apply component labels consistently
- Use priority labels based on epic classification
- Keep epic labels synchronized with planning files

### 2. Regular Maintenance
- Weekly sprint planning sessions
- Monthly epic review meetings
- Quarterly project structure review
- Regular automation health checks

### 3. Team Training
- Onboard team members to project workflows
- Document custom view purposes
- Train on GitHub Actions integration
- Establish project management ceremonies

This setup provides comprehensive project management capabilities while maintaining integration with the file-based planning system and AI-assisted development workflows.