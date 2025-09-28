import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_create_subject_minimal():
    client = TestClient(app)
    res = client.post('/subjects', json={'name':'Nestor Wheelock','aliases':['N. Wheelock']})
    assert res.status_code == 201
    body = res.json()
    assert 'id' in body and body['name'] == 'Nestor Wheelock'

def test_duplicate_subject_rejected():
    client = TestClient(app)
    client.post('/subjects', json={'name':'Duplicate','aliases':[]})
    res = client.post('/subjects', json={'name':'duplicate','aliases':[]})
    assert res.status_code == 409
