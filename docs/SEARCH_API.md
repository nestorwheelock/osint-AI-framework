# Search Infrastructure API Documentation

## Quick Reference

### Import Statements
```python
from apps.search.orchestrator import (
    MetaSearchOrchestrator, SearchStrategy, SearchConfig,
    search_osint, quick_search
)
from apps.search.adapters import SearchAdapterFactory, SearchResult
from apps.search.utils import canonicalize_url, deduplicate_urls, extract_domain
```

### Basic Usage Examples

#### Simple OSINT Search
```python
# One-liner for OSINT investigations
results = search_osint("APT29 tactics", max_results=15)
for result in results:
    print(f"{result.title}\n{result.url}\n{result.snippet[:100]}...\n")
```

#### Advanced Orchestration
```python
# Full control over search execution
config = SearchConfig(
    preferred_adapters=['duckduckgo', 'lynx'],
    enable_deduplication=True,
    max_total_results=25
)

orchestrator = MetaSearchOrchestrator(config)
orchestrator.load_adapters()

results = orchestrator.search(
    "cybersecurity threat intelligence",
    strategy=SearchStrategy.ADAPTIVE
)

# Get performance statistics
stats = orchestrator.get_search_statistics()
print(f"Search completed in {stats['average_response_time']:.2f}s")
```

#### Custom Adapter Usage
```python
# Use specific adapters for specialized searches
duckduckgo = SearchAdapterFactory.get_adapter('duckduckgo')
lynx = SearchAdapterFactory.get_adapter('lynx')

# Combine results manually
ddg_results = duckduckgo.search("OSINT tools", limit=10)
lynx_results = lynx.search("OSINT tools", limit=10)

all_results = ddg_results + lynx_results
unique_results = deduplicate_urls([r.url for r in all_results])
```

## Core Classes

### MetaSearchOrchestrator

**Constructor:**
```python
MetaSearchOrchestrator(config: Optional[SearchConfig] = None)
```

**Methods:**

#### load_adapters
```python
def load_adapters(self, adapter_names: Optional[List[str]] = None) -> None:
    """Load search adapters for orchestration.

    Args:
        adapter_names: Specific adapters to load, or None for all available
    """
```

#### search
```python
def search(
    self,
    query: str,
    strategy: SearchStrategy = SearchStrategy.PARALLEL,
    config: Optional[SearchConfig] = None
) -> List[SearchResult]:
    """Execute meta-search across multiple adapters.

    Args:
        query: Search query string
        strategy: Search execution strategy (PARALLEL, SEQUENTIAL, ADAPTIVE)
        config: Optional config override

    Returns:
        Ranked and deduplicated search results
    """
```

#### get_search_statistics
```python
def get_search_statistics(self) -> Dict[str, Any]:
    """Get comprehensive search performance statistics.

    Returns:
        Dictionary containing:
        - total_searches: Number of searches executed
        - success_rate: Percentage of successful searches
        - average_response_time: Average time per search in seconds
        - adapter_performance: Per-adapter statistics
    """
```

### SearchConfig

**Configuration Options:**
```python
@dataclass
class SearchConfig:
    max_results_per_adapter: int = 10      # Results per adapter
    timeout_seconds: int = 30              # Search timeout
    enable_deduplication: bool = True      # Remove duplicate URLs
    enable_ranking: bool = True            # Rank results by relevance
    preferred_adapters: List[str] = ['duckduckgo', 'lynx', 'curl']
    fallback_adapters: List[str] = ['google', 'bing']
    min_snippet_length: int = 20           # Quality filter
    max_total_results: int = 50            # Total result limit
```

### SearchResult

**Attributes:**
```python
@dataclass
class SearchResult:
    title: str      # Result title
    url: str        # Canonicalized URL
    snippet: str    # Content snippet
    source: str     # Source adapter name
```

## Search Strategies

### SearchStrategy.PARALLEL
- Executes all adapters simultaneously
- Fastest execution time
- Best for real-time searches
- May hit rate limits with multiple adapters

### SearchStrategy.SEQUENTIAL
- Executes adapters one by one
- Most reliable execution
- Slower but consistent results
- Best for batch processing

### SearchStrategy.ADAPTIVE
- Starts with fast adapters, adds slower ones if needed
- OSINT-optimized approach
- Balances speed and completeness
- Recommended for intelligence gathering

## URL Canonicalization API

