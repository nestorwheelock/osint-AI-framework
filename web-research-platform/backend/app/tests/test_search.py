from httpx import AsyncClient
import pytest
from app.main import app

@pytest.mark.asyncio
async def test_meta_search_collapses_duplicates():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        res = await ac.post('/search', json={'subject_id':'S1','query':'test','engines':['google','ddg']})
        assert res.status_code == 200
        items = res.json()
        # Should return exactly one item because duplicates collapse
        assert len(items) == 1
        assert items[0]['canonical_url'].startswith('https://example.com/post')
