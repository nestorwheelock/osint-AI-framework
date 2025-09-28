# S-009 — Configuration Management

**As a** OSINT researcher
**I want** to securely manage system configuration and API keys
**So that** I can customize behavior without exposing sensitive information

## Acceptance Criteria
- [ ] When I configure search engines, API keys are stored securely
- [ ] When I set system defaults, they apply globally unless overridden per session
- [ ] When configuration changes, the system validates settings before applying
- [ ] When secrets are stored, they are encrypted and not logged in plain text
- [ ] When I view configuration, sensitive values are masked in the interface
- [ ] When configuration is invalid, clear error messages guide correction

## Definition of Done
- [ ] Configuration management system with environment variable support
- [ ] Secure storage of API keys and sensitive configuration
- [ ] Configuration validation with schema enforcement
- [ ] UI for safe configuration management (masked sensitive fields)
- [ ] Default configuration with per-session override capability
- [ ] Configuration versioning and rollback functionality
- [ ] Unit tests cover configuration logic and validation
- [ ] Integration tests verify configuration application
- [ ] Security tests ensure no secrets leak in logs/responses

## Dependencies
- Design section: [Configuration Management](../../docs/design/osint-platform.md#core-services)
- Security: Secret encryption and environment variable handling
- All stories that require configuration (search engines, AI APIs)

## Links
- PRD: [/docs/product/osint-platform.md](../../docs/product/osint-platform.md)
- Design: [/docs/design/osint-platform.md](../../docs/design/osint-platform.md)
- Tasks: [/planning/tasks/T-009-config-management.md](../tasks/T-009-config-management.md)

## Test Plan

### Unit Tests (pytest)
- `test_config_validation_schemas`
- `test_secret_encryption_decryption`
- `test_environment_variable_loading`
- `test_config_override_hierarchy`
- `test_invalid_config_error_handling`
- `test_sensitive_field_masking`
- `test_config_rollback_functionality`

### Integration Tests (pytest + database)
- `test_config_persistence_and_retrieval`
- `test_config_changes_apply_to_services`
- `test_session_level_config_overrides`

### Security Tests
- `test_secrets_not_in_logs`
- `test_api_responses_mask_sensitive_data`
- `test_config_file_permissions`

## AI Coding Brief
```yaml
role: "Senior backend engineer with security and configuration expertise."
objective: "Implement secure configuration management with encryption."
constraints:
  allowed_paths:
    - backend/app/services/config/
    - backend/app/models/configuration.py
    - backend/app/routes/config.py
    - backend/app/tests/test_config.py
  dependencies: "Pydantic for validation, cryptography for encryption"
  testing: "Test validation, encryption, and security scenarios"
  security:
    - "🚨 CRITICAL: NEVER include any AI, Claude, or assistant attribution anywhere"
    - "🚨 CRITICAL: NEVER use phrases like 'Generated with Claude', 'Co-Authored-By: Claude', etc."
    - "🚨 CRITICAL: Do not reference AI assistance in code, comments, commits, or any deliverables"
    - "🚨 CRITICAL: This is a SECURITY REQUIREMENT - violations will be automatically detected and removed"
    - "NEVER log or expose API keys or sensitive configuration"
tests_to_make_pass:
  - backend/app/tests/test_config.py::test_secure_config_storage
  - backend/app/tests/test_config.py::test_config_validation
  - backend/app/tests/test_config.py::test_secret_encryption
definition_of_done:
  - "All referenced tests pass in CI"
  - "Configuration system handles secrets securely"
  - "Validation prevents invalid configuration from breaking system"
  - "UI provides safe configuration management"
  - "No attribution or AI references in code/commits"
```

## Technical Notes

### Configuration Schema
```python
class SystemConfig(BaseModel):
    # Search Engine Configuration
    search_engines: SearchEngineConfig

    # AI/ML Configuration
    ai_config: AIConfig

    # Scraping Configuration
    scraping_config: ScrapingConfig

    # System Defaults
    defaults: DefaultsConfig

class SearchEngineConfig(BaseModel):
    google_api_key: Optional[SecretStr] = None
    google_search_engine_id: Optional[str] = None
    bing_api_key: Optional[SecretStr] = None
    enabled_engines: List[str] = ["duckduckgo"]  # Free engines by default

class AIConfig(BaseModel):
    openai_api_key: Optional[SecretStr] = None
    openai_model: str = "gpt-3.5-turbo"
    max_tokens_per_request: int = 4000
    enable_local_models: bool = True
    monthly_budget_usd: Optional[float] = None

class ScrapingConfig(BaseModel):
    default_timeout: int = 30
    max_concurrent_requests: int = 5
    user_agent: str = "OSINT-Framework/1.0"
    respect_robots_txt: bool = True
    rate_limit_delay: float = 2.0
```

### Configuration Storage
```python
class Configuration(Base):
    id: UUID
    config_type: ConfigType  # SYSTEM, SESSION, USER
    reference_id: Optional[UUID]  # session_id or user_id
    config_key: str
    config_value_encrypted: str  # Encrypted JSON
    is_sensitive: bool
    created_at: datetime
    updated_at: datetime
    created_by: str

class ConfigurationHistory(Base):
    id: UUID
    configuration_id: UUID
    previous_value_encrypted: str
    changed_by: str
    changed_at: datetime
    change_reason: Optional[str]
```

### Secret Encryption
```python
class SecretManager:
    def __init__(self, encryption_key: str):
        self.fernet = Fernet(encryption_key.encode())

    def encrypt_secret(self, value: str) -> str:
        """Encrypt sensitive configuration values."""
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt_secret(self, encrypted_value: str) -> str:
        """Decrypt sensitive configuration values."""
        return self.fernet.decrypt(encrypted_value.encode()).decode()

    def mask_for_display(self, value: str) -> str:
        """Mask sensitive values for UI display."""
        if len(value) <= 8:
            return "*" * len(value)
        return value[:4] + "*" * (len(value) - 8) + value[-4:]
```

### Configuration Hierarchy
```
1. Environment Variables (highest priority)
2. Session Configuration (per investigation)
3. User Configuration (per user)
4. System Configuration (global defaults)
5. Built-in Defaults (lowest priority)
```

### API Endpoints
```
GET    /config                              - Get effective configuration
PUT    /config                              - Update system configuration
GET    /config/sessions/{session_id}        - Get session-specific config
PUT    /config/sessions/{session_id}        - Update session configuration
POST   /config/validate                     - Validate configuration schema
GET    /config/history                      - View configuration changes
POST   /config/rollback/{version_id}        - Rollback to previous version
```

### Environment Variable Support
```bash
# Search Engines
GOOGLE_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
BING_API_KEY=your_bing_api_key

# AI Services
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
AI_MONTHLY_BUDGET=100.00

# System Settings
DEFAULT_TIMEOUT=30
MAX_CONCURRENT_REQUESTS=5
RATE_LIMIT_DELAY=2.0
```

### Security Considerations
- **Encryption**: All sensitive values encrypted at rest
- **Logging**: Never log decrypted secrets or API keys
- **API**: Mask sensitive fields in all API responses
- **Files**: Restrict file permissions on configuration files
- **Validation**: Sanitize and validate all configuration input
