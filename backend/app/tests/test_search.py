import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_meta_search_collapses_duplicates():
    client = TestClient(app)
    res = client.post('/search', json={'subject_id':'S1','query':'test','engines':['google','ddg']})
    assert res.status_code == 200
    items = res.json()
    # Should return exactly one item because duplicates collapse
    assert len(items) == 1
    assert items[0]['canonical_url'].startswith('https://example.com/post')
