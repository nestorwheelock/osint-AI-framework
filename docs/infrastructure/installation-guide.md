# OSINT Platform Installation & Setup Guide

## Prerequisites

### System Requirements

#### Development Environment
- **OS**: Linux, macOS, or Windows with WSL2
- **RAM**: Minimum 8GB, Recommended 16GB
- **Storage**: 20GB free space
- **CPU**: Multi-core processor (4+ cores recommended)

#### Software Dependencies
- **Docker**: Version 24.0 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: Version 2.30 or higher
- **Node.js**: Version 20 LTS (for frontend development)
- **Python**: Version 3.11 (for backend development)

#### Account Requirements
- **GitHub**: For repository access and CI/CD
- **Docker Hub**: For container registry access
- **OpenAI**: API key for AI entity extraction

### Installation Steps

#### 1. Install Docker and Docker Compose

##### Linux (Ubuntu/Debian)
```bash
# Update package index
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

##### macOS
```bash
# Install Docker Desktop
brew install --cask docker

# Start Docker Desktop and verify
docker --version
docker-compose --version
```

##### Windows with WSL2
```powershell
# Install Docker Desktop for Windows
# Download from: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe

# Verify in WSL2
docker --version
docker-compose --version
```

#### 2. Clone Repository

```bash
# Clone the repository
git clone https://github.com/nestorwheelock/osint-AI-framework.git
cd osint-AI-framework

# Verify repository structure
ls -la
```

#### 3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Required environment variables:
```bash
# Database Configuration
DB_HOST=database
DB_PORT=5432
DB_NAME=osint_platform
DB_USER=osint_user
DB_PASSWORD=secure_password_123

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_password_123

# API Keys
OPENAI_API_KEY=your_openai_api_key_here

# Application Configuration
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1

# Frontend Configuration
VITE_API_BASE_URL=http://localhost:8000
```

## Development Environment Setup

### Quick Start

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# View running services
docker-compose ps

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Individual Service Management

#### Backend Development
```bash
# Start backend with hot reload
docker-compose -f docker-compose.dev.yml up backend database redis -d

# View backend logs
docker-compose logs -f backend

# Execute commands in backend container
docker-compose exec backend bash

# Run tests
docker-compose exec backend pytest

# Apply database migrations
docker-compose exec backend alembic upgrade head
```

#### Frontend Development
```bash
# Start frontend with hot module replacement
docker-compose -f docker-compose.dev.yml up frontend -d

# View frontend logs
docker-compose logs -f frontend

# Install new packages
docker-compose exec frontend npm install package-name

# Run frontend tests
docker-compose exec frontend npm test
```

#### Database Management
```bash
# Connect to PostgreSQL
docker-compose exec database psql -U osint_user -d osint_platform

# Create database backup
docker-compose exec database pg_dump -U osint_user osint_platform > backup.sql

# Restore database backup
docker-compose exec -T database psql -U osint_user osint_platform < backup.sql

# Reset database
docker-compose exec backend alembic downgrade base
docker-compose exec backend alembic upgrade head
```

### Development Workflow

#### Code Changes
1. **Backend Changes**: Automatically reloaded via volume mounting
2. **Frontend Changes**: Hot module replacement updates browser
3. **Database Changes**: Create new migration with Alembic
4. **Configuration Changes**: Restart affected services

#### Testing Workflow
```bash
# Run all tests
./scripts/run-tests.sh

# Run specific test suites
docker-compose exec backend pytest tests/unit/
docker-compose exec backend pytest tests/integration/
docker-compose exec frontend npm run test:unit
docker-compose exec frontend npm run test:e2e
```

## Production Deployment

### Prerequisites

#### Server Requirements
- **OS**: Ubuntu 20.04 LTS or CentOS 8
- **RAM**: Minimum 16GB, Recommended 32GB
- **Storage**: 100GB SSD storage
- **CPU**: 8+ cores for production workload
- **Network**: Public IP with domain name

#### Security Configuration
```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Configure firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Install fail2ban
sudo apt-get install fail2ban -y
```

### Docker Production Setup

#### 1. Install Docker (Production)
```bash
# Install Docker CE
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Configure Docker daemon
sudo tee /etc/docker/daemon.json <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
EOF

# Restart Docker
sudo systemctl restart docker
sudo systemctl enable docker
```

#### 2. Deploy Application
```bash
# Clone repository
git clone https://github.com/nestorwheelock/osint-AI-framework.git
cd osint-AI-framework

# Configure production environment
cp .env.production .env
nano .env  # Update with production values

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose ps
curl http://localhost/healthz
```

#### 3. SSL Configuration
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com

# Configure auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Database Production Setup

#### PostgreSQL Optimization
```sql
-- /docker-entrypoint-initdb.d/01-production-config.sql
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET work_mem = '32MB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
SELECT pg_reload_conf();
```

#### Backup Configuration
```bash
# Create backup script
sudo tee /usr/local/bin/backup-osint-db.sh <<EOF
#!/bin/bash
BACKUP_DIR="/var/backups/osint-platform"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="osint_platform"

mkdir -p $BACKUP_DIR
docker-compose exec -T database pg_dump -U osint_user $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
EOF

