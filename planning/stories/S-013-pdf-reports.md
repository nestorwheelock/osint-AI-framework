# S-013 — PDF Report Generation

**As a** OSINT researcher
**I want** to generate professional PDF reports from investigation results
**So that** I can share findings in a formatted, presentation-ready document

## Acceptance Criteria
- [ ] When I request a report, a formatted PDF is generated with investigation summary
- [ ] When PDF is created, it includes key findings, timeline, and entity relationships
- [ ] When report contains images, screenshots and charts are properly embedded
- [ ] When report is generated, it follows a professional template with branding
- [ ] When large datasets exist, report summarizes rather than listing everything
- [ ] When PDF is complete, it can be downloaded or shared via secure link

## Definition of Done
- [ ] PDF generation service using professional templating
- [ ] Report template with sections for summary, timeline, entities, evidence
- [ ] Image and chart embedding with proper formatting
- [ ] Executive summary generation from investigation data
- [ ] Configurable report templates and styling
- [ ] Secure PDF download and sharing functionality
- [ ] Unit tests cover PDF generation and formatting
- [ ] Integration tests verify complete report workflows
- [ ] E2E tests confirm report download functionality

## Dependencies
- Design section: [PDF Report Generation](../../docs/design/osint-platform.md#advanced-features)
- Story: S-008 (Export functionality foundation)
- Story: S-011 (Timeline data for reports)

## Links
- PRD: [/docs/product/osint-platform.md](../../docs/product/osint-platform.md)
- Design: [/docs/design/osint-platform.md](../../docs/design/osint-platform.md)
- Tasks: [/planning/tasks/T-013-pdf-reports.md](../tasks/T-013-pdf-reports.md)
- Related: [S-008: Export Functionality](S-008-export-functionality.md), [S-011: Timeline Assembly](S-011-timeline-assembly.md)

## Test Plan

### Unit Tests (pytest)
- `test_pdf_template_rendering`
- `test_image_embedding_functionality`
- `test_report_section_generation`
- `test_executive_summary_creation`
- `test_chart_generation_and_embedding`
- `test_pdf_styling_and_formatting`
- `test_large_dataset_summarization`

### Integration Tests (pytest + PDF libraries)
- `test_complete_report_generation`
- `test_multi_page_report_handling`
- `test_pdf_file_integrity`

### E2E Tests (Playwright)
- `test_report_generation_request_ui`
- `test_pdf_download_workflow`
- `test_report_template_selection`

## AI Coding Brief
```yaml
role: "Senior engineer with document generation and PDF expertise."
objective: "Implement professional PDF report generation system."
constraints:
  allowed_paths:
    - backend/app/services/reports/
    - backend/app/templates/pdf/
    - backend/app/routes/reports.py
    - backend/app/tests/test_reports.py
  dependencies: "ReportLab or WeasyPrint for PDF, Jinja2 for templates"
  testing: "Test PDF generation and verify document structure"
  security:
    - "NEVER include author attribution in commits or code"
    - "Do not reference AI assistance in any deliverables"
tests_to_make_pass:
  - backend/app/tests/test_reports.py::test_pdf_generation
  - backend/app/tests/test_reports.py::test_report_content
  - backend/app/tests/test_reports.py::test_image_embedding
definition_of_done:
  - "All referenced tests pass in CI"
  - "PDF reports have professional appearance and formatting"
  - "Reports accurately summarize investigation findings"
  - "Generated PDFs are valid and can be opened in standard viewers"
  - "No attribution or AI references in code/commits"
```

## Technical Notes

### Report Generation Models
```python
class ReportJob(Base):
    id: UUID
    subject_id: UUID
    report_type: ReportType  # EXECUTIVE, DETAILED, TIMELINE, ENTITY_FOCUSED
    template_id: UUID
    status: ReportStatus  # PENDING, GENERATING, COMPLETED, FAILED
    progress_percent: int
    file_path: Optional[str]
    file_size: Optional[int]
    page_count: Optional[int]
    generated_by: str
    generated_at: datetime
    expires_at: datetime  # Auto-delete after expiration
    download_count: int
    error_message: Optional[str]

class ReportTemplate(Base):
    id: UUID
    name: str
    description: str
    template_path: str
    is_system: bool
    sections: List[str]  # JSON list of section types
    styling_config: dict  # Colors, fonts, layout options
    created_by: str
    created_at: datetime
```

### PDF Generation Pipeline
```python
class PDFReportGenerator:
    def generate_report(self, subject_id: UUID, template_id: UUID) -> str:
        """Generate complete PDF report and return file path."""

    def create_executive_summary(self, subject: Subject) -> str:
        """Generate executive summary from investigation data."""

    def generate_entity_section(self, entities: List[Entity]) -> dict:
        """Create entity analysis section with charts."""

    def generate_timeline_section(self, timeline: List[TimelineEvent]) -> dict:
        """Create timeline visualization section."""

    def embed_evidence_images(self, web_pages: List[WebPage]) -> List[dict]:
        """Embed screenshots and relevant images."""
```

### Report Templates
```html
<!-- Executive Summary Template -->
<section class="executive-summary">
    <h1>Investigation Report: {{ subject.name }}</h1>
    <div class="summary-stats">
        <div class="stat">
            <span class="number">{{ stats.total_pages }}</span>
            <span class="label">Pages Analyzed</span>
        </div>
        <div class="stat">
            <span class="number">{{ stats.total_entities }}</span>
            <span class="label">Entities Extracted</span>
        </div>
    </div>
    <p class="summary-text">{{ executive_summary }}</p>
</section>

<!-- Timeline Section Template -->
<section class="timeline">
    <h2>Timeline of Events</h2>
    {% for event in timeline_events %}
    <div class="timeline-event">
        <div class="date">{{ event.date | format_date }}</div>
        <div class="content">
            <h3>{{ event.title }}</h3>
            <p>{{ event.description }}</p>
            <span class="source">Source: {{ event.source_url }}</span>
        </div>
    </div>
    {% endfor %}
</section>
```

### Chart Generation
```python
class ChartGenerator:
    def create_entity_distribution_chart(self, entities: List[Entity]) -> bytes:
        """Generate pie chart of entity types."""

    def create_timeline_chart(self, events: List[TimelineEvent]) -> bytes:
        """Generate timeline visualization."""

    def create_source_credibility_chart(self, pages: List[WebPage]) -> bytes:
        """Generate chart of source reliability."""

    def create_geographical_distribution(self, locations: List[Entity]) -> bytes:
        """Generate map of location entities."""
```

### Report Sections
```python
class ReportSections:
    EXECUTIVE_SUMMARY = "executive_summary"
    KEY_FINDINGS = "key_findings"
    TIMELINE = "timeline"
    ENTITY_ANALYSIS = "entity_analysis"
    SOURCE_ANALYSIS = "source_analysis"
    EVIDENCE_GALLERY = "evidence_gallery"
    METHODOLOGY = "methodology"
    APPENDIX = "appendix"

    @classmethod
    def get_default_sections(cls) -> List[str]:
        return [
            cls.EXECUTIVE_SUMMARY,
            cls.KEY_FINDINGS,
            cls.TIMELINE,
            cls.ENTITY_ANALYSIS,
            cls.SOURCE_ANALYSIS
        ]
```

### API Endpoints
```
POST   /subjects/{subject_id}/reports       - Generate new report
GET    /reports/{report_id}                 - Get report status
GET    /reports/{report_id}/download        - Download PDF
GET    /report-templates                    - List available templates
POST   /report-templates                    - Create custom template
```

### Styling and Branding
```css
/* Default Report Styling */
@page {
    size: A4;
    margin: 2cm;
    @top-center { content: "OSINT Investigation Report"; }
    @bottom-center { content: counter(page); }
}

.header {
    border-bottom: 2px solid #2563eb;
    padding-bottom: 1em;
    margin-bottom: 2em;
}

.executive-summary {
    background: #f8fafc;
    padding: 1.5em;
    border-left: 4px solid #2563eb;
}

.timeline-event {
    display: flex;
    margin-bottom: 1em;
    border-left: 2px solid #e5e7eb;
    padding-left: 1em;
}
```