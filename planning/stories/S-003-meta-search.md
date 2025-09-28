```yaml
last_synced: '2025-09-28T16:22:25.045764'
status: todo
```

# S-003 — Meta-Search Implementation

**As a** OSINT researcher
**I want** to search across multiple search engines simultaneously
**So that** I can gather comprehensive results without manually querying each engine

## Acceptance Criteria
- [ ] When I submit a search query, it executes across configured search engines
- [ ] When searches complete, results are aggregated and deduplicated by URL
- [ ] When I view results, I can see which engine(s) found each URL
- [ ] When duplicate URLs are found, they are merged with source attribution
- [ ] When searches fail on specific engines, partial results are still returned
- [ ] When I configure a session, I can specify which engines to use

## Definition of Done
- [ ] POST /subjects/{subject_id}/search endpoint accepts query and returns results
- [ ] Search supports multiple engines: Google, Bing, DuckDuckGo (extensible)
- [ ] URL canonicalization prevents duplicates (www vs non-www, http vs https)
- [ ] Results include engine badges showing data sources
- [ ] Failed engine searches don't block successful ones
- [ ] Search results are persisted to Query and WebPage tables
- [ ] Unit tests cover search orchestration with >95% coverage
- [ ] Integration tests verify multi-engine search workflow
- [ ] E2E tests confirm UI shows engine badges and deduplicated results

## Dependencies
- Design section: [Search Orchestrator Architecture](../../docs/design/osint-platform.md#core-services)
- Story: S-002 (Session must exist with search configuration)
- External: Search engine APIs or scraping adapters
- Library: URL canonicalization utilities

## Links
- PRD: [/docs/product/osint-platform.md](../../docs/product/osint-platform.md)
- Design: [/docs/design/osint-platform.md](../../docs/design/osint-platform.md)
- Data Model: [/docs/data-model.md](../../docs/data-model.md)
- Tasks: [/planning/tasks/T-003-meta-search.md](../tasks/T-003-meta-search.md)
- Related: [S-002: Start Session](S-002-start-session.md)
- Existing: [prompts/issues/US-003-meta-search.yaml](../../prompts/issues/US-003-meta-search.yaml)

## Test Plan

### Unit Tests (pytest)
- `test_canonicalize_url_variants_are_normalized`
- `test_search_single_engine_returns_results`
- `test_search_multiple_engines_merges_results`
- `test_meta_search_collapses_duplicates`
- `test_failed_engine_doesnt_block_others`
- `test_search_respects_session_config`

### Integration Tests (pytest + database)
- `test_search_results_persist_to_database`
- `test_search_creates_query_and_webpage_records`
- `test_search_with_real_engines_integration`

### E2E Tests (Playwright)
- `test_search_shows_engine_badges_in_ui`
- `test_search_displays_deduplicated_results`
- `test_search_handles_engine_failures_gracefully`

## AI Coding Brief
```yaml
role: "Senior backend dev, TDD only."
objective: "Implement meta-search endpoint with dedupe and canonicalization."
constraints:
  allowed_paths:
    - backend/app/routes/search.py
    - backend/app/services/search/
    - backend/app/utils/url.py
    - backend/app/tests/test_search.py
    - backend/app/tests/test_url_utils.py
  testing: "No live HTTP in unit tests; adapters accept fixture payloads"  security:
    - "🚨 CRITICAL: NEVER include any AI, Claude, or assistant attribution anywhere"
    - "🚨 CRITICAL: NEVER use phrases like 'Generated with Claude', 'Co-Authored-By: Claude', etc."
    - "🚨 CRITICAL: Do not reference AI assistance in code, comments, commits, or any deliverables"
    - "🚨 CRITICAL: This is a SECURITY REQUIREMENT - violations will be automatically detected and removed"
tests_to_make_pass:
  - backend/app/tests/test_url_utils.py::test_canonicalize_url_variants
  - backend/app/tests/test_search.py::test_meta_search_collapses_duplicates
  - frontend/e2e/tests/search.spec.ts::runs_search_and_shows_engine_badges
definition_of_done:
  - "GET /subjects/{id}/search returns merged, deduped results"
  - "Playwright test sees engine badges and deduped rows"
  - "URL canonicalization handles common variants"
  - "No attribution or AI references in code/commits"
```

## Technical Notes

### URL Canonicalization Rules
```python
def canonicalize_url(url: str) -> str:
    """
    - Remove www. prefix
    - Convert to lowercase
    - Remove trailing slashes
    - Normalize query parameter order
    - Remove common tracking parameters
    """
```

### Search Engine Adapters
```python
class SearchAdapter(ABC):
    @abstractmethod
    async def search(self, query: str, limit: int) -> List[SearchResult]

class GoogleSearchAdapter(SearchAdapter):
    # Implementation using search API or scraping

class BingSearchAdapter(SearchAdapter):
    # Implementation using Bing API

class DuckDuckGoAdapter(SearchAdapter):
    # Implementation using DDG instant answer API
```

### Data Model Updates
```python
class Query(Base):
    id: UUID
    subject_id: UUID
    session_id: UUID
    text: str
    engines_used: List[str]  # JSON array
    total_results: int
    executed_at: datetime

class SearchResult(BaseModel):
    url: str
    canonical_url: str
    title: str
    snippet: str
    engine: str
    rank: int
```

### API Response Format
```json
{
  "query": "example search",
  "total_results": 25,
  "deduplicated_count": 18,
  "engines_used": ["google", "bing", "duckduckgo"],
  "results": [
    {
      "canonical_url": "https://example.com/page",
      "title": "Example Page",
      "snippet": "This is an example...",
      "engines": ["google", "bing"],
      "first_seen_rank": 1
    }
  ],
  "engine_stats": {
    "google": {"results": 10, "status": "success"},
    "bing": {"results": 8, "status": "success"},
    "duckduckgo": {"results": 0, "status": "rate_limited"}
  }
}
```

### Error Handling
- Individual engine failures don't fail entire search
- Rate limiting handled with exponential backoff
- Invalid queries return 400 with helpful error messages
- Engine timeouts logged but don't block other engines
