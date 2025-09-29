# GitHub Contexts: Repository vs User Account

## Overview
Our OSINT AI Framework uses both repository-level and user account-level GitHub features. Understanding the correct context is crucial for proper automation and visibility.

## Repository Level (`nestorwheelock/osint-AI-framework`)
**Location**: https://github.com/nestorwheelock/osint-AI-framework

**Features**:
-  **Issues**: Created and managed at repository level
-  **Pull Requests**: Repository-specific
-  **Code**: Repository content, branches, releases
-  **Repository Settings**: Webhooks, collaborators, etc.

**CLI Commands**:
```bash
# Issues (repository context)
gh issue create --title "Title" --body "Body"
gh issue list
gh issue view 67

# Repository info
gh repo view
```

## User Account Level (`nestorwheelock`)
**Location**: https://github.com/nestorwheelock?tab=projects

**Features**:
-  **Projects**: Cross-repository project management (Project #5)
-  **User Settings**: Account-wide configurations
-  **Organizations**: User membership and roles

**CLI Commands**:
```bash
# Projects (user context)
gh api graphql -f query='
  query($owner: String!, $number: Int!) {
    user(login: $owner) {
      projectV2(number: $number) {
        items(first: 100) { ... }
      }
    }
  }
' -F owner=nestorwheelock -F number=5
```

## Current Configuration

### Working Correctly:
- **Issues**: Repository level (`nestorwheelock/osint-AI-framework/issues`)
- **Projects**: User account level (Project #5 at user level)
- **Project Updates**: Our bulk update script correctly targets user-level Project #5

### Integration:
- Repository issues can be linked to user-level projects
- User-level Project #5 manages items across repositories
- GitHub CLI automatically detects repository context when run from repo directory

## Verification Commands

### Check Repository Context:
```bash
gh repo view --json name,owner
```

### Check Issues:
```bash
gh issue list --limit 10
gh issue view {issue_number}
```

### Check Project Access:
```bash
# Via our bulk update script
python scripts/bulk-update-project-status.py
```

## Troubleshooting

### Issue Not Visible in Web Interface:
1. **Browser Cache**: Clear cache and hard refresh
2. **Repository Access**: Ensure you're logged in with correct account
3. **Direct URL**: Try accessing direct issue URL
4. **CLI Verification**: Use `gh issue view {number}` to confirm existence

### Project Updates Not Working:
1. **Authentication**: Ensure keyring authentication is active
2. **User Context**: Verify Project #5 is at user account level
3. **API Permissions**: Check token has `project` scope

## Best Practices

1. **Always verify context** before creating issues/projects
2. **Use direct URLs** for manual verification
3. **Include verification steps** in automation scripts
4. **Document** the distinction between repo and user features
