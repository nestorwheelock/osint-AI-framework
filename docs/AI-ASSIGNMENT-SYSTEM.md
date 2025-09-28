# AI Assignment System Documentation

A comprehensive system for automated task delegation to AI assistants with precise constraints, boundaries, and workflow integration.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Quick Start](#quick-start)
5. [Core Components](#core-components)
6. [Constraint System](#constraint-system)
7. [Prompt Templates](#prompt-templates)
8. [Workflow Integration](#workflow-integration)
9. [Advanced Usage](#advanced-usage)
10. [API Reference](#api-reference)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)
13. [Testing](#testing)
14. [Contributing](#contributing)

## Overview

### What is the AI Assignment System?

The AI Assignment System is a sophisticated framework for delegating development tasks to AI assistants while maintaining strict boundaries, security requirements, and quality standards. It transforms your planning files into actionable, constraint-based prompts that ensure AI assistants work within defined scope boundaries.

### Key Benefits

- **Scope Control**: Prevent AI assistants from modifying unintended files
- **Security Enforcement**: Automatic prevention of AI attribution in code
- **Quality Assurance**: Enforce testing requirements and definition of done
- **Workflow Integration**: Seamless GitHub Projects integration
- **Template Reusability**: Consistent approach across projects
- **Audit Trail**: Complete tracking of task assignments and constraints

### Use Cases

- **Enterprise Development**: Large teams needing controlled AI assistance
- **Open Source Projects**: Maintaining contribution quality and scope
- **Educational Environments**: Teaching proper AI-assisted development
- **Compliance Requirements**: Projects requiring audit trails and attribution control
- **Template-Based Development**: Reusable project methodologies

## Architecture

### System Components

```
AI Assignment System
├── Constraint Parser      (ai-constraint-parser.py)
│   ├── YAML Frontmatter Parser
│   ├── AI Coding Brief Extractor
│   └── Constraint Validator
├── Prompt Generator       (generate-ai-prompt.py)
│   ├── Template Engine
│   ├── Multi-Platform Support
│   └── Interactive Formatter
├── Assignment Manager     (ai-assign.py)
│   ├── Task Delegation
│   ├── Workflow Integration
│   └── Bulk Operations
└── Testing Suite         (test_ai_system.py)
    ├── Unit Tests
    ├── Integration Tests
    └── End-to-End Tests
```

### Data Flow

```
Planning Files (*.md)
       ↓
Constraint Parser
       ↓
AIConstraints Object
       ↓
Prompt Generator
       ↓
Formatted AI Prompt
       ↓
Assignment Manager
       ↓
AI Platform Integration
```

### File Structure

```
project/
├── planning/
│   ├── stories/           # User stories with AI coding briefs
│   │   ├── S-001-*.md     # Story files
│   │   └── S-NNN-*.md
│   └── tasks/             # Task breakdowns
│       ├── T-001-*.md     # Task files
│       └── T-NNN-*.md
├── scripts/
│   ├── ai-constraint-parser.py    # Core constraint extraction
│   ├── generate-ai-prompt.py      # Prompt generation
│   ├── ai-assign.py               # Main assignment interface
│   └── test_ai_system.py          # Test suite
├── tmp/                   # Generated prompts (git-ignored)
│   ├── T-001-prompt-claude-code.md
│   └── assignment-history.json
└── docs/
    └── AI-ASSIGNMENT-SYSTEM.md    # This documentation
```

## Installation & Setup

### Prerequisites

- Python 3.8+
- Git repository with planning structure
- Planning files in Markdown format
- YAML support (PyYAML)

### Installation

```bash
# Clone or copy the AI assignment scripts to your project
cp scripts/ai-*.py your-project/scripts/

# Install dependencies (if not already available)
pip install PyYAML

# Make scripts executable
chmod +x scripts/ai-*.py

# Verify installation
python scripts/ai-assign.py --help
```

### Planning Structure Setup

Create the required directory structure:

```bash
mkdir -p planning/{stories,tasks}
mkdir -p tmp
```

Add to `.gitignore`:
```
tmp/
*.tmp
*-prompt-*.md
```

### Story Template

Create stories with AI coding briefs:

```markdown
# S-001 — Feature Name

**As a** user type
**I want** to do something
**So that** I can achieve goal

## AI Coding Brief
```yaml
role: "Senior Django backend engineer practicing strict TDD"
objective: "Implement feature with proper error handling and testing"
constraints:
  allowed_paths:
    - backend/apps/feature/models.py
    - backend/apps/feature/views.py
    - backend/apps/feature/tests.py
  forbidden_paths:
    - backend/settings/production.py
  database: "Use Django ORM with PostgreSQL"
  testing: "Write Django tests first, then implement minimal code to pass"
  security:
    - "🚨 CRITICAL: NEVER include any AI, Claude, or assistant attribution anywhere"
    - "🚨 CRITICAL: Follow OWASP security guidelines"
tests_to_make_pass:
  - backend/apps/feature/tests.py::TestFeature::test_success
definition_of_done:
  - "All tests pass with Django test runner"
  - "API endpoints return proper HTTP status codes"
  - "Documentation updated"
```
```

### Task Template

Create tasks that inherit or override story constraints:

```markdown
```yaml
last_synced: '2025-09-28T16:22:25.047760'
status: todo
```

# T-001 — Tasks for S-001: Feature Implementation

## Prerequisites
- [ ] Review feature requirements
- [ ] Set up development environment

## Implementation
- [ ] Create feature models
- [ ] Implement API endpoints
- [ ] Add comprehensive tests

## Testing
- [ ] Unit tests for all components
- [ ] Integration tests for API
- [ ] Error handling verification

## Links
- **S-001**: [Feature Story](../stories/S-001-feature.md)
```

## Quick Start

### 1. List Available Tasks

```bash
python scripts/ai-assign.py --list
```

### 2. Review Task Summary

```bash
python scripts/ai-assign.py T-001 --summary
```

### 3. Assign Task to AI

```bash
# Assign to Claude Code (default)
python scripts/ai-assign.py T-001

# Assign to different platform
python scripts/ai-assign.py T-001 --ai gpt4

# Save prompt and auto-open browser
python scripts/ai-assign.py T-001 --save --open
```

### 4. Bulk Assignment

```bash
# Assign multiple ready tasks
python scripts/ai-assign.py --bulk --max-tasks 3
```

## Core Components

### AIConstraints Data Class

The core data structure representing task constraints:

```python
@dataclass
class AIConstraints:
    task_id: str                    # Task identifier (T-001)
    title: str                      # Human-readable title
    role: str                       # AI role/persona
    objective: str                  # What to accomplish
    allowed_paths: List[str]        # Files AI can modify
    forbidden_paths: List[str]      # Files AI cannot touch
    tests_to_make_pass: List[str]   # Required test cases
    definition_of_done: List[str]   # Completion criteria
    security_requirements: List[str] # Security constraints
    database: str                   # Database requirements
    testing_approach: str           # Testing methodology
```

### AIConstraintParser

Extracts constraints from planning files:

```python
parser = AIConstraintParser(project_root)

# Parse constraints for specific task
constraints = parser.parse_task_constraints("T-001")

# Validate constraint completeness
issues = parser.validate_constraints(constraints)

# List available tasks
tasks = parser.list_available_tasks()
```

**Constraint Resolution Priority:**
1. Task file YAML frontmatter (highest priority)
2. Parent story AI coding brief
3. Default values (if specified)

### AIPromptGenerator

Converts constraints to formatted prompts:

```python
generator = AIPromptGenerator()

# Generate platform-specific prompt
prompt = generator.generate_prompt(constraints, 'claude-code')

# Generate interactive copy-paste format
interactive_prompt = generator.generate_interactive_prompt(constraints)

# List available templates
templates = generator.list_templates()
```

### AIAssignmentManager

Main interface for task delegation:

```python
manager = AIAssignmentManager(project_root, repo_name, project_number)

# Assign single task
success = manager.assign_task("T-001", ai_platform="claude-code", save_prompt=True)

# Show task summary
manager.show_task_summary("T-001")

# Bulk assign ready tasks
results = manager.bulk_assign_ready_tasks(max_tasks=5)
```

## Constraint System

### File Access Control

The cornerstone of safe AI development is precise file access control:

#### Allowed Paths
Specify exactly which files the AI can modify:

```yaml
constraints:
  allowed_paths:
    - backend/apps/auth/models.py      # Specific file
    - backend/apps/auth/views.py       # Another specific file
    - backend/apps/auth/tests/         # Directory (use carefully)
    - frontend/src/components/Auth.tsx # Frontend files
```

#### Forbidden Paths
Explicitly prevent access to sensitive areas:

```yaml
constraints:
  forbidden_paths:
    - backend/settings/production.py   # Production settings
    - .env                            # Environment variables
    - scripts/deployment/             # Deployment scripts
    - docs/security/                  # Security documentation
```

#### Path Validation

The system validates paths for conflicts and safety:

- **Conflict Detection**: Flags paths that are both allowed and forbidden
- **Overly Broad Access**: Warns about root directory access (`/`, `*`, `**`)
- **Missing Constraints**: Ensures constraints are not empty
- **Path Existence**: Optionally validates paths exist in project

### Security Requirements

Critical security constraints prevent unauthorized code attribution:

```yaml
security:
  - "🚨 CRITICAL: NEVER include any AI, Claude, or assistant attribution anywhere"
  - "🚨 CRITICAL: NEVER use phrases like 'Generated with Claude', 'Co-Authored-By: Claude', etc."
  - "🚨 CRITICAL: Do not reference AI assistance in code, comments, commits, or any deliverables"
  - "🚨 CRITICAL: This is a SECURITY REQUIREMENT - violations will be automatically detected and removed"
  - "Follow OWASP security guidelines for data handling"
  - "Use secure password hashing (bcrypt, Argon2)"
  - "Implement proper input validation and sanitization"
```

### Testing Requirements

Specify exact tests that must pass:

```yaml
tests_to_make_pass:
  - backend/apps/auth/tests.py::TestUserRegistration::test_register_success
  - backend/apps/auth/tests.py::TestUserLogin::test_login_success
  - backend/apps/auth/tests.py::TestPasswordSecurity::test_password_hashing
  - backend/apps/auth/tests.py::TestJWTTokens::test_token_generation
```

**Test Specification Formats:**
- `file.py::TestClass::test_method` - Specific test method
- `file.py::TestClass` - All tests in class
- `file.py` - All tests in file
- `pytest backend/apps/auth/` - All tests in directory

### Definition of Done

Clear, measurable completion criteria:

```yaml
definition_of_done:
  - "All referenced tests pass with Django test runner"
  - "API endpoints return proper HTTP status codes (200, 400, 401, 404)"
  - "Database operations are atomic with proper error handling"
  - "Code follows project style guide (PEP 8, type hints)"
  - "API documentation automatically generated and updated"
  - "No security vulnerabilities in static analysis"
  - "Performance requirements met (< 200ms response time)"
```

### Role and Objective

Define AI persona and clear goals:

```yaml
role: "Senior Django backend engineer practicing strict TDD"
objective: "Implement complete user authentication system with JWT tokens and OAuth integration"

# Alternative roles:
role: "Frontend React developer with accessibility expertise"
role: "DevOps engineer with Docker and Kubernetes experience"
role: "Security engineer with OWASP compliance focus"
```

## Prompt Templates

### Template System

The system supports multiple AI platforms through customizable templates:

#### Claude Code Template (Default)
Optimized for Claude Code's development environment:

```
# T-001 — Feature Implementation
You are acting as a **Senior Django Developer**.

**Objective**: Implement user authentication with proper security

**Constraints and Boundaries**:

**File Access**:
- ✅ **Allowed**: `backend/apps/auth/models.py`
- ✅ **Allowed**: `backend/apps/auth/views.py`
- ❌ **Forbidden**: `backend/settings/production.py`

**Required Tests**:
- 🧪 **Test**: `backend/apps/auth/tests.py::test_login_success`

**Definition of Done**:
- ✅ **Done**: All tests pass
- ✅ **Done**: API returns proper status codes

**Security Requirements**:
- 🔒 NEVER include AI attribution
- 🔒 Follow OWASP guidelines

**Important**: Stay strictly within the allowed paths.
```

#### General Template
Compatible with most AI assistants:

```
# T-001 — Feature Implementation
Please act as a **Senior Django Developer**.

Objective: Implement user authentication with proper security

Constraints:
- Allowed file: backend/apps/auth/models.py
- Allowed file: backend/apps/auth/views.py
- Forbidden file: backend/settings/production.py
- Required test: backend/apps/auth/tests.py::test_login_success
- Definition of done: All tests pass

Please ensure all changes stay within the specified file boundaries.
```

#### Minimal Template
Stripped-down format for simple tasks:

```
# T-001 — Feature Implementation
Role: **Senior Django Developer**
Task: Implement user authentication with proper security
Rules:
- File: backend/apps/auth/models.py
- File: backend/apps/auth/views.py
- Test: backend/apps/auth/tests.py::test_login_success
- Done: All tests pass
```

### Custom Templates

Create custom templates for specific AI platforms or preferences:

```python
from generate_ai_prompt import PromptTemplate, AIPromptGenerator

custom_template = PromptTemplate(
    name='Enterprise Assistant',
    ai_assistant='Corporate AI',
    role_prefix='Your role is',
    objective_format='Primary goal: {}',
    constraints_header='Compliance Requirements:',
    path_format='- Authorized file: {}',
    test_format='- Mandatory test: {}',
    done_format='- Success criteria: {}',
    footer='Ensure full compliance with enterprise policies.'
)

generator = AIPromptGenerator()
generator.add_custom_template('enterprise', custom_template)

prompt = generator.generate_prompt(constraints, 'enterprise')
```

### Template Selection Guidelines

- **Claude Code**: Best for Django/Python projects with file system access
- **General**: Cross-platform compatibility, works with most AI assistants
- **Minimal**: Simple tasks, reduced prompt length
- **Custom**: Specific organizational requirements or AI platforms

## Workflow Integration

### GitHub Projects Integration

The system integrates with GitHub Projects for complete workflow automation:

#### Setup GitHub Integration

```bash
# Configure repository and project
python scripts/ai-assign.py T-001 --repo owner/repo --project-number 5

# With environment variables
export GITHUB_REPO="owner/repo"
export GITHUB_PROJECT="5"
python scripts/ai-assign.py T-001
```

#### Automatic Status Updates

When GitHub integration is configured:

1. **Task Assignment**: Updates GitHub Project item to "In Progress"
2. **Assignment Tracking**: Records assignment history and AI platform
3. **Constraint Validation**: Prevents assignment of invalid tasks
4. **Completion Workflow**: Enables marking tasks complete through GitHub

#### Bidirectional Sync

Pre-commit hooks ensure file-based planning stays synchronized:

```yaml
# .pre-commit-config.yaml
- id: sync-github-status
  name: Sync GitHub Project Status to Files
  entry: python scripts/sync-status-to-files.py owner/repo --project-number 5
  files: '^planning/.*\.md'
  require_serial: true
  pass_filenames: false
```

### File-Based Workflow

For projects without GitHub Projects:

1. **Local Assignment**: Generate prompts locally without status updates
2. **Manual Tracking**: Use task file YAML frontmatter for status
3. **Audit Trail**: Assignment history saved to `tmp/assignment-history.json`
4. **Portable Documentation**: Complete independence from GitHub

### Assignment History

Track all task assignments:

```json
{
  "assignments": [
    {
      "task_id": "T-001",
      "timestamp": "2025-09-28T16:22:25.047760",
      "ai_platform": "claude-code",
      "constraints_hash": "abc123...",
      "prompt_file": "tmp/T-001-prompt-claude-code.md",
      "status": "assigned"
    }
  ]
}
```

## Advanced Usage

### Bulk Assignment Operations

Efficiently assign multiple tasks:

```bash
# Assign up to 5 ready tasks
python scripts/ai-assign.py --bulk --max-tasks 5

# Specific AI platform
python scripts/ai-assign.py --bulk --ai gpt4 --max-tasks 3

# With filtering (requires GitHub integration)
python scripts/ai-assign.py --bulk --status todo --max-tasks 10
```

#### Bulk Assignment Logic

1. **Task Discovery**: Scans all available tasks
2. **Constraint Validation**: Only assigns tasks with valid constraints
3. **Priority Ordering**: Processes tasks in logical order
4. **Resource Management**: Respects max-tasks limit
5. **Error Handling**: Continues processing despite individual failures

### Custom Constraint Sources

Extend constraint parsing for custom sources:

```python
class CustomConstraintParser(AIConstraintParser):
    def parse_task_constraints(self, task_id: str) -> Optional[AIConstraints]:
        # Try default sources first
        constraints = super().parse_task_constraints(task_id)
        if constraints:
            return constraints

        # Custom source: config files
        config_file = self.project_root / "config" / f"{task_id}.yaml"
        if config_file.exists():
            return self._parse_config_file(config_file)

        # Custom source: external API
        return self._fetch_from_api(task_id)
```

### Constraint Inheritance

Advanced constraint inheritance patterns:

```yaml
# Parent story S-001
constraints:
  allowed_paths:
    - backend/apps/auth/
  security:
    - "No AI attribution"
  testing: "TDD approach"

---

# Child task T-001 (inherits and extends)
constraints:
  allowed_paths:
    - backend/apps/auth/models.py    # More specific than parent
  additional_tests:
    - test_custom_validation
```

### Validation Customization

Custom validation rules:

```python
class CustomValidator:
    def validate_paths(self, constraints: AIConstraints) -> List[str]:
        issues = []

        # Custom rule: no root directory access
        for path in constraints.allowed_paths:
            if path in ['/', '.', '*']:
                issues.append(f"Root directory access not allowed: {path}")

        # Custom rule: must include tests
        if not any('test' in path for path in constraints.allowed_paths):
            issues.append("Must include at least one test file")

        return issues
```

### Multi-Platform Prompt Generation

Generate prompts for multiple platforms simultaneously:

```python
def generate_multi_platform_prompts(constraints: AIConstraints, task_id: str):
    generator = AIPromptGenerator()
    platforms = ['claude-code', 'gpt4', 'claude-web']

    prompts = {}
    for platform in platforms:
        try:
            template = generator.ai_platforms[platform]['prompt_template']
            prompt = generator.generate_interactive_prompt(constraints, template)
            prompts[platform] = prompt

            # Save to platform-specific file
            prompt_file = f"tmp/{task_id}-prompt-{platform}.md"
            Path(prompt_file).write_text(prompt)

        except Exception as e:
            print(f"Failed to generate {platform} prompt: {e}")

    return prompts
```

## API Reference

### AIConstraints

Core data structure for task constraints.

#### Constructor

```python
AIConstraints(
    task_id: str,                    # Required: Task identifier
    title: str,                      # Required: Human-readable title
    role: str,                       # Required: AI role/persona
    objective: str,                  # Required: What to accomplish
    allowed_paths: List[str],        # Required: Files AI can modify
    forbidden_paths: List[str] = None,     # Optional: Forbidden files
    tests_to_make_pass: List[str] = None,  # Optional: Required tests
    definition_of_done: List[str] = None,  # Optional: Completion criteria
    security_requirements: List[str] = None, # Optional: Security rules
    database: str = None,            # Optional: Database requirements
    testing_approach: str = None     # Optional: Testing methodology
)
```

#### Methods

```python
# No public methods - data class with automatic defaults
```

### AIConstraintParser

Extracts constraints from planning files.

#### Constructor

```python
AIConstraintParser(project_root: Path = None)
```

#### Methods

```python
parse_task_constraints(task_id: str) -> Optional[AIConstraints]
"""Parse constraints for a given task ID."""

validate_constraints(constraints: AIConstraints) -> List[str]
"""Validate constraint completeness and return issues."""

list_available_tasks() -> List[str]
"""List all available task IDs."""
```

#### Private Methods

```python
_find_task_file(task_id: str) -> Optional[Path]
_find_story_file(story_id: str) -> Optional[Path]
_get_parent_story_id(task_id: str) -> Optional[str]
_extract_title(content: str) -> str
_extract_yaml_constraints(content: str) -> Optional[Dict]
_extract_ai_coding_brief(content: str) -> Optional[Dict]
_build_constraints_object(task_id: str, title: str, data: Dict) -> AIConstraints
```

### AIPromptGenerator

Converts constraints to formatted prompts.

#### Constructor

```python
AIPromptGenerator()
```

#### Methods

```python
generate_prompt(constraints: AIConstraints, template_name: str = 'claude-code') -> str
"""Generate a formatted AI prompt."""

generate_interactive_prompt(constraints: AIConstraints, template_name: str = 'claude-code') -> str
"""Generate interactive copy-paste format prompt."""

list_templates() -> Dict[str, str]
"""Return available prompt templates with descriptions."""

add_custom_template(name: str, template: PromptTemplate) -> None
"""Add a custom prompt template."""

validate_constraints_for_prompt(constraints: AIConstraints) -> List[str]
"""Validate constraints are suitable for prompt generation."""
```

### AIAssignmentManager

Main interface for task delegation.

#### Constructor

```python
AIAssignmentManager(
    project_root: Path = None,
    repo_name: str = None,
    project_number: int = None
)
```

#### Methods

```python
assign_task(
    task_id: str,
    ai_platform: str = 'claude-code',
    auto_open: bool = False,
    save_prompt: bool = False
) -> bool
"""Assign a task to an AI assistant."""

show_task_summary(task_id: str) -> bool
"""Show a summary of task constraints and readiness."""

list_available_tasks(status_filter: str = None) -> List[str]
"""List available tasks, optionally filtered by status."""

bulk_assign_ready_tasks(
    ai_platform: str = 'claude-code',
    max_tasks: int = 5
) -> Dict[str, bool]
"""Assign multiple ready tasks to AI platform."""
```

### PromptTemplate

Configuration for prompt formatting.

#### Constructor

```python
PromptTemplate(
    name: str,                      # Template display name
    ai_assistant: str,              # AI assistant name
    role_prefix: str,               # Role introduction format
    objective_format: str,          # Objective formatting
    constraints_header: str,        # Constraints section header
    path_format: str,               # File path formatting
    test_format: str,               # Test case formatting
    done_format: str,               # Definition of done formatting
    footer: str = ""                # Optional footer text
)
```

## Best Practices

### Constraint Design

#### Start Narrow, Expand Gradually

```yaml
# Good: Specific file access
allowed_paths:
  - backend/apps/auth/models.py
  - backend/apps/auth/views.py
  - backend/apps/auth/tests.py

# Avoid: Overly broad access
allowed_paths:
  - backend/
  - "*"
```

#### Use Explicit Forbidden Paths

```yaml
# Protect sensitive areas
forbidden_paths:
  - backend/settings/production.py
  - .env
  - scripts/deployment/
  - credentials/
```

#### Include Comprehensive Security Requirements

```yaml
security:
  - "🚨 CRITICAL: NEVER include any AI, Claude, or assistant attribution anywhere"
  - "🚨 CRITICAL: Follow OWASP security guidelines"
  - "🚨 CRITICAL: Use secure password hashing (bcrypt, Argon2)"
  - "🚨 CRITICAL: Implement proper input validation"
  - "🚨 CRITICAL: No hardcoded secrets or credentials"
```

### Task Organization

#### Story-Task Hierarchy

```
S-001 User Authentication (Story)
├── T-001 User Model Implementation
├── T-002 Registration API
├── T-003 Login API
└── T-004 JWT Token Management
```

#### Constraint Inheritance

- **Stories**: Define broad constraints and security requirements
- **Tasks**: Specify exact files and tests for focused work
- **Inheritance**: Tasks inherit story constraints by default
- **Overrides**: Tasks can override story constraints when needed

### Testing Strategy

#### Specify Exact Tests

```yaml
tests_to_make_pass:
  - backend/apps/auth/tests.py::TestUserModel::test_user_creation
  - backend/apps/auth/tests.py::TestUserModel::test_password_hashing
  - backend/apps/auth/tests.py::TestRegistration::test_valid_registration
  - backend/apps/auth/tests.py::TestLogin::test_successful_login
```

#### Include Integration Tests

```yaml
tests_to_make_pass:
  - backend/apps/auth/tests.py::TestAuthIntegration::test_full_auth_flow
  - backend/apps/auth/tests.py::TestAuthAPI::test_api_endpoints
```

### Prompt Quality

#### Clear, Actionable Objectives

```yaml
# Good: Specific and measurable
objective: "Implement user registration API with email validation, password hashing, and duplicate prevention"

# Avoid: Vague or ambiguous
objective: "Do user stuff"
```

#### Comprehensive Definition of Done

```yaml
definition_of_done:
  - "All specified tests pass with Django test runner"
  - "API endpoints return proper HTTP status codes (201, 400, 409)"
  - "Password hashing uses bcrypt with proper salt"
  - "Email validation prevents invalid formats"
  - "Duplicate email registration returns 409 Conflict"
  - "API documentation updated with endpoint specifications"
```

### Security Best Practices

#### AI Attribution Prevention

The system automatically includes attribution prevention in all prompts, but ensure your constraints explicitly forbid:

- AI assistant names in code, comments, or commits
- Attribution phrases like "Generated with Claude"
- Co-authored-by lines referencing AI assistants
- References to AI assistance in documentation

#### Sensitive File Protection

Always protect sensitive files:

```yaml
forbidden_paths:
  - backend/settings/production.py   # Production configuration
  - .env*                           # Environment variables
  - credentials/                    # Credential files
  - keys/                          # Encryption keys
  - scripts/deployment/            # Deployment scripts
  - docker/production/             # Production containers
```

### Template Selection

#### Platform-Specific Guidelines

- **Claude Code**:
  - Use for Django/Python projects
  - Leverages file system access
  - Best for complex development tasks

- **General**:
  - Cross-platform compatibility
  - Works with most AI assistants
  - Good for simple to moderate tasks

- **Minimal**:
  - Reduced prompt length
  - Fast processing
  - Suitable for focused, simple tasks

### Workflow Integration

#### GitHub Projects Setup

1. **Project Creation**: Create GitHub Project before task assignment
2. **Label Management**: Use consistent labels for task types
3. **Status Tracking**: Leverage automatic status updates
4. **Bidirectional Sync**: Enable pre-commit hooks for file synchronization

#### Local Development

1. **Prompt Saving**: Always save prompts for reference and debugging
2. **Assignment History**: Maintain records of task assignments
3. **Constraint Validation**: Validate constraints before assignment
4. **Bulk Operations**: Use bulk assignment for efficiency

## Troubleshooting

### Common Issues

#### No Constraints Found

```
❌ No constraints found for T-001
```

**Causes & Solutions:**

1. **Missing Task File**: Ensure `T-001-*.md` exists in `planning/tasks/`
2. **Invalid YAML**: Check YAML syntax in task frontmatter or story AI brief
3. **Missing Story**: Ensure parent story `S-001-*.md` exists with AI coding brief
4. **File Naming**: Verify files follow naming convention `{ID}-{description}.md`

**Debug Steps:**

```bash
# Check if task file exists
ls planning/tasks/T-001-*.md

# Validate YAML syntax
python scripts/ai-constraint-parser.py T-001 --validate

# Check parent story
ls planning/stories/S-001-*.md

# Test constraint parsing manually
python scripts/ai-constraint-parser.py T-001
```

#### YAML Parsing Errors

```
⚠️ Failed to parse AI Coding Brief YAML: while parsing a block mapping
```

**Common YAML Issues:**

1. **Missing Newlines**: Ensure proper line breaks between YAML keys
2. **Indentation**: Use consistent 2-space indentation
3. **Quotes**: Properly escape quotes in string values
4. **Colons**: Space required after colons in key-value pairs

**Fix Example:**

```yaml
# Wrong: Missing newline before security
testing: "TDD approach"  security:
  - "No AI attribution"

# Correct: Proper newline and indentation
testing: "TDD approach"
security:
  - "No AI attribution"
```

#### Validation Warnings

```
⚠️ Validation issues:
  - No allowed paths specified - AI will have no file access boundaries
  - Empty or missing objective - AI won't know what to accomplish
```

**Resolution:**

1. **Add Allowed Paths**: Specify exact files AI can modify
2. **Clear Objective**: Write specific, actionable objectives
3. **Complete Constraints**: Include all required constraint fields

#### Template Errors

```
❌ Template error: Unknown template: custom
```

**Solutions:**

1. **Use Valid Templates**: `claude-code`, `general`, `minimal`
2. **Register Custom Templates**: Add custom templates before use
3. **Check Spelling**: Verify template names are correct

#### GitHub Integration Issues

```
⚠️ Could not update task status in GitHub Project
```

**Common Causes:**

1. **Authentication**: GitHub CLI not authenticated
2. **Repository Access**: Insufficient permissions for repository
3. **Project Number**: Incorrect GitHub Project number
4. **Network Issues**: Connectivity problems

**Debug Steps:**

```bash
# Check GitHub CLI authentication
gh auth status

# Test repository access
gh repo view owner/repo

# Verify project exists
gh project list --owner owner

# Test project access
gh project view 5 --owner owner
```

### Advanced Debugging

#### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run your commands
python scripts/ai-assign.py T-001 --summary
```

#### Manual Constraint Inspection

```python
from scripts.ai_constraint_parser import AIConstraintParser

parser = AIConstraintParser()
constraints = parser.parse_task_constraints("T-001")

if constraints:
    print(f"Task ID: {constraints.task_id}")
    print(f"Role: {constraints.role}")
    print(f"Objective: {constraints.objective}")
    print(f"Allowed paths: {constraints.allowed_paths}")
    print(f"Security: {constraints.security_requirements}")
else:
    print("No constraints found")
```

#### Test Constraint Sources

```bash
# Test task-level constraints
python -c "
import yaml
content = open('planning/tasks/T-001-task.md').read()
if content.startswith('```yaml'):
    lines = content.split('\n')
    yaml_end = lines.index('```', 1)
    yaml_content = '\n'.join(lines[1:yaml_end])
    print('Task YAML:', yaml.safe_load(yaml_content))
"

# Test story-level constraints
python -c "
import re, yaml
content = open('planning/stories/S-001-story.md').read()
match = re.search(r'## AI Coding Brief\s*```yaml\s*(.*?)\s*```', content, re.DOTALL)
if match:
    print('Story YAML:', yaml.safe_load(match.group(1)))
"
```

### Error Recovery

#### Constraint Repair

```python
def repair_constraints(task_id: str):
    \"\"\"Repair common constraint issues.\"\"\"
    parser = AIConstraintParser()
    constraints = parser.parse_task_constraints(task_id)

    if not constraints:
        print(f"Creating minimal constraints for {task_id}")
        return AIConstraints(
            task_id=task_id,
            title=f"Repaired Task {task_id}",
            role="Senior Developer",
            objective="Complete the assigned task",
            allowed_paths=["TODO: Specify allowed files"]
        )

    # Fix common issues
    issues = parser.validate_constraints(constraints)
    for issue in issues:
        if "allowed_paths" in issue:
            constraints.allowed_paths = ["TODO: Specify allowed files"]
        if "objective" in issue:
            constraints.objective = "Complete the assigned task"

    return constraints
```

#### File Recovery

```bash
# Backup corrupted files
cp planning/tasks/T-001-task.md planning/tasks/T-001-task.md.backup

# Regenerate from template
cat > planning/tasks/T-001-task.md << 'EOF'
```yaml
last_synced: '2025-09-28T16:22:25.047760'
status: todo
```

# T-001 — Recovered Task

This task file was recovered due to parsing errors.

## Implementation
- [ ] Define task requirements
- [ ] Add proper constraints

## Links
- **S-001**: [Parent Story](../stories/S-001-story.md)
EOF
```

## Testing

### Running Tests

The system includes comprehensive tests for all components:

```bash
# Run all tests
python scripts/test_ai_system.py

# Run with verbose output
python scripts/test_ai_system.py --verbose

# Test specific component
python -c "
import sys
sys.path.append('scripts')
exec(open('scripts/test_ai_system.py').read())
test_constraint_creation()
"
```

### Test Coverage

The test suite covers:

- **AIConstraints**: Data class creation and defaults
- **AIConstraintParser**: File parsing and constraint extraction
- **AIPromptGenerator**: Template rendering and formatting
- **AIAssignmentManager**: Task delegation and workflow integration
- **End-to-End**: Complete workflow from files to prompts

### Test Structure

```python
# Unit Tests
class TestAIConstraints:
    def test_constraints_creation_with_required_fields(self)
    def test_constraints_creation_with_all_fields(self)

class TestAIConstraintParser:
    def test_parse_constraints_from_story_ai_brief(self)
    def test_parse_constraints_from_task_yaml_frontmatter(self)
    def test_validate_constraints_success(self)
    def test_validate_constraints_missing_fields(self)

# Integration Tests
class TestIntegration:
    def test_end_to_end_constraint_parsing_and_prompt_generation(self)
    def test_assignment_manager_integration(self)
    def test_bulk_assignment_workflow(self)
```

### Creating Custom Tests

Add tests for your specific use cases:

```python
def test_custom_constraint_parsing():
    """Test parsing of custom constraint format."""
    # Create test files
    # Parse constraints
    # Validate results
    pass

def test_custom_template_rendering():
    """Test custom prompt template."""
    # Create custom template
    # Generate prompt
    # Validate formatting
    pass
```

### Continuous Integration

Add to your CI pipeline:

```yaml
# .github/workflows/test.yml
name: Test AI Assignment System

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: pip install PyYAML
    - name: Run AI system tests
      run: python scripts/test_ai_system.py
```

## Contributing

### Development Setup

1. **Fork Repository**: Create your own fork for development
2. **Local Setup**: Clone and set up development environment
3. **Install Dependencies**: Ensure Python 3.8+ and PyYAML
4. **Run Tests**: Verify everything works before changes

### Code Standards

- **Python Style**: Follow PEP 8 with type hints
- **Documentation**: Include docstrings for all public methods
- **Testing**: Add tests for new functionality
- **Security**: Never compromise constraint validation or security requirements

### Contribution Guidelines

1. **Feature Requests**: Open issue describing the enhancement
2. **Bug Reports**: Include reproduction steps and error messages
3. **Pull Requests**: Include tests and documentation updates
4. **Security Issues**: Report privately for security-related bugs

### Architecture Extensions

#### Adding New AI Platforms

```python
# In ai-assign.py AIAssignmentManager.__init__()
self.ai_platforms['new-platform'] = {
    'name': 'New AI Platform',
    'url': 'https://new-ai-platform.com',
    'prompt_template': 'general',  # or create custom template
    'instructions': 'Copy prompt and paste into New AI Platform'
}
```

#### Custom Constraint Sources

```python
class DatabaseConstraintParser(AIConstraintParser):
    def parse_task_constraints(self, task_id: str) -> Optional[AIConstraints]:
        # Try database source
        constraints = self._fetch_from_database(task_id)
        if constraints:
            return constraints

        # Fallback to file-based parsing
        return super().parse_task_constraints(task_id)
```

#### Enhanced Validation

```python
class EnhancedValidator:
    def validate_constraints(self, constraints: AIConstraints) -> List[str]:
        issues = []

        # Custom validation rules
        if self._check_security_compliance(constraints):
            issues.append("Security compliance check failed")

        if self._validate_test_coverage(constraints):
            issues.append("Insufficient test coverage")

        return issues
```

### Release Process

1. **Version Update**: Update version numbers in scripts
2. **Documentation**: Update README and changelog
3. **Testing**: Run full test suite
4. **Tagging**: Create git tag for release
5. **Distribution**: Update package distribution if applicable

---

## Appendix

### Sample Files

#### Complete Story Example

```markdown
```yaml
last_synced: '2025-09-28T16:22:25.047760'
status: todo
```

# S-001 — User Authentication System

**As a** platform administrator
**I want** to implement secure user authentication
**So that** users can safely access the system with proper access controls

## Acceptance Criteria

- [ ] Users can register with email and password
- [ ] Users can login with valid credentials
- [ ] Passwords are securely hashed and stored
- [ ] JWT tokens are generated for authenticated sessions
- [ ] Invalid login attempts are properly handled
- [ ] Registration prevents duplicate email addresses

## Definition of Done

- [ ] All authentication tests pass
- [ ] API endpoints return proper HTTP status codes
- [ ] Password security follows OWASP guidelines
- [ ] JWT tokens have appropriate expiration
- [ ] API documentation is updated
- [ ] Security review completed

## AI Coding Brief

```yaml
role: "Senior Django backend engineer practicing strict TDD"
objective: "Implement complete user authentication system with JWT tokens, proper security, and comprehensive testing"
constraints:
  allowed_paths:
    - backend/apps/auth/models.py
    - backend/apps/auth/views.py
    - backend/apps/auth/serializers.py
    - backend/apps/auth/urls.py
    - backend/apps/auth/tests.py
    - backend/apps/auth/migrations/
  forbidden_paths:
    - backend/settings/production.py
    - .env
    - credentials/
  database: "Use Django ORM with PostgreSQL, ensure atomic transactions"
  testing: "Write Django tests first, then implement minimal code to pass"
  security:
    - "🚨 CRITICAL: NEVER include any AI, Claude, or assistant attribution anywhere"
    - "🚨 CRITICAL: Use bcrypt for password hashing with proper salt"
    - "🚨 CRITICAL: JWT tokens must expire appropriately (1 hour access, 7 days refresh)"
    - "🚨 CRITICAL: Implement rate limiting for login attempts"
    - "🚨 CRITICAL: Validate all input data and sanitize output"
tests_to_make_pass:
  - backend/apps/auth/tests.py::TestUserModel::test_user_creation
  - backend/apps/auth/tests.py::TestUserModel::test_password_hashing
  - backend/apps/auth/tests.py::TestRegistration::test_register_success
  - backend/apps/auth/tests.py::TestRegistration::test_register_duplicate_email
  - backend/apps/auth/tests.py::TestLogin::test_login_success
  - backend/apps/auth/tests.py::TestLogin::test_login_invalid_credentials
  - backend/apps/auth/tests.py::TestJWTTokens::test_token_generation
  - backend/apps/auth/tests.py::TestJWTTokens::test_token_expiration
definition_of_done:
  - "All referenced tests pass with Django test runner"
  - "Password hashing uses bcrypt with minimum 12 rounds"
  - "JWT tokens expire after 1 hour (access) and 7 days (refresh)"
  - "API endpoints return proper HTTP status codes (201, 200, 400, 401, 409)"
  - "Registration API prevents duplicate email with 409 Conflict"
  - "Login API implements rate limiting (5 attempts per minute)"
  - "All user input is validated and sanitized"
  - "API documentation updated with authentication endpoints"
```
```

#### Complete Task Example

```markdown
```yaml
last_synced: '2025-09-28T16:22:25.047760'
status: todo
role: "Senior Django backend engineer with authentication expertise"
objective: "Implement User model with secure password handling and JWT integration"
constraints:
  allowed_paths:
    - backend/apps/auth/models.py
    - backend/apps/auth/tests.py
  tests_to_make_pass:
    - backend/apps/auth/tests.py::TestUserModel::test_user_creation
    - backend/apps/auth/tests.py::TestUserModel::test_password_hashing
  definition_of_done:
    - "User model created with proper fields"
    - "Password hashing implemented with bcrypt"
    - "Model tests pass completely"
```

# T-001 — User Model Implementation for S-001

## Prerequisites

- [ ] Review Django User model best practices
- [ ] Understand bcrypt password hashing requirements
- [ ] Set up Django auth app structure
- [ ] Review JWT integration requirements

## Implementation Tasks

### Core Model Development
- [ ] Create custom User model extending AbstractUser
- [ ] Add email field as primary identifier (USERNAME_FIELD)
- [ ] Implement secure password hashing with bcrypt
- [ ] Add user metadata fields (created_at, updated_at, is_verified)
- [ ] Configure proper model meta options

### Password Security
- [ ] Implement bcrypt password hashing with minimum 12 rounds
- [ ] Add password validation (length, complexity)
- [ ] Ensure passwords are never stored in plain text
- [ ] Add password history tracking (prevent reuse)

### Testing Implementation
- [ ] Write test for user creation with valid data
- [ ] Write test for password hashing verification
- [ ] Write test for email uniqueness constraint
- [ ] Write test for user authentication
- [ ] Write test for invalid data handling

### Database Integration
- [ ] Create initial migration for User model
- [ ] Test migration rollback/forward compatibility
- [ ] Verify database constraints are properly enforced
- [ ] Test model relationships and foreign keys

## Verification Steps

- [ ] All model tests pass: `python manage.py test backend.apps.auth.tests.TestUserModel`
- [ ] Migration applies cleanly: `python manage.py migrate`
- [ ] User creation works via Django admin
- [ ] Password hashing uses bcrypt algorithm
- [ ] Email uniqueness is enforced at database level

## Links

- **S-001**: [User Authentication Story](../stories/S-001-user-authentication.md)
- **Design**: [Authentication Architecture](../../docs/design/authentication.md)
- **Tests**: [Authentication Test Suite](../../backend/apps/auth/tests.py)
```

### Configuration Examples

#### Complete .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: local
    hooks:
      - id: sync-github-status
        name: Sync GitHub Project Status to Files
        entry: python scripts/sync-status-to-files.py owner/repo --project-number 5
        language: system
        files: '^planning/.*\.md'
        require_serial: true
        pass_filenames: false

      - id: validate-ai-constraints
        name: Validate AI Constraints
        entry: python scripts/validate-all-constraints.py
        language: system
        files: '^planning/.*\.md'
        pass_filenames: false
```

#### Complete .gitignore for AI System

```
# AI Assignment System
tmp/
*-prompt-*.md
assignment-history.json
constraint-cache.json

# AI Generated Content (if needed)
ai-generated/
*.ai-backup

# Prompt Files
prompts/
*.prompt
```

---

*This documentation covers the complete AI Assignment System. For additional support, please refer to the troubleshooting section or create an issue in the project repository.*