sudo chmod +x /usr/local/bin/backup-osint-db.sh

# Schedule backups
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-osint-db.sh
```

## Automated Installation Scripts

### Development Setup Script

```bash
#!/bin/bash
# scripts/setup-dev.sh

set -e

echo " Setting up OSINT Platform development environment..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Aborting." >&2; exit 1; }

# Create environment file
if [ ! -f .env ]; then
    echo " Creating environment file..."
    cp .env.example .env
    echo "  Please edit .env with your configuration before continuing."
    echo "   Required: OPENAI_API_KEY, SECRET_KEY"
    exit 1
fi

# Build and start services
echo "  Building Docker images..."
docker-compose -f docker-compose.dev.yml build

echo "  Starting database..."
docker-compose -f docker-compose.dev.yml up -d database redis

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
timeout 60 bash -c 'until docker-compose exec database pg_isready -U osint_user; do sleep 2; done'

# Run database migrations
echo " Running database migrations..."
docker-compose -f docker-compose.dev.yml run --rm backend alembic upgrade head

# Seed development data
echo " Seeding development data..."
docker-compose -f docker-compose.dev.yml run --rm backend python scripts/seed_dev_data.py

# Start all services
echo " Starting all services..."
docker-compose -f docker-compose.dev.yml up -d

echo " Development environment ready!"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
```

### Production Deployment Script

```bash
#!/bin/bash
# scripts/deploy-production.sh

set -e

echo " Deploying OSINT Platform to production..."

# Verify environment
if [ "$ENVIRONMENT" != "production" ]; then
    echo " This script should only run in production environment"
    exit 1
fi

# Pull latest changes
echo " Pulling latest changes..."
git pull origin main

# Build production images
echo "  Building production images..."
docker-compose -f docker-compose.prod.yml build

# Backup database
echo " Creating database backup..."
./scripts/backup-database.sh

# Update database schema
echo " Updating database schema..."
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# Deploy with rolling update
echo " Performing rolling update..."
docker-compose -f docker-compose.prod.yml up -d --remove-orphans

# Health check
echo " Performing health check..."
timeout 60 bash -c 'until curl -f http://localhost/healthz; do sleep 5; done'

# Clean up old images
echo " Cleaning up old images..."
docker image prune -f

echo " Production deployment complete!"
```

### Testing Script

```bash
#!/bin/bash
# scripts/run-tests.sh

set -e

echo " Running OSINT Platform test suite..."

# Start test dependencies
docker-compose -f docker-compose.test.yml up -d database redis

# Wait for dependencies
timeout 60 bash -c 'until docker-compose -f docker-compose.test.yml exec database pg_isready -U osint_user; do sleep 2; done'

# Run backend tests
echo " Running backend tests..."
docker-compose -f docker-compose.test.yml run --rm backend pytest --cov=app --cov-report=xml --cov-report=term-missing

# Run frontend tests
echo "  Running frontend tests..."
docker-compose -f docker-compose.test.yml run --rm frontend npm test -- --coverage --watchAll=false

# Run E2E tests
echo " Running E2E tests..."
docker-compose -f docker-compose.test.yml run --rm e2e npx playwright test

# Cleanup
docker-compose -f docker-compose.test.yml down -v

echo " All tests passed!"
```

## Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check which process is using a port
sudo lsof -i :8000

# Kill process using port
sudo kill -9 $(sudo lsof -t -i :8000)

# Use different ports in docker-compose
```

#### Database Connection Issues
```bash
# Check database container status
docker-compose ps database

# View database logs
docker-compose logs database

# Reset database
docker-compose down -v
docker-compose up -d database
```

#### Permission Issues
```bash
# Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker

# Fix file permissions
sudo chown -R $USER:$USER .
```

#### Memory Issues
```bash
# Check Docker resource usage
docker stats

# Increase Docker memory limits
# Edit Docker Desktop settings or /etc/docker/daemon.json
```

### Performance Optimization

#### Database Performance
```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM subjects WHERE created_at > NOW() - INTERVAL '1 day';

-- Create missing indexes
CREATE INDEX CONCURRENTLY idx_subjects_created_at ON subjects(created_at);

-- Update table statistics
ANALYZE subjects;
```

#### Application Performance
```bash
# Monitor container resources
docker stats

# Profile application performance
docker-compose exec backend python -m cProfile -o profile.stats app/main.py

# Optimize Docker builds
docker system prune -a
```

### Monitoring and Logging

#### Log Management
```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Search logs
docker-compose logs backend | grep ERROR

# Export logs
docker-compose logs --no-color backend > backend.log
```

#### System Monitoring
```bash
# Check system resources
htop
df -h
free -m

# Monitor Docker
docker system df
docker system events
```

## Security Considerations

### Container Security
- Use non-root users in containers
- Regularly update base images
- Scan images for vulnerabilities
- Limit container capabilities

### Network Security
- Use Docker networks for isolation
- Implement proper firewall rules
- Enable TLS for all communications
- Regular security audits

### Data Security
- Encrypt data at rest and in transit
- Implement proper backup encryption
- Use strong passwords and API keys
- Regular security assessments
