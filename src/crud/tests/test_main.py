from fastapi.testclient import TestClient

from  crud.main import app

client = TestClient(app)

def test_all_notes():
    response = client.get('/notes')
    assert response.status_code == 200
    assert isinstance(response.json(), list)