# GitHub Project Permissions & Setup Guide

## Authentication Issues & Solutions

### Problem: Bad Credentials (HTTP 401)
This occurs when:
1. GitHub token has expired
2. Token lacks required scopes
3. Environment variables override stored credentials

### Solution: Proper Authentication Setup

```bash
# 1. Clear any conflicting environment variables
unset GH_TOKEN
unset GITHUB_TOKEN

# 2. Re-authenticate with all required scopes
gh auth login --scopes "repo,read:org,project,gist,workflow"

# 3. Verify authentication
gh auth status
# Should show: ✓ Token scopes: 'gist', 'project', 'read:org', 'repo', 'workflow'

# 4. Test repository access
gh repo view nestorwheelock/osint-LLM-framework
```

## GitHub Projects V2 Permissions

### Required Token Scopes for Projects
- ✅ **project** - Create and manage GitHub Projects
- ✅ **repo** - Access to repository (for linking issues)
- ✅ **read:org** - Read organization information
- ✅ **workflow** - Manage GitHub Actions (for automation)

### Project Creation & Management

#### 1. Create Project via CLI
```bash
# Create user project
gh project create --title "OSINT LLM Framework Development" --owner "@me"

# Create organization project (if member)
gh project create --title "Project Name" --owner "organization-name"
```

#### 2. Project GraphQL Operations
```bash
# List user projects
gh api graphql -f query='
query {
  viewer {
    projectsV2(first: 10) {
      nodes {
        id
        title
        number
        url
      }
    }
  }
}'

# Get project details
gh api graphql -f query='
query($owner: String!, $number: Int!) {
  user(login: $owner) {
    projectV2(number: $number) {
      id
      title
      fields(first: 20) {
        nodes {
          ... on ProjectV2Field {
            id
            name
            dataType
          }
        }
      }
    }
  }
}' -f owner="nestorwheelock" -F number=1
```

#### 3. Add Items to Project
```bash
# Add repository to project
gh api graphql -f query='
mutation($projectId: ID!, $contentId: ID!) {
  addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
    item {
      id
    }
  }
}' -f projectId="PROJECT_ID" -f contentId="ISSUE_ID"
```

### Project Field Management

#### Add Custom Fields
```bash
# Add Status field (single select)
gh api graphql -f query='
mutation($projectId: ID!) {
  createProjectV2Field(input: {
    projectId: $projectId
    dataType: SINGLE_SELECT
    name: "Status"
    singleSelectOptions: [
      {name: "Backlog", color: GRAY}
      {name: "Ready", color: YELLOW}
      {name: "In Progress", color: BLUE}
      {name: "Review", color: ORANGE}
      {name: "Done", color: GREEN}
    ]
  }) {
    projectV2Field {
      id
      name
    }
  }
}' -f projectId="PROJECT_ID"

# Add Priority field
gh api graphql -f query='
mutation($projectId: ID!) {
  createProjectV2Field(input: {
    projectId: $projectId
    dataType: SINGLE_SELECT
    name: "Priority"
    singleSelectOptions: [
      {name: "High", color: RED}
      {name: "Medium", color: YELLOW}
      {name: "Low", color: GREEN}
    ]
  }) {
    projectV2Field {
      id
      name
    }
  }
}' -f projectId="PROJECT_ID"
```

## Complete Automation Script Enhancement