### canonicalize_url
```python
def canonicalize_url(
    url: str,
    remove_fragment: bool = True,
    remove_tracking: bool = True,
    normalize_domain: bool = True,
    sort_query_params: bool = True
) -> str:
    """Canonicalize a URL by applying normalization rules.

    Args:
        url: The URL to canonicalize
        remove_fragment: Whether to remove URL fragments (#section)
        remove_tracking: Whether to remove tracking parameters
        normalize_domain: Whether to normalize domain (remove www, etc.)
        sort_query_params: Whether to sort query parameters alphabetically

    Returns:
        Canonicalized URL string
    """
```

### deduplicate_urls
```python
def deduplicate_urls(urls: List[str]) -> List[str]:
    """Remove duplicate URLs based on canonical form.

    Args:
        urls: List of URLs to deduplicate

    Returns:
        List of unique URLs (first occurrence preserved)
    """
```

### extract_domain
```python
def extract_domain(url: str) -> str:
    """Extract and normalize the domain from a URL.

    Args:
        url: URL to extract domain from

    Returns:
        Normalized domain name
    """
```

## Search Adapters

### Available Adapters

#### DuckDuckGoSearchAdapter
- **Reliability**: 
- **Bot Detection**: Low risk
- **Rate Limits**: Generous
- **Use Case**: Primary OSINT searches

#### LynxSearchAdapter
- **Reliability**: 
- **Bot Detection**: Very low risk
- **Rate Limits**: Excellent
- **Use Case**: Stealth investigations

#### CurlSearchAdapter
- **Reliability**: 
- **Bot Detection**: Low risk
- **Rate Limits**: Good
- **Use Case**: Custom header searches

#### GoogleSearchAdapter
- **Reliability**:  (with API)
- **Bot Detection**: High risk (scraping)
- **Rate Limits**: Restrictive
- **Use Case**: API-based searches only

#### BingSearchAdapter
- **Reliability**: 
- **Bot Detection**: Medium risk
- **Rate Limits**: Moderate
- **Use Case**: API-based searches

### Adapter Factory

```python
# Get specific adapter
adapter = SearchAdapterFactory.get_adapter('duckduckgo')

# Get all available adapters
all_adapters = SearchAdapterFactory.create_all_adapters()

# List available adapter names
names = SearchAdapterFactory.get_available_adapters()
# Returns: ['google', 'bing', 'duckduckgo', 'lynx', 'curl']
```

## Error Handling

### Common Exceptions

```python
try:
    results = orchestrator.search("query")
except Exception as e:
    print(f"Search failed: {e}")
    # Orchestrator continues with other adapters
    # Returns partial results if any adapters succeed
```

### Graceful Degradation

The search infrastructure is designed for graceful degradation:

- If one adapter fails, others continue
- Partial results are returned when possible
- Performance statistics track failure rates
- Empty results returned on total failure

### Debugging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable verbose logging for troubleshooting
orchestrator = MetaSearchOrchestrator()
results = orchestrator.search("debug query")

# Check adapter availability
print(f"Loaded adapters: {orchestrator.get_available_adapters()}")

# Monitor performance
stats = orchestrator.get_search_statistics()
for adapter, perf in stats['adapter_performance'].items():
    if perf['success_rate'] < 0.8:
        print(f"Warning: {adapter} success rate: {perf['success_rate']:.2%}")
```

## Best Practices

### Production Configuration

```python
# Recommended production settings
PRODUCTION_CONFIG = SearchConfig(
    max_results_per_adapter=8,
    timeout_seconds=25,
    enable_deduplication=True,
    enable_ranking=True,
    preferred_adapters=['duckduckgo', 'lynx'],
    fallback_adapters=['curl'],
    min_snippet_length=25,
    max_total_results=40
)
```

### Performance Optimization

1. **Use appropriate strategies:**
   - PARALLEL for speed
   - SEQUENTIAL for reliability
   - ADAPTIVE for OSINT

2. **Configure timeouts appropriately:**
   - Short timeouts (15s) for real-time
   - Longer timeouts (45s) for comprehensive searches

3. **Optimize result limits:**
   - Fewer results per adapter = faster execution
   - Higher quality filters = better results

4. **Monitor adapter performance:**
   - Disable consistently failing adapters
   - Adjust timeouts based on statistics

### OSINT Best Practices

1. **Use adaptive strategy** for intelligence gathering
2. **Enable deduplication** to remove redundant information
3. **Set appropriate snippet length** for meaningful content
4. **Prefer DuckDuckGo and Lynx** for reliability
5. **Monitor rate limits** to avoid detection
6. **Rotate adapters** for high-volume searches

---

*For complete implementation details, see the source code in `apps/search/`*
