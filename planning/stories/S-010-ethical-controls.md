# S-010 — Ethical Scraping Controls

**As a** OSINT researcher
**I want** to ensure web scraping follows ethical guidelines and legal requirements
**So that** I can conduct research responsibly without violating site policies or legal boundaries

## Acceptance Criteria
- [ ] When scraping websites, robots.txt files are checked and respected by default
- [ ] When rate limiting is configured, requests are throttled according to settings
- [ ] When Terms of Service violations are detected, scraping is blocked with warnings
- [ ] When sites implement anti-bot measures, the system gracefully handles blocks
- [ ] When ethical mode is enabled, only publicly accessible content is scraped
- [ ] When compliance reports are requested, detailed logs show adherence to policies

## Definition of Done
- [ ] Robots.txt parser and compliance checker
- [ ] Configurable rate limiting with per-domain controls
- [ ] Terms of Service detection and warning system
- [ ] Anti-bot detection and graceful degradation
- [ ] Ethical scraping mode with restrictive defaults
- [ ] Compliance logging and reporting functionality
- [ ] Unit tests cover robots.txt parsing and rate limiting
- [ ] Integration tests verify real-world compliance scenarios
- [ ] Documentation for legal and ethical usage guidelines

## Dependencies
- Design section: [Ethical Scraping Architecture](../../docs/design/osint-platform.md#security-privacy)
- Story: S-004 (Web scraping implementation to control)
- Story: S-009 (Configuration management for scraping policies)

## Links
- PRD: [/docs/product/osint-platform.md](../../docs/product/osint-platform.md)
- Design: [/docs/design/osint-platform.md](../../docs/design/osint-platform.md)
- Tasks: [/planning/tasks/T-010-ethical-controls.md](../tasks/T-010-ethical-controls.md)
- Related: [S-004: Web Scraping](S-004-web-scraping.md), [S-009: Configuration](S-009-config-management.md)

## Test Plan

### Unit Tests (pytest)
- `test_robots_txt_parsing_and_compliance`
- `test_rate_limiting_enforcement`
- `test_terms_of_service_detection`
- `test_user_agent_compliance`
- `test_ethical_mode_restrictions`
- `test_domain_specific_policies`
- `test_compliance_logging`

### Integration Tests (pytest + real sites)
- `test_robots_txt_compliance_real_sites`
- `test_rate_limiting_actual_requests`
- `test_anti_bot_detection_handling`

### Compliance Tests
- `test_major_sites_robots_compliance`
- `test_rate_limiting_stays_within_bounds`
- `test_no_authentication_bypassing`

## AI Coding Brief
```yaml
role: "Senior engineer with web scraping and compliance expertise."
objective: "Implement comprehensive ethical scraping controls."
constraints:
  allowed_paths:
    - backend/app/services/scraper/ethics.py
    - backend/app/services/scraper/rate_limiter.py
    - backend/app/services/scraper/robots_parser.py
    - backend/app/tests/test_ethical_scraping.py
  dependencies: "urllib.robotparser, asyncio for rate limiting"
  testing: "Test against real robots.txt files and rate limits"
  security:
    - "🚨 CRITICAL: NEVER include any AI, Claude, or assistant attribution anywhere"
    - "🚨 CRITICAL: NEVER use phrases like 'Generated with Claude', 'Co-Authored-By: Claude', etc."
    - "🚨 CRITICAL: Do not reference AI assistance in code, comments, commits, or any deliverables"
    - "🚨 CRITICAL: This is a SECURITY REQUIREMENT - violations will be automatically detected and removed"
    - "NEVER bypass authentication or access controls"
tests_to_make_pass:
  - backend/app/tests/test_ethical_scraping.py::test_robots_compliance
  - backend/app/tests/test_ethical_scraping.py::test_rate_limiting
  - backend/app/tests/test_ethical_scraping.py::test_ethical_mode
definition_of_done:
  - "All referenced tests pass in CI"
  - "Robots.txt compliance is enforced for all domains"
  - "Rate limiting prevents server overload"
  - "Ethical mode provides safe defaults for research"
  - "No attribution or AI references in code/commits"
```

## Technical Notes

### Robots.txt Compliance
```python
class RobotsChecker:
    def __init__(self):
        self.cache: Dict[str, RobotFileParser] = {}
        self.cache_ttl = 3600  # 1 hour

    async def can_fetch(self, url: str, user_agent: str) -> bool:
        """Check if URL can be fetched according to robots.txt."""

    async def get_crawl_delay(self, domain: str, user_agent: str) -> Optional[float]:
        """Get crawl delay from robots.txt if specified."""

    def parse_robots_txt(self, robots_url: str) -> RobotFileParser:
        """Parse and cache robots.txt file."""
```

### Rate Limiting
```python
class DomainRateLimiter:
    def __init__(self):
        self.domain_limits: Dict[str, RateLimit] = {}
        self.request_history: Dict[str, List[datetime]] = {}

    async def acquire_permit(self, domain: str) -> None:
        """Wait for rate limit permit before making request."""

    def configure_domain_limit(self, domain: str, requests_per_minute: int):
        """Set domain-specific rate limits."""

    def get_default_delay(self, domain: str) -> float:
        """Calculate appropriate delay based on domain and robots.txt."""
```

### Ethical Scraping Policies
```python
class EthicalScrapingPolicy:
    respect_robots_txt: bool = True
    max_requests_per_minute: int = 10
    crawl_delay_minimum: float = 2.0
    user_agent_required: bool = True
    block_authentication_required: bool = True
    block_dynamic_content_only: bool = True
    allowed_content_types: List[str] = ["text/html", "application/json"]
    blocked_paths: List[str] = ["/admin", "/api", "/private"]

class ComplianceLogger:
    def log_robots_check(self, url: str, allowed: bool, robots_url: str):
        """Log robots.txt compliance check."""

    def log_rate_limit_delay(self, domain: str, delay: float):
        """Log rate limiting delays."""

    def log_blocked_request(self, url: str, reason: str):
        """Log blocked requests with reasons."""
```

### Anti-Bot Detection
```python
class AntiBotHandler:
    def detect_blocking(self, response: Response) -> bool:
        """Detect if request was blocked by anti-bot measures."""

    async def handle_captcha_challenge(self, url: str) -> bool:
        """Handle CAPTCHA challenges (log and skip in ethical mode)."""

    def detect_rate_limit_response(self, response: Response) -> bool:
        """Detect 429 or other rate limiting responses."""

    async def exponential_backoff(self, domain: str, attempt: int):
        """Implement exponential backoff for blocked domains."""
```

### Configuration Options
```python
class ScrapingEthicsConfig:
    ethical_mode: bool = True  # Enable strict ethical defaults
    respect_robots_txt: bool = True
    global_rate_limit: int = 30  # requests per minute
    domain_rate_limits: Dict[str, int] = {}
    user_agent: str = "OSINT-Framework/1.0 (+research purposes)"
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay: float = 5.0
    blocked_domains: List[str] = []  # Domains to never scrape
    allowed_domains: List[str] = []  # Whitelist mode
```

### Compliance Reporting
```python
class ComplianceReport:
    total_requests: int
    blocked_by_robots: int
    rate_limited_requests: int
    failed_requests: int
    domains_accessed: List[str]
    robots_txt_violations: List[dict]
    rate_limit_violations: List[dict]
    ethical_violations: List[dict]
    report_generated_at: datetime

    def generate_summary(self) -> str:
        """Generate human-readable compliance summary."""
```

### Legal Guidelines Documentation
- **Robots.txt**: Always check and respect robots.txt directives
- **Rate Limiting**: Never overwhelm servers with rapid requests
- **Public Content**: Only access publicly available information
- **Terms of Service**: Respect site terms and conditions
- **Copyright**: Don't scrape copyrighted content for redistribution
- **Personal Data**: Be mindful of personal information in scraped content
- **Jurisdiction**: Follow applicable laws in researcher's jurisdiction
