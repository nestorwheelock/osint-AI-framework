---
name: Backend Development Task
about: Create a task for backend API, database, or service implementation
title: "[T-XXX] Backend Task: "
labels: ["task", "backend", "api"]
assignees: []
---

## Task Overview
**Story Reference**: S-XXX - Story Name
**Epic**: OSINT Research Platform
**Estimated Hours**: XX-XX hours
**Priority**: [Highest/High/Medium/Low]

## Implementation Phases

### Phase 1: API Design & Testing (X hours)
- [ ] Define API endpoints and schemas
- [ ] Write API contract tests
- [ ] Create test fixtures and mock data
- [ ] Implement test database setup

### Phase 2: Core Implementation (X hours)
- [ ] Implement data models and schemas
- [ ] Create API route handlers
- [ ] Add business logic and validation
- [ ] Implement error handling

### Phase 3: Integration & Optimization (X hours)
- [ ] Database integration and migrations
- [ ] Performance optimization
- [ ] Security implementation
- [ ] Documentation updates

## API Specification

### Endpoints
```
METHOD /path/{id}    - Description
METHOD /path         - Description
```

### Data Models
```python
class ModelName(Base):
    id: UUID
    field: Type
    created_at: datetime
```

### Request/Response Examples
```json
{
  "example": "request body"
}
```

## Testing Requirements

### Unit Tests (pytest)
- [ ] `test_endpoint_success_case`
- [ ] `test_endpoint_validation_errors`
- [ ] `test_endpoint_not_found`
- [ ] `test_model_creation_validation`

### Integration Tests
- [ ] End-to-end API workflow tests
- [ ] Database transaction tests
- [ ] Authentication and authorization tests
- [ ] Performance and load tests

### API Contract Tests
- [ ] OpenAPI schema validation
- [ ] Request/response format verification
- [ ] Error response consistency
- [ ] Status code correctness

## Database Requirements

### Schema Changes
```sql
-- Migration SQL if needed
CREATE TABLE example (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
```

### Indexes and Performance
- [ ] Required database indexes
- [ ] Query optimization
- [ ] Connection pooling configuration
- [ ] Performance benchmarks

## Security Implementation
- [ ] Input validation and sanitization
- [ ] Authentication middleware
- [ ] Authorization checks
- [ ] Rate limiting
- [ ] SQL injection prevention
- [ ] XSS protection

## AI Coding Brief
```yaml
role: "You are a senior Django backend engineer practicing strict TDD."
objective: "Implement secure, performant Django REST Framework endpoints with proper testing."
constraints:
  allowed_paths:
    - backend/apps/*/models.py
    - backend/apps/*/views.py
    - backend/apps/*/serializers.py
    - backend/apps/*/urls.py
    - backend/apps/*/services.py
    - backend/apps/*/tests.py
  framework: "Django with Django REST Framework and PostgreSQL"
  testing: "Write Django tests first, then implement minimal code to pass"
  security:
    - "NEVER include author attribution in commits or code"
    - "Do not reference AI assistance in any deliverables"
    - "Implement proper input validation and error handling"
tests_to_make_pass:
  - backend/apps/*/tests.py
definition_of_done:
  - "All referenced tests pass with Django test runner"
  - "API endpoints return proper HTTP status codes"
  - "Database operations are atomic with proper error handling"
  - "DRF API documentation is automatically generated"
  - "Security best practices are implemented"
  - "Code coverage > 95%"
  - "No attribution or AI references in code/commits"
```

## Performance Targets
- **Response Time**: < 200ms (95th percentile)
- **Throughput**: Handle X requests/second
- **Database Queries**: < 100ms average
- **Memory Usage**: Stay within container limits

## Completion Criteria
- [ ] All API endpoints implemented and tested
- [ ] Database schema updated with migrations
- [ ] Integration tests passing
- [ ] Performance targets met
- [ ] Security requirements implemented
- [ ] OpenAPI documentation complete
- [ ] Code review completed and approved

---
**Links**:
- Task File: `planning/tasks/T-XXX-task-name.md`
- Related Story: `planning/stories/S-XXX-story-name.md`
- API Design: `docs/design/osint-platform.md`
- Data Model: `docs/data-model.md`