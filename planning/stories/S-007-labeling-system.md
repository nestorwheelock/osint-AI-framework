# S-007 — Labeling & Filtering System

**As a** OSINT researcher
**I want** to manually label and filter collected web pages and entities
**So that** I can organize findings by relevance, credibility, and investigation themes

## Acceptance Criteria
- [ ] When I view web pages, I can assign predefined and custom labels
- [ ] When I view entities, I can mark them as relevant, false positive, or key subject
- [ ] When I apply filters, only content matching selected criteria is displayed
- [ ] When I create custom labels, they are available for future use
- [ ] When labels are applied, they persist across sessions and team members
- [ ] When filtering by multiple criteria, results use logical AND/OR operations

## Definition of Done
- [ ] Label management system with predefined categories
- [ ] Web page labeling with user interface integration
- [ ] Entity labeling and relevance scoring
- [ ] Advanced filtering with multiple criteria support
- [ ] Custom label creation and management
- [ ] Label persistence and audit trail
- [ ] Unit tests cover labeling logic and edge cases
- [ ] Integration tests verify database persistence
- [ ] E2E tests confirm user interface functionality

## Dependencies
- Design section: [Labeling System Architecture](../../docs/design/osint-platform.md#core-services)
- Story: S-004 (Web pages to label), S-006 (Entities to label)
- Database: Label and relationship tables

## Links
- PRD: [/docs/product/osint-platform.md](../../docs/product/osint-platform.md)
- Design: [/docs/design/osint-platform.md](../../docs/design/osint-platform.md)
- Data Model: [/docs/data-model.md](../../docs/data-model.md)
- Tasks: [/planning/tasks/T-007-labeling-system.md](../tasks/T-007-labeling-system.md)
- Related: [S-004: Web Scraping](S-004-web-scraping.md), [S-006: Entity Extraction](S-006-entity-extraction.md)

## Test Plan

### Unit Tests (pytest)
- `test_create_predefined_labels`
- `test_create_custom_labels`
- `test_apply_labels_to_webpages`
- `test_apply_labels_to_entities`
- `test_filter_by_single_label`
- `test_filter_by_multiple_labels_and_or`
- `test_label_audit_trail`

### Integration Tests (pytest + database)
- `test_label_persistence_across_sessions`
- `test_bulk_labeling_operations`
- `test_label_statistics_and_counts`

### E2E Tests (Playwright)
- `test_label_webpages_in_ui`
- `test_filter_results_by_labels`
- `test_create_custom_labels_workflow`

## AI Coding Brief
```yaml
role: "Senior full-stack engineer with UI and database expertise."
objective: "Implement comprehensive labeling and filtering system."
constraints:
  allowed_paths:
    - backend/app/models/label.py
    - backend/app/routes/labels.py
    - backend/app/services/labeling/
    - backend/app/tests/test_labeling.py
  dependencies: "SQLAlchemy relationships, query optimization"
  testing: "Test complex filtering queries and UI interactions"  security:
    - "🚨 CRITICAL: NEVER include any AI, Claude, or assistant attribution anywhere"
    - "🚨 CRITICAL: NEVER use phrases like 'Generated with Claude', 'Co-Authored-By: Claude', etc."
    - "🚨 CRITICAL: Do not reference AI assistance in code, comments, commits, or any deliverables"
    - "🚨 CRITICAL: This is a SECURITY REQUIREMENT - violations will be automatically detected and removed"
tests_to_make_pass:
  - backend/app/tests/test_labeling.py::test_label_crud_operations
  - backend/app/tests/test_labeling.py::test_filtering_logic
  - backend/app/tests/test_labeling.py::test_bulk_operations
definition_of_done:
  - "All referenced tests pass in CI"
  - "Labeling system supports complex filtering scenarios"
  - "UI provides intuitive labeling and filtering experience"
  - "Database queries are optimized for large datasets"
  - "No attribution or AI references in code/commits"
```

## Technical Notes

### Label Data Model
```python
class Label(Base):
    id: UUID
    name: str
    description: Optional[str]
    color: str  # Hex color for UI display
    category: LabelCategory  # RELEVANCE, CREDIBILITY, THEME, CUSTOM
    is_system: bool  # True for predefined labels
    created_by: Optional[str]  # User identifier
    created_at: datetime

class WebPageLabel(Base):
    web_page_id: UUID
    label_id: UUID
    applied_by: str
    applied_at: datetime
    confidence: Optional[float]  # For AI-suggested labels

class EntityLabel(Base):
    entity_id: UUID
    label_id: UUID
    applied_by: str
    applied_at: datetime
    relevance_score: Optional[int]  # 1-5 scale
```

### Predefined Label Categories
```python
SYSTEM_LABELS = {
    "RELEVANCE": [
        {"name": "Highly Relevant", "color": "#22c55e"},
        {"name": "Somewhat Relevant", "color": "#eab308"},
        {"name": "Not Relevant", "color": "#ef4444"},
        {"name": "Needs Review", "color": "#8b5cf6"}
    ],
    "CREDIBILITY": [
        {"name": "Verified Source", "color": "#059669"},
        {"name": "Reliable", "color": "#0891b2"},
        {"name": "Questionable", "color": "#ea580c"},
        {"name": "Disinformation", "color": "#dc2626"}
    ],
    "CONTENT_TYPE": [
        {"name": "News Article", "color": "#3b82f6"},
        {"name": "Social Media", "color": "#8b5cf6"},
        {"name": "Forum Post", "color": "#06b6d4"},
        {"name": "Official Document", "color": "#10b981"}
    ]
}
```

### Filtering API
```python
class FilterQuery:
    def __init__(self):
        self.labels: List[UUID] = []
        self.label_operator: str = "AND"  # AND, OR
        self.date_range: Optional[DateRange] = None
        self.content_types: List[str] = []
        self.language: Optional[str] = None
        self.relevance_min: Optional[int] = None

    def build_query(self) -> Query:
        """Build SQLAlchemy query from filter criteria."""
```

### API Endpoints
```
POST   /labels                              - Create new label
GET    /labels                              - List all labels
PUT    /labels/{label_id}                   - Update label
DELETE /labels/{label_id}                   - Delete label

POST   /pages/{page_id}/labels/{label_id}   - Apply label to page
DELETE /pages/{page_id}/labels/{label_id}   - Remove label from page
GET    /pages/filter                        - Filter pages by labels

POST   /entities/{entity_id}/labels/{label_id} - Apply label to entity
DELETE /entities/{entity_id}/labels/{label_id} - Remove label from entity
GET    /entities/filter                         - Filter entities by labels
```

### UI Components
- **Label Picker**: Multi-select dropdown with color coding
- **Filter Bar**: Advanced filtering with multiple criteria
- **Label Manager**: Create and edit custom labels
- **Bulk Actions**: Apply labels to multiple items at once
- **Label Analytics**: Statistics on label usage and distribution