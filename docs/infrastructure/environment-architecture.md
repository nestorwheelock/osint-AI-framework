# Environment Architecture & Infrastructure Design

## Overview

This document outlines the complete infrastructure architecture for the OSINT Research Platform, covering development, staging, and production environments using Docker, PostgreSQL, and automated CI/CD pipelines.

## Environment Strategy

### Development Environment
- **Purpose**: Local development with hot reloading and debugging
- **Infrastructure**: Docker Compose with local containers
- **Database**: PostgreSQL with development data seeding
- **Deployment**: Manual via `docker-compose up`

### Staging Environment
- **Purpose**: Pre-production testing and integration validation
- **Infrastructure**: Cloud-hosted containers (similar to production)
- **Database**: PostgreSQL with production-like data
- **Deployment**: Automated via GitHub Actions on merge to `develop`

### Production Environment
- **Purpose**: Live system for end users
- **Infrastructure**: Cloud-hosted with high availability
- **Database**: PostgreSQL with backup and disaster recovery
- **Deployment**: Automated via GitHub Actions on merge to `main` (with approval)

## Docker Architecture

### Service Composition

```yaml
# docker-compose.yml structure
services:
  # Core Application Services
  backend:          # FastAPI application server
  frontend:         # React/TypeScript development server

  # Data Layer
  database:         # PostgreSQL primary database
  redis:           # Cache and job queue

  # Processing Services
  playwright:       # Web scraping service
  ai-processor:     # Entity extraction service

  # Infrastructure Services
  nginx:           # Reverse proxy and load balancer
  monitoring:      # Application monitoring
```

### Container Specifications

#### Backend Container
```dockerfile
# Multi-stage build for optimization
FROM python:3.11-slim as base
FROM base as development  # Hot reload, debugging tools
FROM base as production   # Optimized, minimal dependencies
```

#### Frontend Container
```dockerfile
FROM node:20-alpine as base
FROM base as development  # Dev server with HMR
FROM base as production   # Static build with nginx
```

#### Database Container
```yaml
database:
  image: postgres:15-alpine
  environment:
    POSTGRES_DB: osint_platform
    POSTGRES_USER: ${DB_USER}
    POSTGRES_PASSWORD: ${DB_PASSWORD}
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./database/init:/docker-entrypoint-initdb.d
```

## Database Architecture

### PostgreSQL Configuration

#### Development Settings
```sql
-- Performance optimized for development
shared_buffers = 256MB
work_mem = 4MB
maintenance_work_mem = 64MB
max_connections = 100
```

#### Production Settings
```sql
-- Performance optimized for production load
shared_buffers = 1GB
work_mem = 16MB
maintenance_work_mem = 256MB
max_connections = 200
random_page_cost = 1.1  -- SSD optimization
```

### Schema Management

#### Migration Strategy
- **Tool**: Alembic for database migrations
- **Process**: Automated migrations in CI/CD pipeline
- **Rollback**: Automated rollback capability for failed deployments
- **Testing**: Migration testing in staging environment

#### Data Seeding
- **Development**: Automated seeding with sample data
- **Staging**: Production-like data for realistic testing
- **Production**: Minimal seeding for system initialization

### Backup Strategy

#### Development
- Daily automated backups to local storage
- 7-day retention policy

#### Production
- Continuous WAL (Write-Ahead Log) streaming
- Daily full backups with 30-day retention
- Point-in-time recovery capability
- Cross-region backup replication

## CI/CD Pipeline Architecture

### GitHub Actions Workflow

```yaml
# .github/workflows/ci-cd.yml structure
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  code-quality:     # Linting, formatting, security scanning
  unit-tests:       # Backend and frontend unit tests
  integration-tests: # API and database integration tests
  e2e-tests:        # Full application end-to-end tests
  build-images:     # Docker image building and optimization
  deploy-staging:   # Automated staging deployment
  deploy-production: # Production deployment (with approval)
```

### Pipeline Stages

#### 1. Code Quality Gate
- **Linting**: ESLint (frontend), flake8/black (backend)
- **Type Checking**: TypeScript, mypy
- **Security Scanning**: Bandit, npm audit, Snyk
- **Code Coverage**: Minimum 80% coverage requirement

#### 2. Testing Stages
- **Unit Tests**: Fast, isolated component testing
- **Integration Tests**: API endpoints and database operations
- **E2E Tests**: Full user workflow validation
- **Performance Tests**: Load testing and benchmarking

#### 3. Build and Deploy
- **Image Building**: Multi-stage Docker builds with caching
- **Registry**: GitHub Container Registry for image storage
- **Deployment**: Rolling updates with health checks
- **Rollback**: Automated rollback on deployment failure

## Infrastructure as Code

