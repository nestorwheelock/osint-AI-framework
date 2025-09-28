# S-004 — Playwright Web Scraping

**As a** OSINT researcher
**I want** to automatically fetch web pages with full browser automation
**So that** I can capture JavaScript-rendered content, screenshots, and PDFs from target URLs

## Acceptance Criteria
- [ ] When I provide a list of URLs, the system fetches each page using Playwright
- [ ] When pages are fetched, both HTML content and screenshots are captured
- [ ] When JavaScript-heavy sites are accessed, content is fully rendered before capture
- [ ] When fetching fails, appropriate error handling and retry logic is implemented
- [ ] When pages are large, the system handles timeouts and resource limits gracefully
- [ ] When PDF generation is requested, high-quality PDFs are created from pages

## Definition of Done
- [ ] POST /subjects/{subject_id}/fetch endpoint accepts URL lists
- [ ] Playwright browser automation configured with proper settings
- [ ] HTML content, screenshots, and PDFs stored in file system
- [ ] WebPage records created in database with metadata
- [ ] Error handling for timeouts, 404s, and connection failures
- [ ] Configurable browser settings (headless, viewport, user agent)
- [ ] Unit tests cover fetch orchestration and error scenarios
- [ ] Integration tests verify actual browser automation
- [ ] E2E tests confirm end-to-end page fetching workflow

## Dependencies
- Design section: [Web Scraper Architecture](../../docs/design/osint-platform.md#core-services)
- Story: S-003 (Meta-search provides URLs to fetch)
- External: Playwright browser binaries and dependencies

## Links
- PRD: [/docs/product/osint-platform.md](../../docs/product/osint-platform.md)
- Design: [/docs/design/osint-platform.md](../../docs/design/osint-platform.md)
- Data Model: [/docs/data-model.md](../../docs/data-model.md)
- Tasks: [/planning/tasks/T-004-web-scraping.md](../tasks/T-004-web-scraping.md)
- Related: [S-003: Meta-Search](S-003-meta-search.md)

## Test Plan

### Unit Tests (pytest)
- `test_playwright_page_fetch_success`
- `test_fetch_handles_javascript_rendering`
- `test_fetch_captures_screenshots_and_html`
- `test_fetch_generates_pdf_when_requested`
- `test_fetch_handles_timeout_gracefully`
- `test_fetch_retries_on_transient_failures`
- `test_fetch_respects_browser_configuration`

### Integration Tests (pytest + Playwright)
- `test_fetch_real_page_end_to_end`
- `test_concurrent_page_fetching`
- `test_browser_resource_management`

### E2E Tests (Playwright)
- `test_fetch_workflow_creates_webpage_records`
- `test_fetch_stores_files_correctly`
- `test_fetch_ui_shows_progress_and_results`

## AI Coding Brief
```yaml
role: "Senior backend engineer with browser automation expertise."
objective: "Implement robust Playwright web scraping with error handling."
constraints:
  allowed_paths:
    - backend/app/services/scraper/
    - backend/app/routes/subjects.py (extend for fetch endpoint)
    - backend/app/models/webpage.py
    - backend/app/tests/test_scraper.py
  dependencies: "Playwright for Python, async/await patterns"
  testing: "Mock Playwright for unit tests, real browser for integration"
  security:
    - "🚨 CRITICAL: NEVER include any AI, Claude, or assistant attribution anywhere"
    - "🚨 CRITICAL: NEVER use phrases like 'Generated with Claude', 'Co-Authored-By: Claude', etc."
    - "🚨 CRITICAL: Do not reference AI assistance in code, comments, commits, or any deliverables"
    - "🚨 CRITICAL: This is a SECURITY REQUIREMENT - violations will be automatically detected and removed"
tests_to_make_pass:
  - backend/app/tests/test_scraper.py::test_fetch_page_success
  - backend/app/tests/test_scraper.py::test_fetch_handles_errors
  - backend/app/tests/test_scraper.py::test_concurrent_fetching
definition_of_done:
  - "All referenced tests pass in CI"
  - "Browser automation works reliably with proper resource cleanup"
  - "File storage and database persistence work correctly"
  - "Error handling covers all common failure scenarios"
  - "No attribution or AI references in code/commits"
```

## Technical Notes

### Playwright Configuration
```python
browser_config = {
    "headless": True,
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": "Mozilla/5.0 (compatible; OSINT-Framework/1.0)",
    "timeout": 30000,
    "wait_until": "networkidle"
}
```

### WebPage Data Model
```python
class WebPage(Base):
    id: UUID
    subject_id: UUID
    session_id: UUID
    url: str
    canonical_url: str
    final_url: str  # After redirects
    http_status: int
    fetched_at: datetime
    html_path: str  # File system path
    screenshot_path: str
    pdf_path: Optional[str]
    content_hash: str
    page_title: str
    meta_description: Optional[str]
    error_message: Optional[str]
```

### File Storage Structure
```
storage/
├── html/
│   ├── 2024/01/15/
│   │   └── {webpage_id}.html
├── screenshots/
│   ├── 2024/01/15/
│   │   └── {webpage_id}.png
└── pdfs/
    ├── 2024/01/15/
    │   └── {webpage_id}.pdf
```

### API Endpoints
```
POST   /subjects/{subject_id}/fetch     - Fetch URLs for subject
GET    /subjects/{subject_id}/pages     - List fetched pages
GET    /pages/{page_id}                 - Get page details
GET    /pages/{page_id}/screenshot      - Download screenshot
GET    /pages/{page_id}/pdf             - Download PDF
```

### Error Handling Scenarios
- **Timeout**: Retry with extended timeout, then fail gracefully
- **404/403**: Record error but continue with other URLs
- **Network**: Exponential backoff retry logic
- **JavaScript**: Wait for network idle, handle dynamic content
- **Memory**: Browser restart after resource limits exceeded
