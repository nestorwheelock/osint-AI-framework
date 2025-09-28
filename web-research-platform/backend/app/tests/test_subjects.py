from httpx import AsyncClient
import pytest
from app.main import app

@pytest.mark.asyncio
async def test_create_subject_minimal():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        res = await ac.post('/subjects', json={'name':'Nestor Wheelock','aliases':['N. Wheelock']})
        assert res.status_code == 201
        body = res.json()
        assert 'id' in body and body['name'] == 'Nestor Wheelock'

@pytest.mark.asyncio
async def test_duplicate_subject_rejected():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        await ac.post('/subjects', json={'name':'Duplicate','aliases':[]})
        res = await ac.post('/subjects', json={'name':'duplicate','aliases':[]})
        assert res.status_code == 409
