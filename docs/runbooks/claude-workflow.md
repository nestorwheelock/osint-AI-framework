# Claude Code Workflow Guide

## Quick Start Commands

### For implementing a new user story:
```
Read /docs/product/osint-platform.md and /docs/design/osint-platform.md. Then open /planning/stories/S-001-create-subject.md. Confirm the acceptance criteria, list assumptions/questions, and produce a numbered execution plan for S-001 only. Do not start any other story. When you're done, update the GitHub issue with a status note and any blockers.

SECURITY REQUIREMENT: Never include author attribution, AI assistance references, or any identifying markers in commits, code, or documentation.
```

### For development environment setup:
```
Set up the development environment by following the backend and frontend setup instructions. Run all tests to ensure everything works. Report any setup issues or missing dependencies.
```

### For running the complete test suite:
```
Run the complete test suite (backend pytest + frontend Playwright). Fix any failing tests and ensure all acceptance criteria are met. Document any test coverage gaps.
```

## Story Implementation Workflow

### Phase 1: Planning Review
1. **Read Context Documents**
   - Product Requirements: `/docs/product/osint-platform.md`
   - System Design: `/docs/design/osint-platform.md`
   - Development Conventions: `/standards/conventions.md`

2. **Understand the Story**
   - Read the specific story file: `/planning/stories/S-XXX-story-name.md`
   - Review acceptance criteria and definition of done
   - Check dependencies on other stories
   - Read the task breakdown: `/planning/tasks/T-XXX-story-name.md`

### Phase 2: Implementation Preparation
1. **Verify Prerequisites**
   - Ensure all dependent stories are complete
   - Check that required tools and libraries are available
   - Verify development environment is working

2. **Plan Approach**
   - List assumptions about implementation
   - Identify potential risks or blockers
   - Create numbered execution steps
   - Estimate effort and complexity

### Phase 3: Test-Driven Development
1. **Write Failing Tests First**
   - Follow the test plan in the story
   - Create unit tests for all new functionality
   - Add integration tests for API endpoints
   - Write E2E tests for user workflows

2. **Implement Minimal Code**
   - Write only enough code to make tests pass
   - Follow the file path constraints in the AI brief
   - Adhere to project conventions and patterns

3. **Refactor and Polish**
   - Improve code quality while keeping tests green
   - Add proper error handling and validation
   - Update documentation and code comments

### Phase 4: Quality Assurance
1. **Run All Tests**
   - Backend: `cd backend && source .venv/bin/activate && pytest -q`
   - Frontend: `cd frontend && npx playwright test`
   - Ensure 100% of story tests pass

2. **Code Quality Checks**
   - Linting: `cd backend && source .venv/bin/activate && ruff check .`
   - Type checking: `cd backend && source .venv/bin/activate && mypy app/`
   - Format check: `cd backend && source .venv/bin/activate && black --check .`

3. **Manual Testing**
   - Test API endpoints with curl/httpie
   - Verify database operations work correctly
   - Check OpenAPI documentation generation

### Phase 5: Documentation and Handoff
1. **Update Documentation**
   - Add API endpoint documentation
   - Update any relevant design documents
   - Document any architectural decisions made

2. **GitHub Issue Updates**
   - Mark completed acceptance criteria as done
   - Add progress notes and decision log
   - Note any blockers or questions for review
   - Link to pull request when ready

## Common Commands

### Backend Development
```bash
# Setup virtual environment
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

# Run tests
pytest -q
pytest app/tests/test_subjects.py -v

# Start development server
uvicorn app.main:app --reload

# Code quality
ruff check .
mypy app/
black --check .
```

### Frontend E2E Testing
```bash
# Setup
cd frontend
npm install
npx playwright install

# Run tests
npx playwright test
npx playwright test --headed
npx playwright test --debug
```

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/S-001-create-subject

# Commit with convention
git commit -m "feat(subjects): implement CRUD operations

Implements S-001: Create Subject with full test coverage
- Add Subject model with SQLAlchemy
- Create FastAPI CRUD endpoints
- Add comprehensive test suite"

# Push and create PR
git push -u origin feature/S-001-create-subject
gh pr create --title "S-001: Create Subject" --body "Implements subject CRUD operations..."
```

## Decision Logging Template

When implementing a story, document key decisions in the GitHub issue:

```markdown
## Decision Log - 2024-MM-DD

**Choice:** Selected SQLAlchemy ORM over raw SQL
**Reasoning:** Better type safety, migration support, and team familiarity
**Trade-offs:** Slightly more overhead, but acceptable for this use case
**Alternatives Considered:**
- Raw SQL with asyncpg: Too much boilerplate
- Tortoise ORM: Less mature ecosystem

**Implementation Notes:**
- Used UUID primary keys for all models
- Added created_at/updated_at timestamps automatically
- Configured connection pooling for production scaling
```

## Troubleshooting

### Common Issues

**Tests failing with import errors:**
```bash
cd backend && source .venv/bin/activate && pip install -e .[dev]
```

**Playwright browsers not installed:**
```bash
cd frontend && npx playwright install
```

**Database connection issues:**
```bash
# Check if postgres is running
sudo systemctl status postgresql
# Or start development with SQLite for testing
```

**Type checking errors:**
```bash
# Add type hints to function signatures
# Use Optional[] for nullable fields
# Import types from typing module
```

### Getting Help

1. **Check Documentation**
   - Review the story and task files
   - Check design documents for architecture decisions
   - Look at existing code patterns in the repository

2. **Ask Specific Questions**
   - "How should I handle validation for the Subject.name field?"
   - "What's the preferred error response format for 400 errors?"
   - "Should I use sync or async database operations here?"

3. **Update Issues**
   - Mark questions clearly in GitHub issues
   - Provide context about what you've tried
   - Tag specific areas that need clarification

## Success Criteria

A story is considered complete when:

- [ ] All acceptance criteria are met and tested
- [ ] All tests pass (unit, integration, E2E)
- [ ] Code follows project conventions
- [ ] Documentation is updated
- [ ] GitHub issue is updated with progress
- [ ] No linting or type checking errors
- [ ] Manual testing confirms functionality works
- [ ] Decision log documents key choices made