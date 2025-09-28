# AI Assignment System

Automated task delegation system that provides AI assistants with precise constraints, boundaries, and requirements extracted from your planning files.

## Overview

This system enables safe, scoped AI development by:

1. **Parsing constraints** from YAML frontmatter and AI coding briefs
2. **Generating formatted prompts** for different AI platforms
3. **Enforcing file boundaries** to prevent scope creep
4. **Integrating with GitHub Projects** for workflow automation
5. **Supporting multiple AI platforms** (Claude Code, GPT-4, etc.)

## Core Components

### 1. AI Constraint Parser (`ai-constraint-parser.py`)

Extracts AI development constraints from planning files:

```bash
# Parse constraints for a specific task
python scripts/ai-constraint-parser.py T-001

# List all available tasks
python scripts/ai-constraint-parser.py --list

# Validate constraint completeness
python scripts/ai-constraint-parser.py T-001 --validate
```

**Constraint Sources:**
- Task file YAML frontmatter (highest priority)
- Parent story AI coding brief section
- Fallback defaults

### 2. Prompt Generator (`generate-ai-prompt.py`)

Converts parsed constraints into AI-ready prompts:

```bash
# Generate Claude Code prompt
python scripts/generate-ai-prompt.py T-001

# Use different template
python scripts/generate-ai-prompt.py T-001 --template general

# Generate interactive copy-paste format
python scripts/generate-ai-prompt.py T-001 --interactive

# Save prompt to file
python scripts/generate-ai-prompt.py T-001 --output tmp/T-001-prompt.md
```

**Available Templates:**
- `claude-code`: Optimized for Claude Code development environment
- `general`: Compatible with most AI assistants
- `minimal`: Stripped-down format for simple tasks

### 3. AI Assignment CLI (`ai-assign.py`)

Main interface for task delegation with full workflow integration:

```bash
# Assign task to Claude Code (default)
python scripts/ai-assign.py T-001

# Use different AI platform
python scripts/ai-assign.py T-001 --ai gpt4

# Auto-open browser and save prompt
python scripts/ai-assign.py T-001 --open --save

# Show task summary before assignment
python scripts/ai-assign.py T-001 --summary

# List all available tasks
python scripts/ai-assign.py --list

# Bulk assign multiple ready tasks
python scripts/ai-assign.py --bulk --max-tasks 3
```

## Constraint System

### File Access Control

Constraints specify exactly which files the AI can modify:

```yaml
constraints:
  allowed_paths:
    - backend/apps/subjects/models.py
    - backend/apps/subjects/views.py
    - backend/apps/subjects/serializers.py
  forbidden_paths:
    - backend/settings/
    - docs/
```

### Security Requirements

Critical security constraints prevent AI attribution:

```yaml
security:
  - "🚨 CRITICAL: NEVER include any AI, Claude, or assistant attribution anywhere"
  - "🚨 CRITICAL: NEVER use phrases like 'Generated with Claude', 'Co-Authored-By: Claude', etc."
  - "🚨 CRITICAL: Do not reference AI assistance in code, comments, commits, or any deliverables"
  - "🚨 CRITICAL: This is a SECURITY REQUIREMENT - violations will be automatically detected and removed"
```

### Testing Requirements

Specify which tests must pass:

```yaml
tests_to_make_pass:
  - backend/apps/subjects/tests.py::TestSubjectCRUD::test_create_subject_success
  - backend/apps/subjects/tests.py::TestSubjectCRUD::test_get_subjects_list
```

### Definition of Done

Clear completion criteria:

```yaml
definition_of_done:
  - "All referenced tests pass with Django test runner"
  - "API endpoints return proper HTTP status codes"
  - "Database operations are atomic with proper error handling"
```

## AI Platform Support

### Claude Code (Recommended)
- **Template**: `claude-code`
- **URL**: https://claude.com/claude-code
- **Best for**: Django/Python development with file access

### Claude Web
- **Template**: `general`
- **URL**: https://claude.ai
- **Best for**: General development tasks

### GPT-4/ChatGPT
- **Template**: `general`
- **URL**: https://chat.openai.com
- **Best for**: Cross-platform compatibility

## Workflow Integration

### GitHub Projects Integration

When configured with repository and project number:

```bash
python scripts/ai-assign.py T-001 --repo owner/repo --project-number 5
```

The system will:
1. Update task status to "In Progress" when assigned
2. Track assignment history
3. Sync with bidirectional GitHub Project hooks

### File-Based Workflow

Tasks are automatically saved to `tmp/` directory:
- `tmp/T-001-prompt-claude-code.md` - Generated prompts
- `tmp/assignment-history.json` - Assignment tracking
- Files are git-ignored for privacy

## Advanced Usage

### Bulk Assignment

Assign multiple ready tasks at once:

