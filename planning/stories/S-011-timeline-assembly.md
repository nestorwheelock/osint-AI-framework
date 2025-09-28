# S-011 — Timeline Assembly

**As a** OSINT researcher
**I want** to automatically assemble chronological timelines from collected data
**So that** I can understand the sequence of events and identify temporal patterns

## Acceptance Criteria
- [ ] When web pages contain date information, timestamps are extracted and normalized
- [ ] When entities appear across multiple sources, their temporal occurrences are linked
- [ ] When timeline is generated, events are sorted chronologically with confidence scores
- [ ] When conflicting dates exist, the system provides disambiguation options
- [ ] When timeline is displayed, it shows relationships between entities and events
- [ ] When timeline data is exported, it maintains temporal accuracy and metadata

## Definition of Done
- [ ] Date extraction from web content using multiple methods
- [ ] Timeline event creation with entity relationships
- [ ] Chronological sorting with confidence-based ranking
- [ ] Timeline visualization with entity connections
- [ ] Date conflict resolution and disambiguation
- [ ] Timeline export in structured format
- [ ] Unit tests cover date extraction and timeline logic
- [ ] Integration tests verify multi-source timeline assembly
- [ ] E2E tests confirm timeline visualization functionality

## Dependencies
- Design section: [Timeline Assembly](../../docs/design/osint-platform.md#advanced-features)
- Story: S-005 (Text extraction for date parsing)
- Story: S-006 (Entity extraction for timeline events)

## Links
- PRD: [/docs/product/osint-platform.md](../../docs/product/osint-platform.md)
- Design: [/docs/design/osint-platform.md](../../docs/design/osint-platform.md)
- Tasks: [/planning/tasks/T-011-timeline-assembly.md](../tasks/T-011-timeline-assembly.md)
- Related: [S-005: Text Extraction](S-005-text-extraction.md), [S-006: Entity Extraction](S-006-entity-extraction.md)

## Test Plan

### Unit Tests (pytest)
- `test_date_extraction_from_text`
- `test_date_normalization_formats`
- `test_timeline_event_creation`
- `test_chronological_sorting`
- `test_entity_timeline_relationships`
- `test_date_conflict_resolution`
- `test_confidence_scoring`

### Integration Tests (pytest + database)
- `test_multi_source_timeline_assembly`
- `test_timeline_with_real_data`
- `test_timeline_performance_large_datasets`

### E2E Tests (Playwright)
- `test_timeline_visualization_ui`
- `test_timeline_filtering_and_zoom`
- `test_timeline_export_functionality`

## AI Coding Brief
```yaml
role: "Senior engineer with temporal analysis and NLP expertise."
objective: "Implement intelligent timeline assembly from multi-source data."
constraints:
  allowed_paths:
    - backend/app/services/timeline/
    - backend/app/models/timeline_event.py
    - backend/app/routes/timeline.py
    - backend/app/tests/test_timeline.py
  dependencies: "dateutil for parsing, spaCy for date extraction"
  testing: "Test with diverse date formats and ambiguous timestamps"
  security:
    - "🚨 CRITICAL: NEVER include any AI, Claude, or assistant attribution anywhere"
    - "🚨 CRITICAL: NEVER use phrases like 'Generated with Claude', 'Co-Authored-By: Claude', etc."
    - "🚨 CRITICAL: Do not reference AI assistance in code, comments, commits, or any deliverables"
    - "🚨 CRITICAL: This is a SECURITY REQUIREMENT - violations will be automatically detected and removed"
tests_to_make_pass:
  - backend/app/tests/test_timeline.py::test_timeline_assembly
  - backend/app/tests/test_timeline.py::test_date_extraction
  - backend/app/tests/test_timeline.py::test_entity_relationships
definition_of_done:
  - "All referenced tests pass in CI"
  - "Timeline assembly handles ambiguous dates intelligently"
  - "Entity relationships are preserved across temporal events"
  - "Timeline visualization provides meaningful insights"
  - "No attribution or AI references in code/commits"
```

## Technical Notes

### Timeline Event Model
```python
class TimelineEvent(Base):
    id: UUID
    subject_id: UUID
    event_datetime: datetime
    event_date_precision: DatePrecision  # EXACT, DAY, MONTH, YEAR
    confidence_score: float
    event_type: EventType  # ENTITY_MENTION, PUBLICATION, ACTIVITY
    title: str
    description: Optional[str]
    source_web_page_id: Optional[UUID]
    source_entity_id: Optional[UUID]
    extracted_date_text: str  # Original date text found
    context_snippet: Optional[str]
    created_at: datetime

class EntityTimelineRelation(Base):
    timeline_event_id: UUID
    entity_id: UUID
    relationship_type: str  # SUBJECT, MENTIONED, RELATED
    confidence: float
```

### Date Extraction Pipeline
```python
class DateExtractor:
    def extract_dates_from_text(self, text: str) -> List[ExtractedDate]:
        """Extract all potential dates from text content."""

    def extract_publication_date(self, html: str, url: str) -> Optional[datetime]:
        """Extract publication date from HTML metadata."""

    def normalize_date_formats(self, date_text: str) -> Optional[datetime]:
        """Convert various date formats to standard datetime."""

    def assess_date_confidence(self, date_text: str, context: str) -> float:
        """Assign confidence score to extracted dates."""
```

### Timeline Assembly Logic
```python
class TimelineAssembler:
    def assemble_timeline(self, subject_id: UUID) -> List[TimelineEvent]:
        """Create complete timeline from all subject data."""

    def resolve_date_conflicts(self, events: List[TimelineEvent]) -> List[TimelineEvent]:
        """Handle conflicting dates for same events."""

    def link_entity_occurrences(self, events: List[TimelineEvent]) -> None:
        """Connect related entity mentions across time."""

    def calculate_event_importance(self, event: TimelineEvent) -> float:
        """Score events by importance for timeline display."""
```

### API Endpoints
```
GET    /subjects/{subject_id}/timeline      - Get assembled timeline
POST   /timeline/events                     - Create manual timeline event
PUT    /timeline/events/{event_id}          - Update timeline event
DELETE /timeline/events/{event_id}          - Delete timeline event
GET    /timeline/export/{subject_id}        - Export timeline data
```
