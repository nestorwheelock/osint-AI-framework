# OSINT Platform — System Design

## Context
The OSINT Platform provides automated web research capabilities for intelligence gathering. The system must handle web scraping at scale, AI-powered content analysis, and structured data export while maintaining ethical scraping practices.

## Proposed Architecture

### High-Level Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   AI Pipeline   │
│   (E2E Tests)   │◄──►│   (FastAPI)     │◄──►│   (Async Jobs)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │   File Storage  │
                       │   (Metadata)    │    │   (HTML/PDFs)   │
                       └─────────────────┘    └─────────────────┘
```

### Core Services
1. **Subject Management**: Create and organize investigation targets
2. **Search Orchestrator**: Coordinate multi-engine search queries
3. **Web Scraper**: Playwright-based page fetching and screenshot capture
4. **Content Processor**: Text extraction, language detection, deduplication
5. **AI Analyzer**: Entity extraction and content analysis pipelines
6. **Export Engine**: Generate reports in multiple formats

### Data Flow
1. User creates Subject and starts Session
2. System executes searches across multiple engines
3. URLs are queued for scraping with Playwright
4. Content is extracted and stored with metadata
5. AI pipelines analyze content for entities
6. Results are labeled, filtered, and exported

## Data/Integrations

### Search Engines
- Google (via search API or scraping)
- Bing (via API)
- DuckDuckGo
- Shodan (for technical reconnaissance)
- Custom search adapters

### AI Services
- OpenAI GPT for entity extraction
- Local models for cost optimization or offline use
- Language detection libraries

### Storage
- **PostgreSQL**: Metadata, relationships, entity data
- **File System**: Raw HTML, PDFs, screenshots
- **Optional Redis**: Caching and job queues

## Trade-offs & Alternatives

### Web Scraping Approach
**Chosen**: Playwright for full browser automation
- ✅ Handles JavaScript-heavy sites
- ✅ Captures screenshots and PDFs
- ❌ Higher resource usage
- ❌ Slower than raw HTTP

**Alternative**: Direct HTTP requests
- ✅ Faster and lighter
- ❌ Limited JavaScript support

### AI Pipeline Architecture
**Chosen**: Async job processing with Celery
- ✅ Handles long-running AI tasks
- ✅ Scalable worker architecture
- ❌ Additional infrastructure complexity

**Alternative**: Synchronous processing
- ✅ Simpler architecture
- ❌ Poor user experience for slow AI tasks

## Security/Privacy

### Data Protection
- All data stored as needed for research purposes (PII, personal data, etc.)
- No encryption requirements (private research system)
- Data retained indefinitely unless manually purged
- Basic logging for debugging and system monitoring

### Ethical Scraping
- Respect robots.txt by default
- Configurable rate limiting
- User-agent identification
- Terms of Service compliance mode

### API Security
- JWT authentication for multi-user scenarios
- Rate limiting on API endpoints
- Input validation and sanitization
- CORS configuration

## Observability

### Logging
- Structured JSON logs for all components
- Request/response logging for debugging
- Scraping activity logs for compliance

### Metrics
- Scraping success/failure rates
- AI pipeline processing times
- Storage usage and growth
- Export job completion rates

### Health Checks
- Database connectivity
- File system availability
- AI service responsiveness
- Background job queue status

## Work Breakdown (map to stories)

### Core Infrastructure (Must Have)
- **S-001**: Subject Creation - Basic CRUD operations
- **S-002**: Session Management - Investigation workflow
- **S-009**: Configuration Management - Secrets and settings

### Data Collection (Must Have)
- **S-003**: Meta-Search - Multi-engine search aggregation
- **S-004**: Web Scraping - Playwright integration
- **S-010**: Ethical Controls - Robots.txt and rate limiting

### Content Processing (Must Have)
- **S-005**: Text Extraction - Content parsing and language detection
- **S-006**: Entity Extraction - AI-powered analysis
- **S-012**: Deduplication - Content fingerprinting

### User Interface (Must Have)
- **S-007**: Labeling System - Manual categorization
- **S-008**: Export Functionality - JSONL and report generation

### Advanced Features (Should Have)
- **S-011**: Timeline Assembly - Chronological reconstruction
- **S-013**: PDF Reports - Formatted output generation
- **S-014**: Job Monitoring - Progress tracking and status

## Open Questions
1. Should we implement real-time search result streaming?
2. What level of JavaScript execution is needed for target sites?
3. How should we handle sites that require login/authentication?
4. What's the optimal balance between speed and thoroughness in content analysis?
5. Should we implement automatic screenshot comparison for change detection?