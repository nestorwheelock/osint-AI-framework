# Professional Code Standards

## Anti-Emoji Policy

**Rationale**: Emojis in professional software development create multiple issues:
- LaTeX/PDF generation failures
- Inconsistent rendering across systems
- Accessibility problems for screen readers
- Unprofessional appearance in enterprise environments
- Unicode compatibility issues
- Version control noise and merge conflicts

## Enforcement Rules

### Prohibited in ALL deliverables:
- Code files (.py, .js, .ts, .java, etc.)
- Documentation (.md, .rst, .txt)
- Comments and docstrings
- Commit messages
- Configuration files
- Test files
- API responses and schemas

### Alternatives for emphasis:
- `[CRITICAL]`, `[WARNING]`, `[INFO]` instead of [CRITICAL][WARNING][INFO]
- `[SUCCESS]`, `[FAIL]` instead of [SUCCESS][FAIL]
- `[NOTE]`, `[TODO]`, `[FIXME]` for annotations
- Standard markdown formatting (**bold**, *italic*, `code`)

### Pre-commit Hook Integration
```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: no-emojis
      name: Prevent emojis in code and docs
      entry: scripts/check-no-emojis.py
      language: python3
      files: \.(py|md|js|ts|txt|yml|yaml|json|rst)$
```

## Implementation

This standard should be added to all AI constraint templates to ensure professional deliverables.
