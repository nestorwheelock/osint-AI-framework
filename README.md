# OSINT AI Framework

A comprehensive AI-powered Open Source Intelligence framework that leverages multiple AI technologies for intelligent data collection, analysis, and automated reporting. Built with Django and modern DevOps practices, featuring advanced AI capabilities and automated workflows.

##  Project Overview

The OSINT AI Framework provides intelligence professionals and researchers with comprehensive AI-enhanced tools to:

- **Systematically collect data** from multiple web sources using ethical scraping
- **Analyze content** with AI-powered entity extraction and pattern recognition
- **Organize research** around subjects and investigation sessions
- **Generate reports** in multiple formats with timeline assembly
- **Maintain compliance** with robots.txt and rate limiting controls

### Key Features

-  **Multi-Engine Search**: Integrate Google, Bing, DuckDuckGo, and custom sources
-  **Web Scraping**: Playwright-based automation with JavaScript support
-  **AI Analysis**: OpenAI-powered entity extraction and content analysis
-  **Smart Organization**: Subject-based research with tagging and filtering
-  **Timeline Assembly**: Chronological reconstruction of findings
-  **Report Generation**: Professional PDF reports with customizable templates
-  **Ethical Controls**: Built-in compliance with robots.txt and rate limiting
-  **Real-time Monitoring**: Job progress tracking and status updates

##  Architecture

### Technology Stack

- **Backend**: Django + Django REST Framework + Celery
- **Frontend**: React + TypeScript + Vite
- **Database**: PostgreSQL with Redis for caching and job queues
- **Search**: Playwright for web scraping with multiple search engine adapters
- **AI**: OpenAI GPT models for entity extraction and analysis
- **Infrastructure**: Docker + Docker Compose with GitHub Actions CI/CD
- **Testing**: pytest (backend) + Jest + Playwright (frontend/E2E)

### System Architecture

```
        
   Frontend             Backend API          AI Pipeline   
   (React/TS)       (Django)         (Celery Jobs) 
        
                                                       
                                                       
        
   Web Scraping         PostgreSQL           File Storage  
   (Playwright)         (Metadata)           (HTML/PDFs)   
        
```

### Core Services

1. **Subject Management**: Create and organize investigation targets
2. **Search Orchestrator**: Coordinate multi-engine search queries
3. **Web Scraper**: Playwright-based page fetching and content extraction
4. **Content Processor**: Text extraction, language detection, deduplication
5. **AI Analyzer**: Entity extraction and content analysis pipelines
6. **Export Engine**: Generate reports in multiple formats (JSONL, PDF)
7. **Job Monitor**: Real-time progress tracking and status updates

##  Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended)
- **Python 3.11+** (for local development)
- **Node.js 20+** (for frontend development)
- **PostgreSQL** (if running without Docker)
- **Redis** (for job queues and caching)

### Option 1: Docker Development (Recommended)

```bash
# Clone the repository
git clone https://github.com/nestorwheelock/osint-AI-framework.git
cd osint-AI-framework

# Copy environment configuration
cp .env.example .env
# Edit .env with your API keys (OpenAI, etc.)

# Start all services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f

# Run database migrations
docker-compose exec backend python manage.py migrate

# Create superuser (optional)
docker-compose exec backend python manage.py createsuperuser

# Access the application
# Backend API: http://localhost:8000
# Frontend: http://localhost:3000
# Admin: http://localhost:8000/admin
```

### Option 2: Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install dependencies
pip install -U pip
pip install -e .[dev]

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver

# Run tests
pytest
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Install Playwright browsers
npx playwright install

# Start development server
npm run dev

# Run tests
npm test

# Run E2E tests
npx playwright test
```

### Environment Configuration

Create `.env` file with required variables:

```bash
# Database
DATABASE_URL=postgresql://osint_user:password@localhost:5432/osint_platform

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys
OPENAI_API_KEY=your_openai_api_key_here

