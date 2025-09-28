# Web Research Platform (Starter)

A TDD-friendly scaffold for a web scraping + AI analysis platform.

## Stack
- **Backend:** FastAPI + pytest
- **Workers:** Celery + Redis (placeholders)
- **DB:** Postgres (psycopg placeholder)
- **E2E:** Playwright (Node) for UI & flow tests
- **CI:** GitHub Actions runs pytest and Playwright

> Start by pushing this repo to GitHub, then open issues using the included templates.


## Quick start

```bash
# Backend (dev)
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .[dev]
uvicorn app.main:app --reload

# Run tests
pytest -q

# Frontend E2E (requires Node 18+)
cd ../frontend
npm install
npx playwright install
npx playwright test
```
