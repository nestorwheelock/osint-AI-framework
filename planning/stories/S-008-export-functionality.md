# S-008 — Export Functionality

**As a** OSINT researcher
**I want** to export investigation results in multiple formats
**So that** I can share findings, create reports, and integrate with external analysis tools

## Acceptance Criteria
- [ ] When I complete an investigation, I can export results to JSONL format
- [ ] When exporting, I can select specific data types (pages, entities, labels)
- [ ] When export is requested, structured data includes all metadata and relationships
- [ ] When large datasets are exported, the system handles pagination and streaming
- [ ] When exports are created, they are stored temporarily for download
- [ ] When export jobs run, progress tracking shows completion status

## Definition of Done
- [ ] POST /subjects/{subject_id}/export endpoint accepts export requests
- [ ] JSONL export format with comprehensive data structure
- [ ] Selective export options for different data types
- [ ] Export job tracking with progress updates
- [ ] File streaming for large exports to prevent memory issues
- [ ] Temporary file cleanup after download completion
- [ ] Unit tests cover export logic and data serialization
- [ ] Integration tests verify complete export workflows
- [ ] E2E tests confirm download functionality

## Dependencies
- Design section: [Export Engine Architecture](../../docs/design/osint-platform.md#core-services)
- Story: S-001 (Subjects), S-004 (Pages), S-006 (Entities), S-007 (Labels)
- Database: All investigation data models

## Links
- PRD: [/docs/product/osint-platform.md](../../docs/product/osint-platform.md)
- Design: [/docs/design/osint-platform.md](../../docs/design/osint-platform.md)
- Data Model: [/docs/data-model.md](../../docs/data-model.md)
- Tasks: [/planning/tasks/T-008-export-functionality.md](../tasks/T-008-export-functionality.md)
- Related: [S-007: Labeling System](S-007-labeling-system.md)

## Test Plan

### Unit Tests (pytest)
- `test_jsonl_export_format_structure`
- `test_selective_export_by_data_type`
- `test_export_includes_all_relationships`
- `test_large_dataset_streaming`
- `test_export_job_progress_tracking`
- `test_temporary_file_cleanup`
- `test_export_data_validation`

### Integration Tests (pytest + database)
- `test_complete_subject_export`
- `test_export_with_filters_applied`
- `test_concurrent_export_jobs`

### E2E Tests (Playwright)
- `test_export_request_and_download`
- `test_export_progress_ui`
- `test_export_options_selection`

## AI Coding Brief
```yaml
role: "Senior backend engineer with data export and streaming expertise."
objective: "Implement robust data export system with multiple formats."
constraints:
  allowed_paths:
    - backend/app/services/exporter/
    - backend/app/models/export_job.py
    - backend/app/routes/export.py
    - backend/app/tests/test_exporter.py
  dependencies: "Streaming responses, background jobs, file handling"
  testing: "Test large dataset handling and format validation"
  security:
    - "NEVER include author attribution in commits or code"
    - "Do not reference AI assistance in any deliverables"
tests_to_make_pass:
  - backend/app/tests/test_exporter.py::test_jsonl_export_success
  - backend/app/tests/test_exporter.py::test_streaming_large_exports
  - backend/app/tests/test_exporter.py::test_export_job_tracking
definition_of_done:
  - "All referenced tests pass in CI"
  - "Export system handles large datasets efficiently"
  - "JSONL format is valid and includes all required data"
  - "Export jobs provide accurate progress tracking"
  - "No attribution or AI references in code/commits"
```

## Technical Notes

### Export Job Data Model
```python
class ExportJob(Base):
    id: UUID
    subject_id: UUID
    format: ExportFormat  # JSONL, CSV, PDF (future)
    data_types: List[str]  # ["pages", "entities", "labels"]
    filter_criteria: Optional[dict]
    status: ExportStatus  # PENDING, RUNNING, COMPLETED, FAILED
    progress_percent: int
    total_records: Optional[int]
    processed_records: int
    file_path: Optional[str]
    file_size: Optional[int]
    created_by: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
```

### JSONL Export Format
```jsonl
{"type": "subject", "id": "uuid", "name": "Investigation Name", "created_at": "2024-01-15T10:00:00Z"}
{"type": "session", "id": "uuid", "subject_id": "uuid", "status": "completed", "config": {...}}
{"type": "webpage", "id": "uuid", "subject_id": "uuid", "url": "https://example.com", "title": "Page Title", "extracted_text": "...", "labels": ["relevant", "news"]}
{"type": "entity", "id": "uuid", "subject_id": "uuid", "web_page_id": "uuid", "entity_type": "PERSON", "value": "John Smith", "confidence": 0.95, "labels": ["key-subject"]}
```

### Export Options
```python
class ExportOptions:
    data_types: List[str] = ["pages", "entities", "labels"]
    include_html: bool = False
    include_screenshots: bool = False
    date_range: Optional[DateRange] = None
    label_filters: List[str] = []
    entity_types: List[str] = []
    min_confidence: Optional[float] = None
    max_records: Optional[int] = None
```

### Streaming Export Implementation
```python
class StreamingExporter:
    async def export_jsonl(self, subject_id: UUID, options: ExportOptions) -> AsyncIterator[str]:
        """Stream JSONL export line by line to handle large datasets."""

    async def export_with_progress(self, job_id: UUID) -> None:
        """Background job with progress tracking."""

    def cleanup_expired_exports(self) -> None:
        """Remove export files older than 24 hours."""
```

### API Endpoints
```
POST   /subjects/{subject_id}/export        - Create export job
GET    /export-jobs/{job_id}                - Get export job status
GET    /export-jobs/{job_id}/download       - Download export file
DELETE /export-jobs/{job_id}                - Cancel export job
GET    /export-jobs                         - List user's export jobs
```

### File Management
- **Storage**: Temporary directory with auto-cleanup
- **Naming**: `{subject_name}_{timestamp}_{job_id}.jsonl`
- **Compression**: Gzip compression for large files
- **Security**: Signed URLs for secure download access
- **Cleanup**: Automatic deletion after 24 hours or download