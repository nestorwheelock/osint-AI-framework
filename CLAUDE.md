# OSINT Framework - Claude Code Guidelines

## Project Overview

**Name**: OSINT Research Platform
**Description**: AI-assisted Open Source Intelligence research platform for systematic data collection, analysis, and reporting
**Tech Stack**: Django (Python), React (TypeScript), PostgreSQL, Docker, Redis
**Development Approach**: Test-Driven Development (TDD) with AI-assisted implementation

## Architecture & Core Components

### Backend (Django + PostgreSQL)
- **Location**: `backend/`
- **Framework**: Django with Django ORM and built-in migrations
- **Testing**: Django TestCase and pytest with >95% coverage requirement
- **Database**: PostgreSQL with Redis for caching and Celery job queues
- **Security**: Django authentication, input validation, no AI attribution

### Frontend (React + TypeScript)
- **Location**: `frontend/src/`
- **Framework**: React with TypeScript, Vite build system
- **Testing**: Jest + React Testing Library + Playwright E2E
- **Styling**: SCSS with BEM methodology and design system
- **Accessibility**: WCAG 2.1 AA compliance required

### Infrastructure (Docker + CI/CD)
- **Containerization**: Multi-stage Docker builds for development and production
- **CI/CD**: GitHub Actions with automated testing, security scanning, deployment
- **Databases**: PostgreSQL primary, Redis cache, development data seeding
- **Monitoring**: Health checks, performance metrics, error tracking

## Development Standards

### Code Style & Quality
- **Python**: Follow PEP 8, use black formatter, type hints required
- **TypeScript**: Strict mode enabled, ESLint + Prettier configuration
- **Testing**: Test-first development, comprehensive edge case coverage
- **Documentation**: Inline comments for complex logic, API documentation via OpenAPI

### Security Requirements
- **🚨 CRITICAL - AI ATTRIBUTION PROHIBITION**:
  - NEVER include any Claude, AI, or assistant attribution in code, comments, commits, or documentation
  - NEVER use phrases like "Generated with Claude", "Co-Authored-By: Claude", "Built with Claude Code", etc.
  - NEVER reference AI assistance, Claude mentions, or automated generation in any deliverables
  - NEVER add credits, thanks, or acknowledgments to Claude or AI tools
  - This is a SECURITY REQUIREMENT for compliance and legal reasons
- **Input Validation**: Sanitize all user inputs and API parameters
- **Authentication**: Implement proper JWT handling and session management
- **Database**: Use parameterized queries, implement proper access controls

### Performance Standards
- **API Response**: < 200ms (95th percentile)
- **Frontend Load**: < 2 seconds initial page load
- **Database Queries**: < 100ms average, proper indexing required
- **Bundle Size**: Optimize for production, code splitting implemented

## Project Structure & Planning System

### File-Based Planning (Source of Truth)
```
planning/
├── stories/           # User stories S-000 to S-015
├── tasks/            # Implementation tasks T-000 to T-015
├── backlog.md        # Epic overview and sprint planning
└── dependencies/     # Inter-story dependencies
```

### AI Coding Briefs
Each task file contains detailed AI coding briefs with:
- **Role**: Specific engineering role (backend, frontend, DevOps)
- **Objective**: Clear implementation goal
- **Constraints**: Allowed file paths, frameworks, security requirements
- **Tests to Pass**: Specific test files and methods
- **Definition of Done**: Acceptance criteria and quality gates

### Reference Documents
- **Design**: `docs/design/osint-platform.md` - System architecture and data models
- **Infrastructure**: `docs/infrastructure/` - Environment setup and deployment
- **API Docs**: Auto-generated OpenAPI specifications
- **Data Model**: `docs/data-model.md` - Database schema and relationships

## Task Implementation Workflow

### 1. Understand the Task
- Read the complete task file in `planning/tasks/T-XXX-*.md`
- Review linked user story in `planning/stories/S-XXX-*.md`
- Check dependencies and related design documents
- Understand the AI coding brief constraints and objectives

### 2. Test-Driven Development
- Write tests first based on acceptance criteria
- Implement minimal code to pass tests
- Refactor while maintaining test coverage
- Ensure all edge cases are covered

### 3. Implementation Guidelines
- Follow the specified file path constraints from AI coding brief
- Use existing patterns and conventions from codebase
- Implement proper error handling and validation
- Add comprehensive logging for debugging