### Environment Configuration

#### Development Environment
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  backend:
    build:
      context: ./backend
      target: development
    volumes:
      - ./backend:/app
      - /app/.venv
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
      - DB_HOST=database
```

#### Production Environment
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    build:
      context: ./backend
      target: production
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - DB_HOST=${DB_HOST}
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Resource Allocation

#### Development Resources
- **Backend**: 512MB RAM, 0.5 CPU
- **Frontend**: 256MB RAM, 0.25 CPU
- **Database**: 1GB RAM, 1 CPU
- **Redis**: 128MB RAM, 0.25 CPU

#### Production Resources
- **Backend**: 2GB RAM, 1 CPU (auto-scaling)
- **Frontend**: 512MB RAM, 0.5 CPU
- **Database**: 8GB RAM, 4 CPU
- **Redis**: 1GB RAM, 0.5 CPU

## Security Architecture

### Container Security

#### Security Hardening
- Non-root user execution in all containers
- Minimal base images (Alpine Linux where possible)
- Regular security updates and vulnerability scanning
- Network isolation and service communication controls

#### Secrets Management
- Environment variables for configuration
- Docker secrets for sensitive data
- External secret management integration (AWS Secrets Manager, etc.)
- Rotation policies for API keys and credentials

### Network Security

#### Service Communication
- Internal Docker network for service-to-service communication
- TLS encryption for all external communications
- API rate limiting and DDoS protection
- Database connection encryption

#### Access Controls
- Role-based access control (RBAC) implementation
- API authentication and authorization
- Database user permissions and access logging
- Administrative access audit trails

## Monitoring and Observability

### Application Monitoring

#### Metrics Collection
- **Performance**: Response times, throughput, error rates
- **Resource Usage**: CPU, memory, disk I/O
- **Business Metrics**: User activity, research operations
- **Infrastructure**: Container health, database performance

#### Logging Strategy
- **Structured Logging**: JSON format for all application logs
- **Centralized Collection**: Log aggregation and search
- **Log Levels**: Debug, info, warning, error, critical
- **Retention**: 30 days for development, 90 days for production

#### Alerting System
- **Performance Alerts**: Response time degradation, error rate spikes
- **Infrastructure Alerts**: Container failures, resource exhaustion
- **Security Alerts**: Authentication failures, suspicious activity
- **Business Alerts**: System downtime, data processing failures

### Health Checks

#### Service Health Endpoints
```python
# Backend health check
@app.get("/healthz")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "database": check_database_connection(),
        "redis": check_redis_connection()
    }
```

#### Infrastructure Health
- Container orchestration health checks
- Database connection pool monitoring
- External API dependency checks
- File system and storage health validation

## Deployment Procedures

### Automated Deployment Process

#### Staging Deployment
1. **Trigger**: Merge to `develop` branch
2. **Testing**: Run full test suite
3. **Build**: Create and tag Docker images
4. **Deploy**: Rolling update to staging environment
5. **Validation**: Automated smoke tests
6. **Notification**: Team notification of deployment status

#### Production Deployment
1. **Trigger**: Merge to `main` branch (requires approval)
2. **Pre-deployment**: Database migration validation
3. **Build**: Production-optimized Docker images
4. **Deploy**: Blue-green deployment strategy
5. **Monitoring**: Enhanced monitoring during deployment
6. **Rollback**: Automated rollback on failure detection

### Manual Deployment Procedures

#### Emergency Hotfix Process
1. Create hotfix branch from `main`
2. Apply minimal fix and test locally
3. Fast-track review and approval
4. Direct deployment to production
5. Post-deployment validation and monitoring

#### Database Migration Process
1. Test migration in staging environment
2. Create database backup before migration
3. Run migration with rollback preparation
4. Validate data integrity post-migration
5. Monitor performance impact

## Disaster Recovery

### Backup Procedures

#### Automated Backups
- **Database**: Continuous WAL streaming + daily full backups
- **Application Data**: Daily incremental backups
- **Configuration**: Version-controlled infrastructure code
- **Monitoring**: Backup validation and integrity checks

#### Recovery Procedures
- **Point-in-Time Recovery**: Database restoration to specific timestamp
- **Full System Recovery**: Complete environment restoration
- **Partial Recovery**: Individual service restoration
- **Data Migration**: Cross-environment data synchronization

### Business Continuity

#### High Availability
- Multi-container deployment with load balancing
- Database replication and failover
- Geographic distribution for disaster resilience
- Automated scaling based on demand

#### Recovery Time Objectives
- **Database Recovery**: < 15 minutes
- **Application Recovery**: < 30 minutes
- **Full System Recovery**: < 2 hours
- **Data Loss Tolerance**: < 1 hour of data