# Django Settings
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Frontend
VITE_API_BASE_URL=http://localhost:8000
```

##  AI-Assisted Development

This project is optimized for AI-assisted development with **Claude Code**:

### Built-in Claude Integration

- ** Structured Planning**: Complete project documentation with PRDs, design docs, and user stories
- ** Task-Ready Workflows**: Granular task breakdowns that Claude can execute independently
- ** Test-Driven Development**: Built-in TDD approach with comprehensive testing
- ** Documentation Links**: Cross-referenced documentation for full context
- ** AI Coding Briefs**: Specific instructions for each development task

### Working with Claude Code

The project includes GitHub Actions integration for Claude Code:

1. **@claude mentions** in issues and PRs trigger AI assistance
2. **Automated issue creation** from markdown task files
3. **Project board integration** with automated status updates
4. **Bidirectional sync** between planning files and GitHub Issues

#### Quick Claude Commands

**Start a new feature:**
```
Read the design document and implement user story S-001. Follow the test-driven development approach and update the issue with progress.
```

**Review and fix:**
```
@claude review this PR for security, performance, and adherence to Django best practices.
```

**Setup assistance:**
```
@claude help me set up the development environment following the installation guide.
```

### Project Structure for AI Development

```
 docs/                          # Human-readable documentation
    product/                   # Product requirements documents
    design/                    # Architecture and design documents
    infrastructure/            # DevOps and deployment guides
    devops/                    # GitHub integration documentation
 planning/                      # Machine-friendly planning
    stories/                   # User stories (S-001 to S-015)
    tasks/                     # Task breakdowns (T-001 to T-015)
    backlog.md                 # Epic overview and sprint planning
 backend/                       # Django application
    apps/                      # Django apps (subjects, search, etc.)
    config/                    # Django settings and configuration
    tests/                     # Backend tests
 frontend/                      # React application
    src/                       # Source code
    tests/                     # Frontend tests
 .github/                       # GitHub integration
     workflows/                 # CI/CD and automation
     ISSUE_TEMPLATE/            # Issue templates for different task types
```

##  Development Guide

### User Stories and Epic Overview

The platform is built around **15 user stories** organized into **5 sprints**:

#### Pre-Sprint: Infrastructure (S-000)
- **S-000**: Environment setup, Docker configuration, CI/CD pipeline

#### Sprint 1: Foundation (S-001, S-002, S-009)
- **S-001**: Subject creation and management
- **S-002**: Investigation session management
- **S-009**: Configuration and settings management

#### Sprint 2: Data Collection (S-003, S-004, S-010)
- **S-003**: Multi-engine meta-search implementation
- **S-004**: Playwright web scraping with JavaScript support
- **S-010**: Ethical scraping controls and compliance

#### Sprint 3: Content Processing (S-005, S-006, S-007, S-008)
- **S-005**: Text extraction and language detection
- **S-006**: AI-powered entity extraction and analysis
- **S-007**: Labeling and filtering system
- **S-008**: Export functionality (JSONL, reports)

#### Sprint 4: Enhanced Features (S-011, S-012, S-013, S-014)
- **S-011**: Timeline assembly and chronological reconstruction
- **S-012**: Content deduplication and similarity detection
- **S-013**: Professional PDF report generation
- **S-014**: Real-time job monitoring and progress tracking

#### Sprint 5: Integration (S-015)
- **S-015**: Final integration, performance optimization, production deployment

### Development Workflow

1. **Planning**: Review user stories in `planning/stories/`
2. **Task Breakdown**: Follow task lists in `planning/tasks/`
3. **Implementation**: Use test-driven development approach
4. **Testing**: Run full test suite (backend + frontend + E2E)
5. **Review**: Use Claude Code for automated code review
6. **Integration**: Automated deployment via GitHub Actions

### Testing Strategy

#### Backend Testing (Django + pytest)
```bash
# Run all backend tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest apps/subjects/tests.py

# Run specific test
pytest apps/subjects/tests.py::TestSubjectCRUD::test_create_subject
```

#### Frontend Testing (Jest + React Testing Library)
```bash
# Run unit tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- src/components/SubjectList.test.tsx
```

#### End-to-End Testing (Playwright)
```bash
# Run all E2E tests
npx playwright test

# Run in headed mode
npx playwright test --headed

# Run specific test
npx playwright test tests/subject-management.spec.ts

