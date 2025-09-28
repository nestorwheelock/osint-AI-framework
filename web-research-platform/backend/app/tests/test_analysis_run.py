from httpx import AsyncClient
import pytest
from app.main import app

@pytest.mark.asyncio
async def test_run_records_prompt_version_and_model_placeholder():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        res = await ac.post('/analyze', json={'subject_id':'S1','pipeline':'entity-extract','page_ids':[]})
        assert res.status_code == 202
        body = res.json()
        assert body['status'] == 'running'
        assert body['run_id'].startswith('RUN-')
