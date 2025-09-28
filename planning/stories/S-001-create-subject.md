```yaml
last_synced: '2025-09-28T17:42:31.115088'
status: todo
```

# S-001 — Create Subject

**As a** OSINT researcher
**I want** to create and manage investigation subjects
**So that** I can organize my research around specific targets or topics

<!-- Test comment for pre-commit hook verification -->

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
role: "You are a senior Django backend engineer practicing strict TDD."
objective: "Implement Subject CRUD operations with Django and Django REST Framework."
constraints:
  allowed_paths:
    - backend/apps/subjects/models.py
    - backend/apps/subjects/views.py
    - backend/apps/subjects/serializers.py
    - backend/apps/subjects/urls.py
    - backend/apps/subjects/tests.py
  database: "Use Django ORM with PostgreSQL"
  testing: "Write Django tests first, then implement minimal code to pass"
  security:
    - "[CRITICAL] NEVER include any AI, Claude, or assistant attribution anywhere"
    - "[CRITICAL] NEVER use phrases like 'Generated with Claude', 'Co-Authored-By: Claude', etc."
    - "[CRITICAL] Do not reference AI assistance in code, comments, commits, or any deliverables"
    - "[CRITICAL] This is a SECURITY REQUIREMENT - violations will be automatically detected and removed"
  professional_standards:
    - "[REQUIRED] NO EMOJIS in any code, documentation, comments, or deliverables"
    - "[REQUIRED] Use text alternatives: [SUCCESS], [FAIL], [WARNING], [INFO], [CRITICAL]"
    - "[REQUIRED] Professional formatting only: **bold**, *italic*, `code`"
    - "[REQUIRED] All deliverables must be enterprise-appropriate and LaTeX-compatible"
tests_to_make_pass:
  - backend/apps/subjects/tests.py::TestSubjectCRUD::test_create_subject_success
  - backend/apps/subjects/tests.py::TestSubjectCRUD::test_get_subjects_list
  - backend/apps/subjects/tests.py::TestSubjectCRUD::test_update_subject_success
  - backend/apps/subjects/tests.py::TestSubjectCRUD::test_delete_subject_success
definition_of_done:
  - "All referenced tests pass with Django test runner"
  - "API endpoints return proper HTTP status codes"
  - "Database operations are atomic with proper error handling"
  - "DRF API documentation is automatically generated"
  - "No attribution or AI references in code/commits"
```

## Technical Notes

### Data Model Requirements
```python
class Subject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=1000, blank=True, null=True)
    aliases = models.JSONField(default=list, blank=True)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subjects'
        ordering = ['-created_at']
```

### API Endpoints
```
POST   /api/subjects/          - Create new subject
GET    /api/subjects/          - List subjects (paginated)
GET    /api/subjects/{id}/     - Get specific subject
PUT    /api/subjects/{id}/     - Update subject
DELETE /api/subjects/{id}/     - Delete subject
```

### Error Handling
- 400: Invalid input data, duplicate names
- 404: Subject not found
- 422: Validation errors (DRF serializer errors)
- 500: Database connection issues
