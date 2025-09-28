# S-001 — Create Subject

**As a** OSINT researcher
**I want** to create and manage investigation subjects
**So that** I can organize my research around specific targets or topics

## Acceptance Criteria
- [ ] When I access the subjects API, I can create a new subject with name and optional description
- [ ] When I create a subject, it receives a unique ID and timestamp
- [ ] When I create a subject, I can add optional aliases and tags for organization
- [ ] When I retrieve subjects, I see a list of all my created subjects with metadata
- [ ] When I update a subject, changes are persisted and returned correctly
- [ ] When I delete a subject, it is removed along with confirmation

## Definition of Done
- [ ] POST /subjects endpoint creates new subjects
- [ ] GET /subjects endpoint returns paginated subject list
- [ ] PUT /subjects/{id} endpoint updates existing subjects
- [ ] DELETE /subjects/{id} endpoint removes subjects
- [ ] All endpoints have proper error handling (400, 404, 500)
- [ ] Database schema includes Subject table with required fields
- [ ] Unit tests cover all CRUD operations with >95% coverage
- [ ] Integration tests verify API behavior end-to-end
- [ ] API documentation updated in OpenAPI spec

## Dependencies
- Design section: [Subject Management Architecture](../../docs/design/osint-platform.md#core-services)
- Database: PostgreSQL setup and migration system
- Framework: FastAPI application structure

## Links
- PRD: [/docs/product/osint-platform.md](../../docs/product/osint-platform.md)
- Design: [/docs/design/osint-platform.md](../../docs/design/osint-platform.md)
- Data Model: [/docs/data-model.md](../../docs/data-model.md)
- Tasks: [/planning/tasks/T-001-create-subject.md](../tasks/T-001-create-subject.md)

## Test Plan

### Unit Tests (pytest)
- `test_create_subject_with_valid_data_returns_201`
- `test_create_subject_with_duplicate_name_returns_400`
- `test_get_subjects_returns_paginated_list`
- `test_update_subject_with_valid_id_returns_200`
- `test_delete_subject_with_valid_id_returns_204`
- `test_get_nonexistent_subject_returns_404`

### Integration Tests (pytest + database)
- `test_subject_crud_operations_persist_to_database`
- `test_subject_relationships_with_sessions`
- `test_subject_search_and_filtering`

### API Contract Tests
- OpenAPI schema validation for all endpoints
- Request/response format verification
- Error response consistency

## AI Coding Brief
```yaml
role: "You are a senior backend engineer practicing strict TDD."
objective: "Implement Subject CRUD operations with FastAPI and SQLAlchemy."
constraints:
  allowed_paths:
    - backend/app/models/
    - backend/app/routes/subjects.py
    - backend/app/schemas/
    - backend/app/tests/test_subjects.py
  database: "Use SQLAlchemy ORM with PostgreSQL"
  testing: "Write tests first, then implement minimal code to pass"
  security:
    - "NEVER include author attribution in commits or code"
    - "Do not reference AI assistance in any deliverables"
tests_to_make_pass:
  - backend/app/tests/test_subjects.py::test_create_subject_success
  - backend/app/tests/test_subjects.py::test_get_subjects_list
  - backend/app/tests/test_subjects.py::test_update_subject_success
  - backend/app/tests/test_subjects.py::test_delete_subject_success
definition_of_done:
  - "All referenced tests pass in CI"
  - "API endpoints return proper HTTP status codes"
  - "Database operations are atomic with proper error handling"
  - "OpenAPI documentation is automatically generated"
  - "No attribution or AI references in code/commits"
```

## Technical Notes

### Data Model Requirements
```python
class Subject(Base):
    id: UUID (primary key)
    name: str (required, max 255 chars)
    description: Optional[str] (max 1000 chars)
    aliases: List[str] (JSON array)
    tags: List[str] (JSON array)
    created_at: datetime
    updated_at: datetime
```

### API Endpoints
```
POST   /subjects          - Create new subject
GET    /subjects          - List subjects (paginated)
GET    /subjects/{id}     - Get specific subject
PUT    /subjects/{id}     - Update subject
DELETE /subjects/{id}     - Delete subject
```

### Error Handling
- 400: Invalid input data, duplicate names
- 404: Subject not found
- 422: Validation errors
- 500: Database connection issues