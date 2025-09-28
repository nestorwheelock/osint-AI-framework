# S-012 — Duplicate Detection

**As a** OSINT researcher
**I want** to automatically detect and merge duplicate content across sources
**So that** I can avoid redundant analysis and focus on unique information

## Acceptance Criteria
- [ ] When web pages have identical content, they are automatically flagged as duplicates
- [ ] When near-duplicate content exists, similarity scores are calculated and displayed
- [ ] When duplicates are detected, the system suggests merging with conflict resolution
- [ ] When entities are extracted from duplicates, they are consolidated into single records
- [ ] When duplicate content is merged, provenance and source attribution is maintained
- [ ] When researchers review duplicates, they can manually confirm or reject suggestions

## Definition of Done
- [ ] Content fingerprinting using multiple hashing algorithms
- [ ] Similarity detection using text comparison techniques
- [ ] Duplicate suggestion system with confidence scoring
- [ ] Manual review interface for duplicate confirmation
- [ ] Entity consolidation across duplicate sources
- [ ] Provenance tracking for merged content
- [ ] Unit tests cover fingerprinting and similarity algorithms
- [ ] Integration tests verify duplicate detection accuracy
- [ ] Performance tests ensure efficient processing of large datasets

## Dependencies
- Design section: [Duplicate Detection](../../docs/design/osint-platform.md#advanced-features)
- Story: S-005 (Text extraction for content comparison)
- Story: S-006 (Entity extraction for consolidation)

## Links
- PRD: [/docs/product/osint-platform.md](../../docs/product/osint-platform.md)
- Design: [/docs/design/osint-platform.md](../../docs/design/osint-platform.md)
- Tasks: [/planning/tasks/T-012-duplicate-detection.md](../tasks/T-012-duplicate-detection.md)
- Related: [S-005: Text Extraction](S-005-text-extraction.md), [S-006: Entity Extraction](S-006-entity-extraction.md)

## Test Plan

### Unit Tests (pytest)
- `test_content_fingerprinting_algorithms`
- `test_similarity_calculation_methods`
- `test_duplicate_threshold_tuning`
- `test_entity_consolidation_logic`
- `test_provenance_preservation`
- `test_manual_review_workflow`
- `test_performance_large_datasets`

### Integration Tests (pytest + database)
- `test_end_to_end_duplicate_detection`
- `test_duplicate_entity_merging`
- `test_cross_source_duplicate_identification`

### E2E Tests (Playwright)
- `test_duplicate_review_interface`
- `test_merge_confirmation_workflow`
- `test_duplicate_status_visualization`

## AI Coding Brief
```yaml
role: "Senior engineer with text similarity and deduplication expertise."
objective: "Implement accurate duplicate detection with manual review capabilities."
constraints:
  allowed_paths:
    - backend/app/services/deduplication/
    - backend/app/models/duplicate_group.py
    - backend/app/routes/duplicates.py
    - backend/app/tests/test_deduplication.py
  dependencies: "scikit-learn for similarity, difflib for text comparison"
  testing: "Test with various content types and similarity thresholds"
  security:
    - "NEVER include author attribution in commits or code"
    - "Do not reference AI assistance in any deliverables"
tests_to_make_pass:
  - backend/app/tests/test_deduplication.py::test_duplicate_detection
  - backend/app/tests/test_deduplication.py::test_similarity_scoring
  - backend/app/tests/test_deduplication.py::test_entity_consolidation
definition_of_done:
  - "All referenced tests pass in CI"
  - "Duplicate detection achieves >95% accuracy on test corpus"
  - "Similarity scoring provides meaningful confidence levels"
  - "Manual review interface enables efficient duplicate management"
  - "No attribution or AI references in code/commits"
```

## Technical Notes

### Duplicate Detection Models
```python
class DuplicateGroup(Base):
    id: UUID
    subject_id: UUID
    group_type: DuplicateType  # EXACT, NEAR_DUPLICATE, SIMILAR
    confidence_score: float
    status: DuplicateStatus  # DETECTED, UNDER_REVIEW, CONFIRMED, REJECTED
    primary_item_id: UUID  # The "canonical" version
    primary_item_type: str  # "webpage" or "entity"
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    merge_strategy: Optional[str]
    created_at: datetime

class DuplicateItem(Base):
    duplicate_group_id: UUID
    item_id: UUID
    item_type: str  # "webpage" or "entity"
    similarity_score: float
    content_hash: str
    fuzzy_hash: str
    added_at: datetime
```

### Content Fingerprinting
```python
class ContentFingerprinter:
    def generate_exact_hash(self, content: str) -> str:
        """SHA-256 hash of normalized content for exact matches."""

    def generate_fuzzy_hash(self, content: str) -> str:
        """Fuzzy hash for near-duplicate detection."""

    def generate_semantic_hash(self, content: str) -> str:
        """Content-based hash ignoring formatting differences."""

    def normalize_content(self, text: str) -> str:
        """Normalize whitespace, punctuation, and formatting."""
```

### Similarity Detection
```python
class SimilarityDetector:
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity using multiple algorithms."""

    def jaccard_similarity(self, text1: str, text2: str) -> float:
        """Jaccard similarity coefficient."""

    def cosine_similarity(self, text1: str, text2: str) -> float:
        """Cosine similarity using TF-IDF vectors."""

    def levenshtein_ratio(self, text1: str, text2: str) -> float:
        """Edit distance ratio for character-level similarity."""

    def detect_near_duplicates(self, content_list: List[str], threshold: float = 0.8) -> List[List[int]]:
        """Group content by similarity above threshold."""
```

### Entity Consolidation
```python
class EntityConsolidator:
    def merge_duplicate_entities(self, entity_group: List[Entity]) -> Entity:
        """Merge duplicate entities preserving all information."""

    def resolve_conflicts(self, entities: List[Entity]) -> dict:
        """Resolve conflicting information across duplicates."""

    def preserve_provenance(self, merged_entity: Entity, source_entities: List[Entity]) -> None:
        """Maintain source attribution for merged data."""

    def update_relationships(self, old_entities: List[UUID], new_entity: UUID) -> None:
        """Update all references to point to consolidated entity."""
```

### Duplicate Review Interface
```python
class DuplicateReviewService:
    def get_pending_duplicates(self, subject_id: UUID) -> List[DuplicateGroup]:
        """Get duplicates awaiting manual review."""

    def confirm_duplicate(self, group_id: UUID, merge_strategy: str, reviewer: str) -> None:
        """Confirm duplicate and execute merge."""

    def reject_duplicate(self, group_id: UUID, reason: str, reviewer: str) -> None:
        """Reject duplicate suggestion."""

    def suggest_merge_strategy(self, group: DuplicateGroup) -> str:
        """AI-powered suggestion for merge approach."""
```

### API Endpoints
```
GET    /subjects/{subject_id}/duplicates    - List detected duplicates
POST   /duplicates/{group_id}/confirm       - Confirm and merge duplicates
POST   /duplicates/{group_id}/reject        - Reject duplicate suggestion
GET    /duplicates/pending                  - Get duplicates needing review
POST   /duplicates/detection/run            - Trigger duplicate detection
```

### Performance Optimizations
- **Incremental Processing**: Only check new content against existing fingerprints
- **Indexing**: Use database indexes on content hashes for fast lookups
- **Batch Processing**: Process similarity calculations in batches
- **Caching**: Cache similarity calculations for repeated comparisons
- **Thresholds**: Configurable similarity thresholds to balance accuracy vs performance