```yaml
last_synced: '2025-09-28T17:42:31.115892'
status: todo
```

# S-005 — Text Extraction & Language Detection

**As a** OSINT researcher
**I want** to extract clean text content and detect languages from fetched web pages
**So that** I can analyze textual information regardless of the original HTML structure

## Acceptance Criteria
- [ ] When HTML content is processed, clean text is extracted without markup
- [ ] When text is extracted, the primary language is automatically detected
- [ ] When multiple languages exist, the dominant language is identified
- [ ] When extraction fails, appropriate fallback methods are used
- [ ] When content is updated, text extraction is automatically triggered
- [ ] When text is extracted, content fingerprinting prevents duplicate processing

## Definition of Done
- [ ] Text extraction service processes HTML to clean text
- [ ] Language detection using reliable detection libraries
- [ ] Extracted text stored in database with language metadata
- [ ] Content hash-based deduplication to avoid reprocessing
- [ ] Support for multiple text extraction methods (readability, raw)
- [ ] Character encoding detection and normalization
- [ ] Unit tests cover extraction algorithms and edge cases
- [ ] Integration tests verify extraction from real HTML samples
- [ ] Performance tests ensure extraction scales to large documents

## Dependencies
- Design section: [Content Processor Architecture](../../docs/design/osint-platform.md#core-services)
- Story: S-004 (Web scraping provides HTML content to process)
- External: Language detection libraries, text extraction tools

## Links
- PRD: [/docs/product/osint-platform.md](../../docs/product/osint-platform.md)
- Design: [/docs/design/osint-platform.md](../../docs/design/osint-platform.md)
- Data Model: [/docs/data-model.md](../../docs/data-model.md)
- Tasks: [/planning/tasks/T-005-text-extraction.md](../tasks/T-005-text-extraction.md)
- Related: [S-004: Web Scraping](S-004-web-scraping.md)

## Test Plan

### Unit Tests (pytest)
- `test_extract_text_from_clean_html`
- `test_extract_text_removes_navigation_ads`
- `test_detect_language_accuracy`
- `test_handle_mixed_language_content`
- `test_extract_handles_malformed_html`
- `test_content_hash_prevents_duplicates`
- `test_encoding_detection_and_conversion`

### Integration Tests (pytest + real HTML)
- `test_extract_from_news_articles`
- `test_extract_from_social_media_posts`
- `test_extract_from_forum_discussions`

## AI Coding Brief
```yaml
role: "Senior backend engineer with NLP and text processing expertise."
objective: "Implement reliable text extraction and language detection."
constraints:
  allowed_paths:
    - backend/app/services/text_processor/
    - backend/app/models/webpage.py (extend with text fields)
    - backend/app/tests/test_text_processor.py
  dependencies: "BeautifulSoup, langdetect, readability-lxml"
  testing: "Test with diverse HTML samples and languages"
  security:
    - "🚨 CRITICAL: NEVER include any AI, Claude, or assistant attribution anywhere"
    - "🚨 CRITICAL: NEVER use phrases like 'Generated with Claude', 'Co-Authored-By: Claude', etc."
    - "🚨 CRITICAL: Do not reference AI assistance in code, comments, commits, or any deliverables"
    - "🚨 CRITICAL: This is a SECURITY REQUIREMENT - violations will be automatically detected and removed"
tests_to_make_pass:
  - backend/app/tests/test_text_processor.py::test_extract_clean_text
  - backend/app/tests/test_text_processor.py::test_language_detection
  - backend/app/tests/test_text_processor.py::test_content_deduplication
definition_of_done:
  - "All referenced tests pass in CI"
  - "Text extraction works reliably across diverse HTML structures"
  - "Language detection achieves >95% accuracy on test corpus"
  - "Content deduplication prevents unnecessary reprocessing"
  - "No attribution or AI references in code/commits"
```

## Technical Notes

### Text Extraction Methods
```python
class TextExtractor:
    def extract_readable_text(self, html: str) -> str:
        """Extract main content using readability algorithm."""

    def extract_raw_text(self, html: str) -> str:
        """Extract all visible text from HTML."""

    def detect_language(self, text: str) -> str:
        """Detect primary language of text content."""

    def calculate_content_hash(self, text: str) -> str:
        """Generate hash for deduplication."""
```

### Extended WebPage Model
```python
class WebPage(Base):
    # ... existing fields ...
    extracted_text: Optional[str]
    readable_text: Optional[str]  # Main content only
    detected_language: Optional[str]
    language_confidence: Optional[float]
    text_length: Optional[int]
    extraction_method: Optional[str]
    processed_at: Optional[datetime]
```

### Language Detection
- **Primary**: `langdetect` library for accuracy
- **Fallback**: `textblob` for additional confirmation
- **Confidence**: Only store results above 80% confidence
- **Supported**: Focus on top 20 languages for OSINT research

### Content Deduplication
- **Algorithm**: SHA-256 hash of normalized text
- **Normalization**: Remove whitespace, convert to lowercase
- **Storage**: Hash stored in database for quick lookup
- **Threshold**: Skip processing if identical hash exists