### 4. Quality Assurance
- Run all tests and ensure >95% coverage
- Perform security validation (no injection vulnerabilities)
- Check performance against established targets
- Validate accessibility compliance (frontend tasks)

## Common Patterns & Utilities

### Backend Patterns
```python
# Standard Django view pattern
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ResourceCreateView(APIView):
    def post(self, request):
        serializer = ResourceSerializer(data=request.data)
        if serializer.is_valid():
            resource = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Standard Django model pattern
from django.db import models
import uuid

class Model(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'table_name'
```

### Frontend Patterns
```typescript
// Standard React component pattern
interface ComponentProps {
  data: DataType;
  onAction: (item: DataType) => void;
}

const Component: React.FC<ComponentProps> = ({ data, onAction }) => {
  const [state, setState] = useState<StateType>(initialState);
  // Component logic
};

// Standard API service pattern
export const apiService = {
  async getData(params: Parameters): Promise<Response> {
    // API call implementation with error handling
  }
};
```

### Error Handling
- **Backend**: Use Django's built-in exception handling and HTTP responses
- **Frontend**: Implement error boundaries and user-friendly error messages
- **Validation**: Django REST Framework serializers for backend, Zod schemas for frontend
- **Logging**: Django's logging framework with structured output

## Testing Strategies

### Backend Testing
- **Unit Tests**: Django TestCase for individual models and views
- **Integration Tests**: Database operations and API endpoints with Django's TestClient
- **API Tests**: Django REST Framework test utilities
- **Performance Tests**: Load testing for critical Django views

### Frontend Testing
- **Unit Tests**: Component logic and utility functions
- **Integration Tests**: Component interactions and API integration
- **E2E Tests**: Complete user workflows with Playwright
- **Accessibility Tests**: axe-core integration for WCAG compliance

### Infrastructure Testing
- **Container Tests**: Docker build and startup validation
- **Deployment Tests**: CI/CD pipeline validation
- **Security Tests**: Vulnerability scanning and penetration testing
- **Performance Tests**: Load testing and resource monitoring

## Debugging & Troubleshooting

### Common Issues
- **Database Connections**: Check connection strings and pool settings
- **API Authentication**: Verify JWT token handling and expiration
- **CORS Issues**: Ensure proper origin configuration
- **Performance**: Use profiling tools and monitoring dashboards

### Development Tools
- **Backend**: Django's test runner, black, mypy, bandit for security scanning
- **Frontend**: Jest, ESLint, Prettier, axe for accessibility testing
- **Database**: pgAdmin for PostgreSQL, Redis CLI for cache inspection
- **Monitoring**: Django logs, application metrics, error tracking

## Repository Etiquette

### Commit Messages
- Use conventional commit format: `type(scope): description`
- Reference issue numbers: `feat(backend): implement subject API (#123)`
- Keep commits atomic and focused
- Never include AI attribution or assistance references

### Pull Request Process
- Link to related GitHub issue
- Include comprehensive testing evidence
- Update documentation if needed
- Ensure CI/CD pipeline passes completely

### Code Review Guidelines
- Focus on security, performance, and maintainability
- Verify test coverage and quality
- Check adherence to project standards
- Validate accessibility and user experience

## Claude Code Integration

When using @claude mentions in issues or PRs:

### Effective Prompts
- **@claude review**: Request code review with security and performance focus
- **@claude implement**: Ask for feature implementation following TDD approach
- **@claude fix**: Request bug fix with root cause analysis
- **@claude test**: Ask for comprehensive test coverage and edge cases
- **@claude optimize**: Request performance optimization with benchmarks

### Context Awareness
Claude has access to:
- Complete project planning documentation
- Design documents and architecture diagrams
- Existing codebase patterns and conventions
- Task-specific AI coding briefs and constraints
- Security and quality requirements

### Best Practices
- Provide specific context about the task or issue
- Reference relevant files and documentation
- Specify performance or security requirements
- Request explanation of implementation decisions
- Ask for test coverage and validation strategies

## ⚠️ CRITICAL SECURITY REMINDER

**NEVER ADD AI ATTRIBUTION**: This project has a strict NO AI ATTRIBUTION policy for security and compliance reasons. Never include any references to Claude, AI assistance, or automated generation in:
- Code comments
- Commit messages
- Documentation
- Pull request descriptions
- Issue comments
- Any project deliverables

Violation of this policy creates security and legal risks. All AI attribution will be automatically detected and removed by our compliance systems.