# Generate test report
npx playwright show-report
```

##  GitHub Integration & Automation

### Automated Workflows

The project includes comprehensive GitHub Actions automation:

#### 1. Task-to-Issue Synchronization
- **Trigger**: Changes to `planning/tasks/*.md` files
- **Action**: Automatically creates/updates GitHub Issues
- **Labels**: Smart labeling based on priority, component, and epic

#### 2. Claude Code Integration
- **Trigger**: @claude mentions in issues/PRs
- **Action**: AI-powered code review and assistance
- **Context**: Automatic loading of relevant documentation

#### 3. Project Board Automation
- **Trigger**: Issue/PR lifecycle events
- **Action**: Updates project board status automatically
- **Features**: Auto-assignment, status transitions, progress tracking

#### 4. Bidirectional Sync
- **Purpose**: Keep markdown files and GitHub Issues synchronized
- **Features**: Conflict resolution, integrity validation, change tracking

### Setting Up GitHub Integration

#### Prerequisites: GitHub CLI Authentication

** REQUIRED BEFORE AUTOMATION**: You must authenticate GitHub CLI with proper permissions.

```bash
# Install GitHub CLI (if needed)
# macOS: brew install gh
# Ubuntu/Debian: sudo apt install gh
# Windows: Download from https://cli.github.com/

# Authenticate with full permissions
gh auth login
# Choose: GitHub.com → HTTPS → Yes → Login with browser
# Grant ALL requested permissions in browser

# Verify authentication
gh auth status
# Should show:  Logged in with 'repo', 'project', 'read:org' scopes
```

**Authentication Troubleshooting:**

| Issue | Cause | Solution |
|-------|-------|----------|
| `HTTP 401: Bad credentials` | Invalid/expired token | `unset GH_TOKEN && gh auth login --scopes "repo,read:org,project,gist,workflow"` |
| `Missing project scope` | Token lacks project permissions | Re-authenticate and grant ALL permissions in browser |
| `Validation Failed (HTTP 422)` | Label format error | Fixed in latest version - update scripts |
| `Authentication failed for Git` | HTTPS auth issues | `git remote set-url origin git@github.com:user/repo.git` |

**Complete Authentication Reset:**
```bash
# 1. Clear all conflicting tokens
unset GH_TOKEN
unset GITHUB_TOKEN

# 2. Re-authenticate with all required scopes
gh auth login --scopes "repo,read:org,project,gist,workflow"

# 3. Verify authentication
gh auth status
# Should show:  Token scopes: 'gist', 'project', 'read:org', 'repo', 'workflow'

# 4. Switch Git to SSH for reliable operations
git remote set-url origin git@github.com:nestorwheelock/osint-AI-framework.git
```

#### Option 1: Automated Setup (Recommended)

Use the automation scripts to set up everything automatically:

```bash
# Complete GitHub project setup
./scripts/setup-github-project.sh

# Or with custom options
./scripts/setup-github-project.sh \
  --repo owner/repo-name \
  --project-name "OSINT AI Framework Development" \
  --dry-run

# Check what would be done
./scripts/setup-github-project.sh --dry-run --verbose
```

**Enhanced Automation Features**:
-  **Repository Configuration**: Merge policies, auto-delete branches
-  **15 Standardized Labels**: `type-feature`, `priority-high`, `size-medium`, etc.
-  **GitHub Project Creation**: GraphQL-based with fallback to CLI
-  **Custom Project Fields**: Status (5 options), Priority (3 options), Size (3 options)
-  **Issue Generation**: Creates issues from all user story files with proper labeling
-  **Project Milestones**: MVP, Beta, v1.0, v1.1
-  **Error Recovery**: Handles authentication issues with detailed troubleshooting

#### Option 2: Manual Setup

1. **Create GitHub Project Board**

Follow the detailed guide in `docs/devops/github-project-setup.md`:

- Create new GitHub Project (Table view)
- Configure custom fields (Epic, Priority, Sprint, Component)
- Set up multiple views (Board, Timeline, Sprint Planning)
- Enable built-in automations

2. **Configure Repository Secrets**

Add these secrets in your GitHub repository settings:

```
ANTHROPIC_API_KEY      # Your Claude API key
PROJECT_TOKEN          # Personal access token with project permissions
```

#### Bidirectional Planning Workflow

For hybrid AI + client planning workflows:

```bash
# 1. AI creates initial stories (already done)
# 2. Set up GitHub Project
./scripts/setup-github-project.sh

# 3. Client planning in GitHub Projects GUI
# (Use web interface for collaboration)

# 4. Sync changes back to files for next AI sprint
./scripts/sync-github-projects.py owner/repo --sync-to-files

# 5. Check sync status
./scripts/sync-github-projects.py owner/repo --status
```

**Workflow Benefits**:
-  **Files remain source of truth** for AI development
-  **GitHub Projects GUI** for client collaboration
-  **Bidirectional sync** keeps everything in sync
-  **AI-ready updates** for next development sprint

### Issue Templates

The project includes specialized issue templates:

- ** User Story**: Complete user story with acceptance criteria
- ** Backend Task**: Django backend development tasks
- ** Frontend Task**: React frontend development tasks
- ** Infrastructure Task**: DevOps and environment setup tasks
- ** Epic**: High-level feature tracking and management

##  Deployment

### Development Deployment

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Run database migrations
docker-compose exec backend python manage.py migrate

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput
```

### Environment-Specific Configuration

#### Development (`docker-compose.dev.yml`)
- Django development server with hot reload
- Debug mode enabled
- Volume mounting for live code changes
- Exposed ports for debugging

#### Production (`docker-compose.prod.yml`)
- Gunicorn WSGI server
- Optimized Docker images
- Environment variable configuration
- Health checks and restart policies

### Monitoring and Logging

#### Health Checks
- **Backend**: `/healthz/` endpoint checks database and Redis connectivity
- **Frontend**: Build status and asset loading validation
- **Infrastructure**: Docker container health monitoring

#### Logging Strategy
- **Structured JSON logs** for all application components
- **Request/response logging** for API debugging
- **Error tracking** with stack traces and context
- **Performance metrics** for optimization insights

##  Troubleshooting

### Common Issues

#### Docker Issues
```bash
# Reset Docker environment
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# Check container logs
docker-compose logs backend
```

#### Database Issues
```bash
# Reset database
docker-compose exec backend python manage.py flush
docker-compose exec backend python manage.py migrate
```

#### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

#### Port Conflicts
```bash
# Check port usage
sudo lsof -i :8000
sudo lsof -i :3000

# Kill conflicting processes
sudo kill -9 $(sudo lsof -t -i :8000)
```

### Performance Optimization

#### Backend Performance
- **Database Query Optimization**: Use Django Debug Toolbar
- **Caching Strategy**: Redis for frequently accessed data
- **API Response Time**: Target <200ms (95th percentile)

#### Frontend Performance
- **Bundle Optimization**: Code splitting and lazy loading
- **Asset Optimization**: Image compression and CDN usage
- **Render Performance**: React component memoization

### Getting Help

1. **Documentation**: Check `docs/` directory for detailed guides
2. **GitHub Issues**: Use issue templates for bug reports and feature requests
3. **Claude Code**: Use @claude mentions for AI assistance
4. **Community**: Contribute improvements and share experiences

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Fork the repository** and create a feature branch
2. **Follow the development workflow** with test-driven development
3. **Use the issue templates** for consistent task definition
4. **Leverage Claude Code** for AI-assisted development
5. **Submit pull requests** with comprehensive testing

### Development Standards

- **Code Quality**: Follow Django and React best practices
- **Testing**: Maintain >95% test coverage
- **Documentation**: Update docs for all changes
- **Security**: Never commit secrets or API keys
- **AI Ethics**: No AI attribution in code or commits

##  Useful Links

- ** Project Planning**: [planning/backlog.md](planning/backlog.md)
- ** Architecture Guide**: [docs/design/osint-platform.md](docs/design/osint-platform.md)
- ** Claude Integration**: [docs/devops/github-ai-integration.md](docs/devops/github-ai-integration.md)
- ** Deployment Guide**: [docs/infrastructure/installation-guide.md](docs/infrastructure/installation-guide.md)
- ** GitHub Project Setup**: [docs/devops/github-project-setup.md](docs/devops/github-project-setup.md)

---

**
