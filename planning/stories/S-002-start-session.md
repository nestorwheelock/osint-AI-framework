# S-002 — Start Investigation Session

**As a** OSINT researcher
**I want** to start an investigation session for a subject
**So that** I can organize and track a specific research workflow with configuration

## Acceptance Criteria
- [ ] When I create a session, I can associate it with an existing subject
- [ ] When I create a session, I can provide configuration parameters (search engines, limits, etc.)
- [ ] When I create a session, it receives a unique ID, status, and timestamps
- [ ] When I retrieve sessions, I can see all sessions for a subject with their status
- [ ] When I update session status, changes are persisted correctly
- [ ] When a session is active, I can track progress and intermediate results

## Definition of Done
- [ ] POST /subjects/{subject_id}/sessions endpoint creates new sessions
- [ ] GET /subjects/{subject_id}/sessions endpoint returns session list
- [ ] GET /sessions/{id} endpoint returns session details
- [ ] PUT /sessions/{id}/status endpoint updates session status
- [ ] Session model includes proper foreign key relationship to Subject
- [ ] Configuration is stored as JSON with validation
- [ ] Status tracking includes: created, running, paused, completed, failed
- [ ] Unit tests cover all session operations with >95% coverage
- [ ] Integration tests verify session workflow

## Dependencies
- Design section: [Session Management Architecture](../../docs/design/osint-platform.md#core-services)
- Story: S-001 (Subject must exist before creating sessions)
- Database: Session table with Subject foreign key

## Links
- PRD: [/docs/product/osint-platform.md](../../docs/product/osint-platform.md)
- Design: [/docs/design/osint-platform.md](../../docs/design/osint-platform.md)
- Data Model: [/docs/data-model.md](../../docs/data-model.md)
- Tasks: [/planning/tasks/T-002-start-session.md](../tasks/T-002-start-session.md)
- Related: [S-001: Create Subject](S-001-create-subject.md)

## Test Plan

### Unit Tests (pytest)
- `test_create_session_with_valid_subject_returns_201`
- `test_create_session_with_invalid_subject_returns_404`
- `test_create_session_with_valid_config_stores_json`
- `test_get_sessions_for_subject_returns_list`
- `test_update_session_status_changes_state`
- `test_session_status_transitions_are_valid`

### Integration Tests (pytest + database)
- `test_session_subject_relationship_integrity`
- `test_session_lifecycle_workflow`
- `test_session_config_persistence`

## AI Coding Brief
```yaml
role: "You are a senior backend engineer practicing strict TDD."
objective: "Implement Session management with proper Subject relationships."
constraints:
  allowed_paths:
    - backend/app/models/session.py
    - backend/app/routes/subjects.py (extend for sessions)
    - backend/app/schemas/session.py
    - backend/app/tests/test_sessions.py
  database: "Use SQLAlchemy with proper foreign key constraints"
  testing: "Write tests first, implement minimal working code"
  security:
    - "NEVER include author attribution in commits or code"
    - "Do not reference AI assistance in any deliverables"
tests_to_make_pass:
  - backend/app/tests/test_sessions.py::test_create_session_success
  - backend/app/tests/test_sessions.py::test_get_sessions_for_subject
  - backend/app/tests/test_sessions.py::test_update_session_status
definition_of_done:
  - "All referenced tests pass in CI"
  - "Session-Subject relationship is enforced in database"
  - "Configuration validation prevents invalid JSON"
  - "Status transitions follow business rules"
  - "No attribution or AI references in code/commits"
```

## Technical Notes

### Data Model Requirements
```python
class Session(Base):
    id: UUID (primary key)
    subject_id: UUID (foreign key to Subject)
    status: SessionStatus (enum: created, running, paused, completed, failed)
    config_json: dict (search engines, limits, filters)
    started_at: datetime
    finished_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    # Relationship
    subject: Subject
```

### Session Configuration Schema
```json
{
  "search_engines": ["google", "bing", "duckduckgo"],
  "max_pages_per_engine": 50,
  "rate_limit_delay": 2.0,
  "respect_robots_txt": true,
  "timeout_seconds": 30,
  "filters": {
    "languages": ["en", "es"],
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    }
  }
}
```

### Status Transitions
```
created → running → completed
created → running → paused → running → completed
created → running → failed
created → failed (on startup failure)
```

### API Endpoints
```
POST   /subjects/{subject_id}/sessions  - Create session for subject
GET    /subjects/{subject_id}/sessions  - List sessions for subject
GET    /sessions/{id}                   - Get session details
PUT    /sessions/{id}/status            - Update session status
PUT    /sessions/{id}/config            - Update session configuration
```