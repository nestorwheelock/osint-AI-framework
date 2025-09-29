# OSINT AI Framework - Search Infrastructure

## Overview

The OSINT AI Framework search infrastructure provides a comprehensive, production-ready solution for conducting multi-source intelligence searches. Built with enterprise-grade architecture, it features bot detection bypass, intelligent result ranking, and automated deduplication.

##  Quick Start

```python
from apps.search.orchestrator import search_osint, quick_search

# OSINT-optimized search across multiple adapters
results = search_osint("cybersecurity threats", max_results=20)

# Quick single-adapter search
results = quick_search("malware analysis", adapter_name='duckduckgo')

for result in results:
    print(f"{result.title} - {result.url}")
```

##  Architecture

### Core Components

1. **Search Adapters** (`apps/search/adapters.py`)
   - Unified interface for multiple search engines
   - Built-in bot detection bypass using terminal browsers
   - Support for Google, Bing, DuckDuckGo, Lynx, and Curl

2. **URL Canonicalization** (`apps/search/utils.py`)
   - Intelligent URL normalization and cleaning
   - Tracking parameter removal (utm_*, fbclid, gclid, etc.)
   - Domain normalization (www removal, mobile prefixes)

3. **Meta-Search Orchestration** (`apps/search/orchestrator.py`)
   - Coordinates multiple search adapters
   - Intelligent result ranking and deduplication
   - Performance monitoring and statistics

##  Search Adapters

### Available Adapters

| Adapter | Status | Bot Detection Bypass | Use Case |
|---------|--------|---------------------|----------|
| DuckDuckGo |  Primary | High | General OSINT searches |
| Lynx |  Recommended | Very High | Stealth searches |
| Curl |  Available | High | Custom header searches |
| Google |  Detected | Low | API access only |
| Bing |  Detected | Low | API access only |

### Creating Custom Adapters

```python
from apps.search.adapters import BaseSearchAdapter, SearchResult

class CustomAdapter(BaseSearchAdapter):
    def get_name(self) -> str:
        return "custom"

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        # Implement your search logic
        results = []
        # ... search implementation
        return results
```

##  Meta-Search Orchestration

### Search Strategies

```python
from apps.search.orchestrator import MetaSearchOrchestrator, SearchStrategy

orchestrator = MetaSearchOrchestrator()
orchestrator.load_adapters(['duckduckgo', 'lynx'])

# Parallel execution (fastest)
results = orchestrator.search("query", strategy=SearchStrategy.PARALLEL)

# Sequential execution (reliable)
results = orchestrator.search("query", strategy=SearchStrategy.SEQUENTIAL)

# Adaptive execution (OSINT-optimized)
results = orchestrator.search("query", strategy=SearchStrategy.ADAPTIVE)
```

### Configuration

```python
from apps.search.orchestrator import SearchConfig

config = SearchConfig(
    max_results_per_adapter=15,
    timeout_seconds=30,
    enable_deduplication=True,
    enable_ranking=True,
    preferred_adapters=['duckduckgo', 'lynx'],
    fallback_adapters=['curl'],
    min_snippet_length=20,
    max_total_results=50
)

orchestrator = MetaSearchOrchestrator(config)
```

##  URL Canonicalization

### Features

- **Tracking Parameter Removal**: Strips utm_*, fbclid, gclid, and 40+ other tracking parameters
- **Domain Normalization**: Removes www, mobile prefixes (m., mobile.)
- **Path Normalization**: Cleans duplicate slashes, trailing slashes
- **Query Parameter Sorting**: Optional alphabetical parameter ordering

### Usage

```python
from apps.search.utils import canonicalize_url, deduplicate_urls

# Clean individual URLs
clean_url = canonicalize_url("https://www.example.com/path?utm_source=google&param=value")
# Result: "https://example.com/path?param=value"

# Deduplicate URL lists
urls = ["https://example.com/page", "https://www.example.com/page?utm_source=email"]
unique_urls = deduplicate_urls(urls)
# Result: ["https://example.com/page"] (deduplicated)
```

##  Performance Monitoring

### Getting Statistics

```python
orchestrator = MetaSearchOrchestrator()
# ... perform searches

stats = orchestrator.get_search_statistics()
print(f"Success rate: {stats['success_rate']:.2%}")
print(f"Average response time: {stats['average_response_time']:.3f}s")

# Per-adapter performance
for adapter, perf in stats['adapter_performance'].items():
    print(f"{adapter}: {perf['success_rate']:.2%} success rate")
```

### Performance Optimization

