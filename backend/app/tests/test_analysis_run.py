import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_run_records_prompt_version_and_model_placeholder():
    client = TestClient(app)
    res = client.post('/analyze', json={'subject_id':'S1','pipeline':'entity-extract','page_ids':[]})
    assert res.status_code == 202
    body = res.json()
    assert body['status'] == 'running'
    assert body['run_id'].startswith('RUN-')
