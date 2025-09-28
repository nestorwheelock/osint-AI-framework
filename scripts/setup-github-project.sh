#!/bin/bash
# GitHub Project Setup Automation Script
# Automates the manual GitHub setup work for new repositories

set -e

# Configuration
REPO_NAME=""
PROJECT_NAME="OSINT Framework Development"
DRY_RUN=false
VERBOSE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

run_command() {
    local cmd="$1"
    local description="$2"

    if [ "$VERBOSE" = true ]; then
        log_info "Running: $cmd"
    fi

    if [ "$DRY_RUN" = true ]; then
        echo "[DRY RUN] Would execute: $cmd"
        return 0
    fi

    if (unset GH_TOKEN && eval "$cmd"); then
        log_success "$description"
        return 0
    else
        log_error "Failed: $description"
        return 1
    fi
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if gh CLI is installed
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) is required but not installed"
        echo "Install with: brew install gh (macOS) or see https://cli.github.com/"
        exit 1
    fi

    # Check if authenticated
    if ! gh auth status &> /dev/null; then
        log_error "Not authenticated with GitHub CLI"
        echo "Run: gh auth login"
        exit 1
    fi

    # Check if we're in a git repository
    if ! git rev-parse --git-dir &> /dev/null; then
        log_error "Not in a git repository"
        exit 1
    fi

    # Auto-detect repo name if not provided
    if [ -z "$REPO_NAME" ]; then
        REPO_NAME=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")
        if [ -z "$REPO_NAME" ]; then
            log_error "Could not determine repository name. Please specify with --repo option"
            exit 1
        fi
    fi

    log_success "Prerequisites checked"
    log_info "Repository: $REPO_NAME"
}

setup_repository_settings() {
    log_info "Configuring repository settings..."

    # Enable/disable repository features
    run_command "gh api -X PATCH repos/$REPO_NAME -f has_issues=true" "Enable issues"
    run_command "gh api -X PATCH repos/$REPO_NAME -f has_projects=true" "Enable projects"
    run_command "gh api -X PATCH repos/$REPO_NAME -f has_wiki=false" "Disable wiki"

    # Configure merge settings
    run_command "gh api -X PATCH repos/$REPO_NAME -f allow_squash_merge=true" "Enable squash merge"
    run_command "gh api -X PATCH repos/$REPO_NAME -f allow_merge_commit=false" "Disable merge commits"
    run_command "gh api -X PATCH repos/$REPO_NAME -f allow_rebase_merge=false" "Disable rebase merge"
    run_command "gh api -X PATCH repos/$REPO_NAME -f delete_branch_on_merge=true" "Auto-delete branches"
}

create_labels() {
    log_info "Creating project labels..."

    # Define labels as "name:color:description"
    labels=(
        "type-feature:0052cc:New feature or enhancement"
        "type-bug:d73a4a:Something is not working"
        "type-docs:0075ca:Documentation improvement"
        "type-refactor:fbca04:Code refactoring"
        "type-infrastructure:1d76db:Infrastructure and DevOps"
        "priority-high:b60205:High priority"
        "priority-medium:fbca04:Medium priority"
        "priority-low:0e8a16:Low priority"
        "size-small:c2e0c6:1-2 days of work"
        "size-medium:fef2c0:3-5 days of work"
        "size-large:f9d0c4:1+ weeks of work"
        "ai-assisted:7057ff:Work done with AI assistance"
        "ready-for-dev:0e8a16:Ready for development"
        "blocked:d93f0b:Blocked by dependency"
        "needs-review:0052cc:Needs code review"
    )

    for label in "${labels[@]}"; do
        IFS=':' read -r name color description <<< "$label"

        # Check if label already exists
        if (unset GH_TOKEN && gh api "repos/$REPO_NAME/labels/$name" &> /dev/null); then
            log_warning "Label '$name' already exists, skipping"
        else
            run_command "gh api -X POST repos/$REPO_NAME/labels -f name='$name' -f color='$color' -f description='$description'" "Create label: $name"
        fi
    done
}

