# Incremental Commit Workflow

**Document Type**: Development Policy & Core AI Prompt Integration
**Version**: 1.0
**Date**: September 28, 2025
**Status**: MANDATORY - Must be added to core AI prompt

---

## Core Development Mandate

**INCREMENTAL COMMIT PROTOCOL**: After every task with working tests, the following workflow is MANDATORY:

### Required Steps

1. **Run all tests** to verify functionality
2. **Git add** modified files
3. **Git commit** with descriptive message
4. **Git push** to remote repository
5. **Update kanban board** to sync project status

### Rationale

- **Preserves incremental progress** and prevents work loss
- **Creates trackable development history** for template extraction
- **Enables rollback** to any working state
- **Documents development velocity** and patterns
- **Facilitates collaborative development** and code review

---

## Implementation in AI Development

### Core AI Prompt Integration

This workflow MUST be integrated into the core AI prompt with the following language:

```
MANDATORY WORKFLOW: After completing any task with working tests:
1. Run tests to verify functionality
2. Git add modified files
3. Git commit with descriptive message
4. Git push to remote repository

This incremental commit protocol is non-negotiable and ensures all progress is preserved and trackable.
```

### Development Logger Integration

The development logger has been enhanced to track commit requirements:

```python
"commit_required": True  # MANDATORY: Every milestone requires commit
```

### Workflow Enforcement

- **Every task completion** with passing tests triggers commit requirement
- **No exceptions** - even small changes must be committed
- **Descriptive commit messages** that explain the change and its purpose
- **Template development** especially requires this for extraction analysis

---

## Commit Message Standards

### Format Template

```
<type>: <description>

<optional body with details>
<optional AI attribution>
```

### Commit Types

- `feat:` New feature implementation
- `fix:` Bug fix or correction
- `test:` Adding or updating tests
- `docs:` Documentation changes
- `refactor:` Code refactoring without feature changes
- `style:` Code style/formatting changes
- `chore:` Build, dependency, or maintenance tasks

### Examples

```bash
# Feature implementation
git commit -m "feat: implement Django search app foundation

- Add SearchQuery and SearchResult models
- Create comprehensive model tests (10/10 passing)
- Configure Django admin interface
- Add app to Django settings

 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Test implementation
git commit -m "test: add TDD test suite for enhanced kanban system

- Create 18 comprehensive test cases
- Test categorization, status mapping, workflow logic
- Mock GitHub API interactions
- All tests passing (18/18)

 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Development Session Tracking

### Workflow Logging

Every commit triggers logging entry:

```python
log_workflow_step(
    step="task_completion",
    description=f"Task completed: {task_description}",
    metadata={
        "tests_passing": tests_status,
        "files_modified": modified_files,
        "timestamp": datetime.now().isoformat(),
        "commit_required": True,  # MANDATORY
        "commit_completed": True   # Verification
    }
)
```

### Progress Metrics

- **Commit frequency** indicates development velocity
- **Test coverage** per commit ensures quality
- **File change patterns** inform template extraction
- **Time between commits** shows task complexity

---

## Template Extraction Benefits

### Development History Capture

- **Complete change history** for every template component
- **Decision point documentation** in commit messages
- **Incremental improvement tracking** across iterations
- **Reusability analysis** based on commit patterns

### Quality Assurance

- **Every commit has passing tests** - guaranteed code quality
- **No broken states** in development history
- **Rollback capability** to any functional point
- **Continuous integration** readiness

---

## Integration Requirements

### Global AI Instructions

This workflow MUST be added to `/home/nwheelo/.claude/CLAUDE.md`:

```markdown
## Incremental Commit Protocol (MANDATORY)

After every task with working tests:
1. Run tests to verify functionality
2. Git add modified files
3. Git commit with descriptive message
4. Git push to remote repository

NO EXCEPTIONS. This preserves progress and enables template extraction.
```

### Project Templates

All Django TDD templates must include:

- Pre-commit hooks for test verification
- Commit message templates
- Development workflow documentation
- Automated commit reminders

---

## Success Metrics

### Compliance Tracking

- **100% commit rate** after task completion
- **Zero broken commits** in development history
- **Consistent commit messages** following standards
- **Complete test coverage** for all commits

### Development Efficiency

- **Faster debugging** with granular history
- **Easier code review** with logical commit boundaries
- **Template extraction** simplified by clear history
- **Client confidence** through visible progress tracking

---

**This incremental commit workflow is fundamental to professional software development and MUST be integrated into the core AI development prompt for consistent application across all projects.**
