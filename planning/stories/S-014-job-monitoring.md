# S-014 — Job Monitoring

**As a** OSINT researcher
**I want** to monitor the progress of long-running analysis tasks
**So that** I can track completion status and identify any issues or bottlenecks

## Acceptance Criteria
- [ ] When long-running jobs are started, progress tracking is automatically enabled
- [ ] When jobs are running, real-time progress updates are displayed in the interface
- [ ] When jobs encounter errors, detailed error messages and recovery options are provided
- [ ] When multiple jobs run concurrently, resource usage and queue status are visible
- [ ] When jobs complete, notifications and result summaries are provided
- [ ] When jobs fail, automatic retry logic attempts recovery with backoff delays

## Definition of Done
- [ ] Job tracking system for all long-running operations
- [ ] Real-time progress updates via WebSocket or polling
- [ ] Error handling and recovery mechanisms
- [ ] Job queue management with priority handling
- [ ] Resource usage monitoring and limits
- [ ] Notification system for job completion/failure
- [ ] Unit tests cover job lifecycle and error scenarios
- [ ] Integration tests verify job monitoring accuracy
- [ ] E2E tests confirm real-time UI updates

## Dependencies
- Design section: [Job Monitoring](../../docs/design/osint-platform.md#operational-excellence)
- All stories that involve background processing (S-004, S-006, S-008, S-013)
- Background job system (Celery or similar)

## Links
- PRD: [/docs/product/osint-platform.md](../../docs/product/osint-platform.md)
- Design: [/docs/design/osint-platform.md](../../docs/design/osint-platform.md)
- Tasks: [/planning/tasks/T-014-job-monitoring.md](../tasks/T-014-job-monitoring.md)
- Related: All background processing stories

## Test Plan

### Unit Tests (pytest)
- `test_job_creation_and_tracking`
- `test_progress_update_mechanisms`
- `test_error_handling_and_recovery`
- `test_job_queue_management`
- `test_resource_limit_enforcement`
- `test_automatic_retry_logic`
- `test_job_cleanup_and_archival`

### Integration Tests (pytest + job queue)
- `test_real_job_monitoring_workflow`
- `test_concurrent_job_handling`
- `test_job_failure_recovery`

### E2E Tests (Playwright)
- `test_job_progress_ui_updates`
- `test_job_cancellation_workflow`
- `test_job_history_and_logs`

## AI Coding Brief
```yaml
role: "Senior engineer with background processing and monitoring expertise."
objective: "Implement comprehensive job monitoring and management system."
constraints:
  allowed_paths:
    - backend/app/services/job_monitor/
    - backend/app/models/job.py
    - backend/app/routes/jobs.py
    - backend/app/tests/test_job_monitor.py
  dependencies: "Celery for background jobs, WebSockets for real-time updates"
  testing: "Test job lifecycle, error handling, and progress tracking"
  security:
    - "🚨 CRITICAL: NEVER include any AI, Claude, or assistant attribution anywhere"
    - "🚨 CRITICAL: NEVER use phrases like 'Generated with Claude', 'Co-Authored-By: Claude', etc."
    - "🚨 CRITICAL: Do not reference AI assistance in code, comments, commits, or any deliverables"
    - "🚨 CRITICAL: This is a SECURITY REQUIREMENT - violations will be automatically detected and removed"
tests_to_make_pass:
  - backend/app/tests/test_job_monitor.py::test_job_tracking
  - backend/app/tests/test_job_monitor.py::test_progress_updates
  - backend/app/tests/test_job_monitor.py::test_error_recovery
definition_of_done:
  - "All referenced tests pass in CI"
  - "Job monitoring provides accurate real-time status updates"
  - "Error handling and recovery work reliably"
  - "Job queue management prevents system overload"
  - "No attribution or AI references in code/commits"
```

## Technical Notes

### Job Monitoring Models
```python
class Job(Base):
    id: UUID
    job_type: JobType  # SCRAPING, ENTITY_EXTRACTION, EXPORT, REPORT_GENERATION
    subject_id: Optional[UUID]
    status: JobStatus  # PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
    progress_percent: int
    current_step: str
    total_steps: int
    completed_steps: int
    priority: JobPriority  # LOW, NORMAL, HIGH, URGENT

    # Timing information
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_duration: Optional[int]  # seconds

    # Resource usage
    memory_usage_mb: Optional[int]
    cpu_usage_percent: Optional[float]

    # Results and errors
    result_data: Optional[dict]
    error_message: Optional[str]
    error_traceback: Optional[str]
    retry_count: int
    max_retries: int

    # Metadata
    created_by: str
    worker_id: Optional[str]
    queue_name: str

class JobLog(Base):
    id: UUID
    job_id: UUID
    level: LogLevel  # DEBUG, INFO, WARNING, ERROR
    message: str
    timestamp: datetime
    step_name: Optional[str]
    data: Optional[dict]
```

### Job Management Service
```python
class JobManager:
    def create_job(self, job_type: JobType, **kwargs) -> Job:
        """Create and queue a new background job."""

    def update_progress(self, job_id: UUID, progress: int, current_step: str):
        """Update job progress and current step."""

    def mark_completed(self, job_id: UUID, result_data: dict):
        """Mark job as completed with results."""

    def mark_failed(self, job_id: UUID, error: str, traceback: str):
        """Mark job as failed with error details."""

    def cancel_job(self, job_id: UUID, reason: str) -> bool:
        """Attempt to cancel a running job."""

    def retry_job(self, job_id: UUID) -> Job:
        """Retry a failed job with exponential backoff."""
```

### Progress Tracking
```python
class ProgressTracker:
    def __init__(self, job_id: UUID, total_steps: int):
        self.job_id = job_id
        self.total_steps = total_steps
        self.current_step = 0

    def update_step(self, step_name: str, increment: int = 1):
        """Update current step and calculate progress percentage."""

    def log_info(self, message: str, **data):
        """Log informational message for job."""

    def log_error(self, message: str, **data):
        """Log error message for job."""

    def set_estimated_duration(self, seconds: int):
        """Set estimated completion time."""
```

### Real-time Updates
```python
class JobNotificationService:
    def __init__(self):
        self.websocket_manager = WebSocketManager()

    async def notify_progress_update(self, job_id: UUID, progress_data: dict):
        """Send real-time progress update to connected clients."""

    async def notify_job_completed(self, job_id: UUID, result_summary: dict):
        """Notify clients of job completion."""

    async def notify_job_failed(self, job_id: UUID, error_info: dict):
        """Notify clients of job failure."""

    def send_email_notification(self, user_email: str, job: Job):
        """Send email notification for important job events."""
```

### Resource Management
```python
class ResourceManager:
    def __init__(self):
        self.max_concurrent_jobs = 10
        self.memory_limit_mb = 2048
        self.cpu_threshold = 80.0

    def can_start_job(self, job_type: JobType) -> bool:
        """Check if system has resources to start new job."""

    def monitor_resource_usage(self, job_id: UUID):
        """Monitor and log resource usage for running job."""

    def enforce_resource_limits(self, job_id: UUID) -> bool:
        """Terminate job if it exceeds resource limits."""

    def get_queue_statistics(self) -> dict:
        """Get current queue status and resource usage."""
```

### Error Recovery
```python
class ErrorRecoveryService:
    def __init__(self):
        self.retry_delays = [60, 300, 900, 3600]  # exponential backoff

    def should_retry(self, job: Job, error: Exception) -> bool:
        """Determine if job should be retried based on error type."""

    def calculate_retry_delay(self, retry_count: int) -> int:
        """Calculate delay before next retry attempt."""

    def handle_job_failure(self, job: Job, error: Exception):
        """Process job failure and determine recovery action."""

    def cleanup_failed_jobs(self, older_than_days: int = 7):
        """Clean up old failed jobs and their artifacts."""
```

### API Endpoints
```
GET    /jobs                                - List jobs with filtering
GET    /jobs/{job_id}                       - Get specific job details
POST   /jobs/{job_id}/cancel                - Cancel running job
POST   /jobs/{job_id}/retry                 - Retry failed job
GET    /jobs/{job_id}/logs                  - Get job execution logs
GET    /jobs/stats                          - Get queue and system statistics
WebSocket /ws/jobs/{job_id}                 - Real-time job updates
```

### Job Types and Workflows
```python
class JobTypes:
    WEB_SCRAPING = "web_scraping"        # S-004
    ENTITY_EXTRACTION = "entity_extraction"  # S-006
    DATA_EXPORT = "data_export"          # S-008
    PDF_GENERATION = "pdf_generation"    # S-013
    DUPLICATE_DETECTION = "duplicate_detection"  # S-012
    TIMELINE_ASSEMBLY = "timeline_assembly"      # S-011

# Example job workflow for web scraping
def scrape_urls_job(subject_id: UUID, urls: List[str]) -> None:
    tracker = ProgressTracker(job_id, len(urls))

    for i, url in enumerate(urls):
        tracker.update_step(f"Scraping {url}")
        try:
            # Perform scraping
            result = scrape_webpage(url)
            tracker.log_info(f"Successfully scraped {url}")
        except Exception as e:
            tracker.log_error(f"Failed to scrape {url}: {str(e)}")

    tracker.update_step("Completed", len(urls))
```