```bash
# Assign up to 5 ready tasks to Claude Code
python scripts/ai-assign.py --bulk --max-tasks 5

# Bulk assign to different platform
python scripts/ai-assign.py --bulk --ai gpt4 --max-tasks 3
```

### Custom Templates

Add custom prompt templates in `generate-ai-prompt.py`:

```python
custom_template = PromptTemplate(
    name='Custom Assistant',
    ai_assistant='My AI',
    role_prefix='Act as a',
    objective_format='Goal: {}',
    constraints_header='Rules:',
    path_format='- Edit: {}',
    test_format='- Test: {}',
    done_format='- Complete: {}',
    footer='Stay within boundaries.'
)

prompt_generator.add_custom_template('custom', custom_template)
```

### Constraint Validation

Comprehensive validation catches common issues:

```bash
python scripts/ai-constraint-parser.py T-001 --validate
```

**Common Issues Detected:**
- Missing or empty constraints
- Overly broad file access
- Conflicting allowed/forbidden paths
- Missing definition of done
- Security requirement gaps

## Integration with Planning Files

### Story-Level Constraints

Stories contain AI coding briefs with reusable constraints:

```markdown
## AI Coding Brief
```yaml
role: "You are a senior Django backend engineer practicing strict TDD."
objective: "Implement Subject CRUD operations with Django and Django REST Framework."
constraints:
  allowed_paths:
    - backend/apps/subjects/models.py
    - backend/apps/subjects/views.py
  database: "Use Django ORM with PostgreSQL"
  testing: "Write Django tests first, then implement minimal code to pass"
```
```

### Task-Level Overrides

Tasks can override or extend story constraints:

```yaml
# Task-specific constraints in YAML frontmatter
constraints:
  allowed_paths:
    - backend/apps/subjects/models.py  # More specific than story
  tests_to_make_pass:
    - backend/apps/subjects/tests.py::TestSpecificFunction
```

## Best Practices

### 1. Constraint Design
- **Start narrow**: Begin with minimal file access, expand as needed
- **Be specific**: Use exact file paths rather than directory wildcards
- **Include tests**: Always specify which tests must pass
- **Security first**: Never omit security requirements

### 2. Template Selection
- **Claude Code**: Use for Django/Python projects with file system access
- **General**: Use for cross-platform compatibility
- **Minimal**: Use for simple, focused tasks

### 3. Workflow Integration
- **Use summaries**: Always review task summary before assignment
- **Save prompts**: Keep copies for reference and debugging
- **Bulk assign**: Leverage bulk assignment for efficiency
- **Monitor constraints**: Regularly validate constraint completeness

### 4. Prompt Quality
- **Clear objectives**: Write specific, actionable objectives
- **Complete constraints**: Include all necessary boundaries
- **Test coverage**: Specify comprehensive test requirements
- **Documentation**: Maintain clear definition of done

## Troubleshooting

### Common Issues

**No constraints found:**
```bash
❌ No constraints found for T-001
```
- Check task file has YAML frontmatter or parent story has AI coding brief
- Verify YAML syntax is valid
- Ensure story-task relationship is correct (T-001 → S-001)

**Validation warnings:**
```bash
⚠️ No allowed paths specified - AI will have no file access boundaries
```
- Add `allowed_paths` to constraints
- Review and fix constraint completeness
- Use `--validate` flag to identify issues

**Template errors:**
```bash
❌ Template error: Unknown template: custom
```
- Check template name is valid: `claude-code`, `general`, `minimal`
- Verify custom templates are properly registered

### Debug Mode

Enable verbose output for troubleshooting:

```bash
python scripts/ai-assign.py T-001 --summary  # Review constraints first
python scripts/ai-constraint-parser.py T-001 --validate  # Check validation
python scripts/generate-ai-prompt.py T-001 --output debug.md  # Save for review
```

## Security Considerations

### AI Attribution Prevention

The system enforces strict security requirements to prevent AI attribution in deliverables:

- **Automated detection**: Security constraints are automatically included
- **Template enforcement**: All templates include attribution warnings
- **Validation checks**: System validates security requirement presence
- **Pre-commit hooks**: Git hooks can detect and block attribution

### File Access Control

Constraints provide defense against scope creep:

- **Path validation**: Only specified files can be modified
- **Boundary enforcement**: Clear warnings about file restrictions
- **Audit trails**: Assignment history tracks what was allowed
- **Template reuse**: Consistent constraints across similar tasks

### Prompt Security

Generated prompts are handled securely:

- **Local storage**: Prompts saved to git-ignored `tmp/` directory
- **No network**: No prompts sent to external services automatically
- **User control**: Manual copy-paste maintains control
- **Clean history**: Temporary files prevent commit pollution

This AI assignment system provides a safe, efficient way to delegate development tasks to AI assistants while maintaining strict boundaries and quality standards.