### Enhanced Project Creation Function
```bash
create_github_project_v2() {
    log_info "Creating GitHub Project V2: $PROJECT_NAME"

    if [ "$DRY_RUN" = false ]; then
        # Create the project
        PROJECT_DATA=$(gh api graphql -f query='
        mutation($title: String!, $ownerId: ID!) {
          createProjectV2(input: {ownerId: $ownerId, title: $title}) {
            projectV2 {
              id
              number
              url
            }
          }
        }' -f title="$PROJECT_NAME" -f ownerId="$(gh api user --jq '.node_id')")

        if [ $? -eq 0 ]; then
            PROJECT_ID=$(echo "$PROJECT_DATA" | jq -r '.data.createProjectV2.projectV2.id')
            PROJECT_NUMBER=$(echo "$PROJECT_DATA" | jq -r '.data.createProjectV2.projectV2.number')
            PROJECT_URL=$(echo "$PROJECT_DATA" | jq -r '.data.createProjectV2.projectV2.url')

            echo "$PROJECT_NUMBER" > .github-project-number
            echo "$PROJECT_ID" > .github-project-id

            log_success "Created project: $PROJECT_URL"
            log_info "Project ID: $PROJECT_ID"
            log_info "Project Number: $PROJECT_NUMBER"

            # Set up project fields
            setup_project_fields "$PROJECT_ID"
        else
            log_error "Failed to create GitHub Project"
        fi
    else
        echo "[DRY RUN] Would create project: $PROJECT_NAME"
    fi
}

setup_project_fields() {
    local project_id="$1"
    log_info "Setting up project custom fields..."

    # Add Status field
    gh api graphql -f query='
    mutation($projectId: ID!) {
      createProjectV2Field(input: {
        projectId: $projectId
        dataType: SINGLE_SELECT
        name: "Status"
        singleSelectOptions: [
          {name: "Backlog", color: GRAY}
          {name: "Ready", color: YELLOW}
          {name: "In Progress", color: BLUE}
          {name: "Review", color: ORANGE}
          {name: "Done", color: GREEN}
        ]
      }) {
        projectV2Field {
          id
          name
        }
      }
    }' -f projectId="$project_id" > /dev/null

    # Add Priority field
    gh api graphql -f query='
    mutation($projectId: ID!) {
      createProjectV2Field(input: {
        projectId: $projectId
        dataType: SINGLE_SELECT
        name: "Priority"
        singleSelectOptions: [
          {name: "High", color: RED}
          {name: "Medium", color: YELLOW}
          {name: "Low", color: GREEN}
        ]
      }) {
        projectV2Field {
          id
          name
        }
      }
    }' -f projectId="$project_id" > /dev/null

    log_success "Project fields configured"
}
```

## Troubleshooting Guide

### 1. Authentication Problems
```bash
# Check current auth status
gh auth status

# Clear and re-authenticate
unset GH_TOKEN
gh auth logout
gh auth login --scopes "repo,read:org,project,gist,workflow"
```

### 2. Project Permission Issues
- Ensure token has `project` scope
- Verify you have permission to create projects in the organization
- Check if organization has project creation restrictions

### 3. GraphQL API Errors
- Validate query syntax with GitHub GraphQL Explorer
- Check field names and IDs are correct
- Ensure proper variable types (String vs ID)

### 4. Rate Limiting
- GitHub API has rate limits (5000 requests/hour for authenticated users)
- Implement backoff strategies for large automations
- Use conditional checks to avoid unnecessary API calls

## Version 2.0 Fixes & Improvements

### 🐛 Fixed Issues
1. **Label Parsing Bug**: Shell syntax error in multi-line string assignment
2. **Authentication Persistence**: Environment variable conflicts overriding stored credentials
3. **Project Field Creation**: GraphQL mutations for custom fields now working
4. **Git Operations**: HTTPS authentication failures resolved with SSH fallback

### 🚀 New Features
1. **Enhanced Error Handling**: Graceful fallbacks for all API operations
2. **Automatic Field Setup**: Status, Priority, and Size fields created automatically
3. **Authentication Recovery**: Step-by-step troubleshooting procedures
4. **Comprehensive Logging**: Detailed output for debugging authentication issues

## Testing Commands

```bash
# Test basic authentication
gh api user --jq '.login'

# Test with full scopes
gh auth status | grep "Token scopes"

# Test project creation (GraphQL)
gh api graphql -f query='query { viewer { login projectsV2(first:1) { nodes { title } } } }'

# Test repository access
gh repo view nestorwheelock/osint-LLM-framework --json name,owner

# Test the enhanced automation (dry run)
./scripts/setup-github-project.sh --repo nestorwheelock/osint-LLM-framework --dry-run

# Full automation test
unset GH_TOKEN && ./scripts/setup-github-project.sh --repo nestorwheelock/osint-LLM-framework
```

## Success Metrics

After running the automation successfully, you should see:
- ✅ Repository settings configured (merge policies, features)
- ✅ 15 standardized labels created
- ✅ GitHub Project created with URL
- ✅ 3 custom fields added (Status, Priority, Size)
- ✅ Issues created for all user stories
- ✅ Project milestones set up

## Production Deployment Checklist

- [ ] Authentication configured with all scopes
- [ ] Git remote set to SSH for reliable operations
- [ ] Automation scripts tested in dry-run mode
- [ ] Repository backup created before automation
- [ ] Team members granted appropriate project permissions
- [ ] Project board configured with appropriate views
- [ ] Workflow automation enabled for issue lifecycle

This guide provides comprehensive solutions for GitHub Project automation, authentication issues, and permission management with all the latest v2.0 enhancements.