create_github_project() {
    log_info "Creating GitHub Project: $PROJECT_NAME"

    if [ "$DRY_RUN" = false ]; then
        # Get user ID for project creation
        USER_ID=$(gh api user --jq '.node_id' 2>/dev/null)

        if [ -z "$USER_ID" ]; then
            log_error "Failed to get user ID - authentication issue"
            return 1
        fi

        # Create project via GraphQL API
        PROJECT_DATA=$(gh api graphql -f query='
        mutation($title: String!, $ownerId: ID!) {
          createProjectV2(input: {ownerId: $ownerId, title: $title}) {
            projectV2 {
              id
              number
              url
            }
          }
        }' -f title="$PROJECT_NAME" -f ownerId="$USER_ID" 2>/dev/null)

        if [ $? -eq 0 ] && [ -n "$PROJECT_DATA" ]; then
            PROJECT_ID=$(echo "$PROJECT_DATA" | jq -r '.data.createProjectV2.projectV2.id' 2>/dev/null)
            PROJECT_NUMBER=$(echo "$PROJECT_DATA" | jq -r '.data.createProjectV2.projectV2.number' 2>/dev/null)
            PROJECT_URL=$(echo "$PROJECT_DATA" | jq -r '.data.createProjectV2.projectV2.url' 2>/dev/null)

            if [ "$PROJECT_ID" != "null" ] && [ -n "$PROJECT_ID" ]; then
                echo "$PROJECT_NUMBER" > .github-project-number
                echo "$PROJECT_ID" > .github-project-id

                log_success "Created project: $PROJECT_URL"
                log_info "Project ID: $PROJECT_ID"
                log_info "Project Number: $PROJECT_NUMBER"

                # Set up project fields
                setup_project_fields "$PROJECT_ID"
            else
                log_error "Failed to parse project creation response"
            fi
        else
            log_warning "GraphQL project creation failed, trying CLI method"

            # Fallback to CLI method
            PROJECT_URL=$(gh project create --title "$PROJECT_NAME" --owner "@me" 2>/dev/null || echo "")

            if [ -n "$PROJECT_URL" ]; then
                PROJECT_NUMBER=$(echo "$PROJECT_URL" | grep -o '[0-9]*$')
                echo "$PROJECT_NUMBER" > .github-project-number
                log_success "Created project (CLI): $PROJECT_URL"
                log_warning "Custom fields need manual setup in GitHub UI"
            else
                log_error "Failed to create GitHub Project"
            fi
        fi
    else
        echo "[DRY RUN] Would create project: $PROJECT_NAME"
    fi
}

setup_project_fields() {
    local project_id="$1"
    log_info "Setting up project custom fields..."

    # Add Status field
    STATUS_RESULT=$(gh api graphql -f query='
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
    }' -f projectId="$project_id" 2>/dev/null)

    if [ $? -eq 0 ]; then
        log_success "Added Status field"
    else
        log_warning "Failed to add Status field"
    fi

    # Add Priority field
    PRIORITY_RESULT=$(gh api graphql -f query='
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
    }' -f projectId="$project_id" 2>/dev/null)

    if [ $? -eq 0 ]; then
        log_success "Added Priority field"
    else
        log_warning "Failed to add Priority field"
    fi

    # Add Size field
    SIZE_RESULT=$(gh api graphql -f query='
    mutation($projectId: ID!) {
      createProjectV2Field(input: {
        projectId: $projectId
        dataType: SINGLE_SELECT
        name: "Size"
        singleSelectOptions: [
          {name: "Small", color: GREEN}
          {name: "Medium", color: YELLOW}
          {name: "Large", color: RED}
        ]
      }) {
        projectV2Field {
          id
          name
        }
      }
    }' -f projectId="$project_id" 2>/dev/null)

    if [ $? -eq 0 ]; then
        log_success "Added Size field"
    else
        log_warning "Failed to add Size field"
    fi
}

create_issues_from_stories() {
    log_info "Creating issues from user stories..."

    local stories_dir="planning/stories"
    local created_count=0

    if [ ! -d "$stories_dir" ]; then
        log_warning "No stories directory found at $stories_dir"
        return
    fi

    # Find all story files
    for story_file in "$stories_dir"/S-*.md; do
        if [ -f "$story_file" ]; then
            local basename=$(basename "$story_file" .md)
            local title=$(head -n 20 "$story_file" | grep '^# ' | head -n 1 | sed 's/^# //' || echo "$basename")

            # Clean up title
            title=$(echo "$title" | sed 's/[#*]//g' | xargs)

            if [ -z "$title" ]; then
                title="$basename"
            fi

            # Create issue body with reference to story file
            local issue_body="**User Story File:** \`$story_file\`

Please see the user story file for complete requirements, acceptance criteria, and implementation details.

This issue was automatically created from the user story planning documentation."

            # Determine labels based on story type
            local labels="ai-assisted,type-feature,ready-for-dev"

            # Create the issue
            if [ "$DRY_RUN" = false ]; then
                ISSUE_URL=$(gh issue create \
                    --title "$title" \
                    --body "$issue_body" \
                    --label "$labels" 2>/dev/null || echo "")

                if [ -n "$ISSUE_URL" ]; then
                    log_success "Created issue: $title"
                    ((created_count++))
                else
                    log_error "Failed to create issue for $story_file"
                fi
            else
                echo "[DRY RUN] Would create issue: $title"
                ((created_count++))
            fi
        fi
    done

    log_success "Created $created_count issues from user stories"
}

setup_milestones() {
    log_info "Setting up project milestones..."

    milestones=(
        "MVP:Initial minimum viable product release"
        "Beta:Beta release for testing"
        "v1.0:First stable release"
        "v1.1:First feature update"
    )

    for milestone in "${milestones[@]}"; do
        IFS=':' read -r title description <<< "$milestone"

        run_command "gh api -X POST repos/$REPO_NAME/milestones -f title='$title' -f description='$description'" "Create milestone: $title"
    done
}

display_summary() {
    echo ""
    echo "🎉 GitHub Project Setup Complete!"
    echo "========================================"
    echo ""
    echo "✅ Repository settings configured"
    echo "✅ Project labels created"
    echo "✅ GitHub Project created: $PROJECT_NAME"
    echo "✅ Issues created from user stories"
    echo "✅ Project milestones set up"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Configure custom fields in GitHub Project UI"
    echo "   2. Set up branch protection rules (if needed)"
    echo "   3. Add team members and collaborators"
    echo "   4. Configure repository secrets for CI/CD"
    echo ""
    echo "🔗 Quick links:"
    echo "   Repository: https://github.com/$REPO_NAME"
    echo "   Issues: https://github.com/$REPO_NAME/issues"

    if [ -f ".github-project-number" ]; then
        local project_number=$(cat .github-project-number)
        local owner=$(echo "$REPO_NAME" | cut -d'/' -f1)
        echo "   Project: https://github.com/users/$owner/projects/$project_number"
    fi
}

show_help() {
    cat << EOF
GitHub Project Setup Automation

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --repo REPO_NAME        Repository name (owner/repo format)
    --project-name NAME     Name for GitHub Project (default: "OSINT Framework Development")
    --dry-run              Show what would be done without making changes
    --verbose              Show detailed command output
    --help                 Show this help message

EXAMPLES:
    $0 --repo myorg/myproject
    $0 --dry-run --verbose
    $0 --project-name "My Custom Project"

PREREQUISITES:
    - GitHub CLI (gh) installed and authenticated
    - Current directory must be a git repository
    - Repository must exist on GitHub

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --repo)
            REPO_NAME="$2"
            shift 2
            ;;
        --project-name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
main() {
    echo "🚀 GitHub Project Setup Automation"
    echo "=================================="
    echo ""

    check_prerequisites

    echo ""
    log_info "Starting automation for repository: $REPO_NAME"

    if [ "$DRY_RUN" = true ]; then
        log_warning "DRY RUN MODE - No changes will be made"
    fi

    echo ""

    setup_repository_settings
    echo ""

    create_labels
    echo ""

    create_github_project
    echo ""

    create_issues_from_stories
    echo ""

    setup_milestones
    echo ""

    display_summary
}

# Run main function
main