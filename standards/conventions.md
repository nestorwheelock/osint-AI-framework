# Development Conventions

## Naming Conventions

### Files & Directories
- **Snake_case** for Python files: `analysis_run.py`
- **kebab-case** for config files: `docker-compose.yml`
- **PascalCase** for TypeScript components: `SearchResults.tsx`
- **lowercase** for directories: `backend/app/routes/`

### Code Structure
- **Classes**: PascalCase (`AnalysisRun`, `WebPageProcessor`)
- **Functions/Methods**: snake_case (`extract_entities`, `fetch_web_page`)
- **Variables**: snake_case (`session_id`, `analysis_results`)
- **Constants**: UPPER_SNAKE_CASE (`DEFAULT_TIMEOUT`, `MAX_RETRIES`)

### Database
- **Tables**: singular snake_case (`subject`, `analysis_run`)
- **Columns**: snake_case (`created_at`, `content_hash`)
- **Foreign Keys**: `{table}_id` pattern (`subject_id`, `web_page_id`)

## Git Workflow

### Branch Naming
- **Features**: `feature/S-001-create-subject`
- **Bugfixes**: `fix/login-redirect-issue`
- **Hotfixes**: `hotfix/security-patch-v1.2.1`
- **Releases**: `release/v1.2.0`

### Commit Messages
```
<type>(<scope>): <description>

<body>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:** feat, fix, docs, style, refactor, test, chore

**Examples:**
- `feat(search): add meta-search endpoint with deduplication`
- `fix(scraper): handle timeout errors in Playwright driver`
- `test(entities): add coverage for extraction pipeline`

### PR Guidelines
- Link to user story: "Implements S-001: Create Subject"
- Include test evidence: screenshots, test output
- Tag reviewers based on area: @backend-team, @frontend-team
- Ensure CI passes before requesting review

## Code Quality

### Python (Backend)
- **Linting**: ruff with strict settings
- **Formatting**: black with 88-character lines
- **Type Hints**: Required for all public functions
- **Testing**: pytest with >90% coverage target
- **Imports**: isort with alphabetical ordering

### TypeScript (Frontend E2E)
- **Linting**: eslint with TypeScript rules
- **Formatting**: prettier with 2-space indentation
- **Testing**: Playwright with page object pattern
- **Types**: Strict TypeScript configuration

### Documentation
- **Docstrings**: Google style for Python functions
- **API Docs**: OpenAPI/Swagger generation from FastAPI
- **README**: Updated for each significant feature
- **ADRs**: Architecture Decision Records in `/docs/design/`

## Testing Strategy

### Test-Driven Development
1. **Red**: Write failing test first
2. **Green**: Implement minimal code to pass
3. **Refactor**: Improve code while keeping tests green

### Test Categories
- **Unit Tests**: Fast, isolated, no external dependencies
- **Integration Tests**: Database and API interactions
- **E2E Tests**: Full user workflows with Playwright
- **Contract Tests**: API schema validation

### Test Naming
```python
def test_<what>_<when>_<expected>():
    # test_extract_entities_when_valid_html_returns_person_locations()
```

### Test Organization
```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # Database and API tests
├── fixtures/       # Shared test data
└── e2e/           # Playwright browser tests
```

## Labels & Issue Management

### GitHub Labels

**Type Labels:**
- `type:story` - User story implementation
- `type:task` - Technical task or subtask
- `type:bug` - Bug fixes
- `type:docs` - Documentation updates
- `type:refactor` - Code improvement without feature changes

**Status Labels:**
- `status:ready` - Ready for development
- `status:in-progress` - Currently being worked on
- `status:blocked` - Waiting for dependency or decision
- `status:review` - Code review in progress
- `status:testing` - QA testing phase
- `status:done` - Complete and merged

**Area Labels:**
- `area:backend` - FastAPI, database, API changes
- `area:frontend` - UI, E2E tests, user experience
- `area:infra` - CI/CD, deployment, infrastructure
- `area:ai` - ML models, entity extraction, analysis
- `area:scraping` - Web scraping, Playwright, data collection

**Priority Labels:**
- `priority:critical` - System down, security issues
- `priority:high` - MVP blockers, user-facing bugs
- `priority:medium` - Important features, performance
- `priority:low` - Nice-to-have, technical debt

### Issue Templates
- Use `.github/ISSUE_TEMPLATE/user_story.md` for features
- Include acceptance criteria and test plans
- Reference related PRD and design documents
- Add AI coding brief for Claude development

### Milestones
- `MVP v1.0` - Core OSINT features (US-001 through US-010)
- `v1.1` - Enhanced features (US-011 through US-014)
- `v2.0` - Future roadmap items

## Claude Code Integration

### Story Handoff Format
When giving Claude a story to implement:
1. **Context**: Link to PRD and design document
2. **Scope**: Specific story ID and acceptance criteria
3. **Constraints**: Allowed file paths and dependencies
4. **Definition of Done**: Test requirements and quality gates

### Decision Logging
Claude should document decisions in issue comments:
```markdown
## Decision Log - [Date]
**Choice:** Selected approach X over Y
**Reasoning:** Performance benefits outweigh complexity
**Trade-offs:** Slightly more memory usage
**Alternatives Considered:** Z was too complex, Y was too slow
```

### Progress Updates
Regular status updates in GitHub issues:
- ✅ Completed tasks with evidence
- 🔄 In-progress items with blockers
- ❓ Questions or clarifications needed
- 📝 Next steps and dependencies