1. **Use DuckDuckGo as primary** - No bot detection, reliable results
2. **Enable Lynx for stealth** - Terminal browser bypasses detection
3. **Configure timeouts appropriately** - Balance speed vs completeness
4. **Use adaptive strategy for OSINT** - Optimized for intelligence gathering

##  Testing

### Running Tests

```bash
# Run all search infrastructure tests
python -m pytest apps/search/tests/ -v

# Specific test suites
python -m pytest apps/search/tests/test_adapters.py -v      # 28 adapter tests
python -m pytest apps/search/tests/test_utils.py -v         # 22 canonicalization tests
python -m pytest apps/search/tests/test_orchestrator.py -v  # 18 orchestration tests
```

### Test Coverage

- **68 comprehensive test cases** across all components
- **100% coverage** for search adapters, URL canonicalization, and orchestration
- **TDD methodology** - tests written before implementation
- **Integration tests** with real search engines

##  Security & Ethics

### Bot Detection Bypass

The terminal-based adapters (Lynx, Curl) are designed to bypass bot detection while respecting rate limits and terms of service:

- **Lynx**: Text-based browser, appears as legitimate user agent
- **Curl**: Custom headers, rotating user agents
- **Rate limiting**: Built-in delays and request throttling

### Responsible Usage

- Respect search engine rate limits
- Use for legitimate OSINT investigations only
- Consider API access for high-volume usage
- Follow applicable laws and regulations

##  API Reference

### Core Classes

#### `MetaSearchOrchestrator`
Main orchestration class for coordinating searches across multiple adapters.

**Methods:**
- `load_adapters(adapter_names: List[str])` - Load specific adapters
- `search(query: str, strategy: SearchStrategy, config: SearchConfig)` - Execute search
- `get_search_statistics()` - Get performance metrics
- `configure(config: SearchConfig)` - Update configuration

#### `SearchResult`
Standardized search result representation.

**Attributes:**
- `title: str` - Result title
- `url: str` - Canonicalized URL
- `snippet: str` - Content snippet
- `source: str` - Source adapter name

#### `URLCanonicalizer`
URL normalization and canonicalization utilities.

**Methods:**
- `canonicalize_url(url: str, **options)` - Normalize single URL
- `deduplicate_urls(urls: List[str])` - Remove duplicates
- `are_urls_equivalent(url1: str, url2: str)` - Check equivalence

### Convenience Functions

```python
# OSINT-optimized search
search_osint(query: str, max_results: int = 20, adapters: List[str] = None)

# Quick single-adapter search
quick_search(query: str, adapter_name: str = 'duckduckgo')

# URL utilities
canonicalize_url(url: str, **kwargs)
extract_domain(url: str)
deduplicate_urls(urls: List[str])
```

##  Troubleshooting

### Common Issues

**No results returned:**
- Check adapter availability with `orchestrator.get_available_adapters()`
- Verify internet connectivity
- Try different search adapters

**Bot detection errors:**
- Use Lynx or Curl adapters instead of Google/Bing
- Reduce request frequency
- Check for IP rate limiting

**Performance issues:**
- Reduce `max_results_per_adapter` in configuration
- Use sequential strategy instead of parallel
- Enable result filtering with `min_snippet_length`

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run searches with detailed logging
results = orchestrator.search("debug query")
```

##  Production Deployment

### Requirements

- Python 3.8+
- Django 4.2+
- BeautifulSoup4
- Optional: lynx, curl system packages

### Installation

```bash
pip install beautifulsoup4
# Optional for terminal browsers
sudo apt-get install lynx curl  # Ubuntu/Debian
brew install lynx curl          # macOS
```

### Configuration

```python
# Production configuration
PRODUCTION_CONFIG = SearchConfig(
    max_results_per_adapter=10,
    timeout_seconds=20,
    enable_deduplication=True,
    enable_ranking=True,
    preferred_adapters=['duckduckgo', 'lynx'],
    min_snippet_length=30,
    max_total_results=30
)
```

##  Roadmap

### Future Enhancements

- [ ] Additional search engine adapters (Yandex, Baidu)
- [ ] Machine learning result ranking
- [ ] Distributed search execution
- [ ] Advanced caching mechanisms
- [ ] RESTful API endpoints
- [ ] WebSocket real-time search feeds

### Contributing

1. Follow TDD methodology - write tests first
2. Use the 6-step incremental commit workflow
3. Maintain 100% test coverage
4. Update documentation for all changes
5. Test with multiple search adapters

---

*Built with enterprise-grade architecture for the OSINT AI Framework. Last updated: Sprint 2 completion.*
