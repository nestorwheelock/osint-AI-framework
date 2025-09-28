```yaml
last_synced: '2025-09-28T17:42:31.116269'
status: todo
```

# S-006 — AI Entity Extraction

**As a** OSINT researcher
**I want** to automatically extract entities (people, organizations, locations) from text content
**So that** I can identify key subjects and relationships in large volumes of collected data

## Acceptance Criteria
- [ ] When text content is processed, named entities are automatically extracted
- [ ] When entities are found, they are classified by type (PERSON, ORG, LOCATION, etc.)
- [ ] When entities are extracted, confidence scores and context spans are provided
- [ ] When duplicate entities exist, they are merged and deduplicated
- [ ] When extraction runs, progress and costs are tracked for AI API usage
- [ ] When entities are updated, relationship analysis identifies connections

## Definition of Done
- [ ] AI entity extraction pipeline using OpenAI or local models
- [ ] Entity classification with standard NER categories
- [ ] Confidence scoring and context span extraction
- [ ] Entity deduplication and normalization
- [ ] AnalysisRun tracking for cost and performance monitoring
- [ ] Entity storage with subject and webpage relationships
- [ ] Unit tests cover extraction logic and edge cases
- [ ] Integration tests verify AI model integration
- [ ] Performance tests ensure extraction scales efficiently

## Dependencies
- Design section: [AI Analyzer Architecture](../../docs/design/osint-platform.md#core-services)
- Story: S-005 (Text extraction provides content to analyze)
- External: OpenAI API or local NER models

## Links
- PRD: [/docs/product/osint-platform.md](../../docs/product/osint-platform.md)
- Design: [/docs/design/osint-platform.md](../../docs/design/osint-platform.md)
- Data Model: [/docs/data-model.md](../../docs/data-model.md)
- Tasks: [/planning/tasks/T-006-entity-extraction.md](../tasks/T-006-entity-extraction.md)
- Related: [S-005: Text Extraction](S-005-text-extraction.md)
- Existing: [prompts/issues/US-006-entity-extract.yaml](../../prompts/issues/US-006-entity-extract.yaml)

## Test Plan

### Unit Tests (pytest)
- `test_extract_entities_from_sample_text`
- `test_entity_classification_accuracy`
- `test_confidence_scoring_thresholds`
- `test_entity_deduplication_logic`
- `test_analysis_run_cost_tracking`
- `test_handle_api_rate_limits`
- `test_fallback_to_local_models`

### Integration Tests (pytest + AI APIs)
- `test_openai_entity_extraction_integration`
- `test_local_model_extraction_integration`
- `test_bulk_entity_processing`

### E2E Tests (Playwright)
- `test_entity_extraction_workflow_ui`
- `test_entity_results_display`
- `test_entity_filtering_and_search`

## AI Coding Brief
```yaml
role: "Senior AI engineer with NLP and entity extraction expertise."
objective: "Implement robust AI-powered entity extraction pipeline."
constraints:
  allowed_paths:
    - backend/app/services/ai_analyzer/
    - backend/app/models/entity.py
    - backend/app/models/analysis_run.py
    - backend/app/tests/test_ai_analyzer.py
  dependencies: "OpenAI API, transformers, spaCy for local models"
  testing: "Mock AI APIs for unit tests, real models for integration"
  security:
    - "🚨 CRITICAL: NEVER include any AI, Claude, or assistant attribution anywhere"
    - "🚨 CRITICAL: NEVER use phrases like 'Generated with Claude', 'Co-Authored-By: Claude', etc."
    - "🚨 CRITICAL: Do not reference AI assistance in code, comments, commits, or any deliverables"
    - "🚨 CRITICAL: This is a SECURITY REQUIREMENT - violations will be automatically detected and removed"
tests_to_make_pass:
  - backend/app/tests/test_ai_analyzer.py::test_entity_extraction_success
  - backend/app/tests/test_ai_analyzer.py::test_entity_deduplication
  - backend/app/tests/test_ai_analyzer.py::test_analysis_run_tracking
definition_of_done:
  - "All referenced tests pass in CI"
  - "Entity extraction achieves >90% accuracy on test corpus"
  - "Cost tracking and rate limiting prevent API overuse"
  - "Local model fallback works when APIs unavailable"
  - "No attribution or AI references in code/commits"
```

## Technical Notes

### Entity Types
```python
class EntityType(Enum):
    PERSON = "PERSON"
    ORGANIZATION = "ORG"
    LOCATION = "LOC"
    DATE = "DATE"
    MONEY = "MONEY"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    URL = "URL"
    MISC = "MISC"
```

### Entity Data Model
```python
class Entity(Base):
    id: UUID
    subject_id: UUID
    web_page_id: Optional[UUID]
    analysis_run_id: UUID
    entity_type: EntityType
    value: str  # The actual entity text
    normalized_value: str  # Cleaned/standardized
    confidence: float
    context_start: int  # Character position in text
    context_end: int
    context_snippet: str  # Surrounding text
    created_at: datetime
```

### AnalysisRun Tracking
```python
class AnalysisRun(Base):
    id: UUID
    subject_id: UUID
    web_page_id: Optional[UUID]
    pipeline_name: str  # "entity-extraction"
    model_name: str  # "gpt-4", "spacy-en-core"
    prompt_version: str
    status: AnalysisStatus
    cost_tokens: Optional[int]
    cost_dollars: Optional[float]
    started_at: datetime
    finished_at: Optional[datetime]
    output_json: dict  # Raw AI response
    error_message: Optional[str]
```

### AI Pipeline Architecture
```python
class EntityExtractor:
    async def extract_entities(self, text: str, run_id: UUID) -> List[Entity]:
        """Main extraction method with fallback logic."""

    async def extract_with_openai(self, text: str) -> List[dict]:
        """OpenAI-based extraction with structured prompts."""

    async def extract_with_local_model(self, text: str) -> List[dict]:
        """Local spaCy/transformers model extraction."""

    def deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """Merge similar entities and resolve conflicts."""
```

### Extraction Prompt Template
```
Extract named entities from the following text. Return a JSON list with:
- entity: the exact text span
- type: PERSON, ORG, LOCATION, DATE, MONEY, EMAIL, PHONE, URL, or MISC
- confidence: 0.0-1.0 confidence score
- context: surrounding words for disambiguation

Text: {input_text}

Response format:
[{"entity": "John Smith", "type": "PERSON", "confidence": 0.95, "context": "CEO John Smith announced"}]
```

### Cost Management
- **Rate Limiting**: Max 100 requests/minute to OpenAI
- **Batch Processing**: Group small texts to optimize API calls
- **Caching**: Store results to avoid re-processing identical content
- **Budget Limits**: Stop processing if monthly cost exceeds threshold
