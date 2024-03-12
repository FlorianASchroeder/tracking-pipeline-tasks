import pytest
from fastapi.testclient import TestClient
from main import app

from firehose_tracker.tracker import SingletonMeta, Tracker

client = TestClient(app)


@pytest.fixture
def mocked_tracker(mocker):
    mocker.patch.dict(SingletonMeta._instances, (), clear=True)
    mocker.patch.object(Tracker, "put_record", return_value=None)
    # mocker.patch.object(Tracker, "ensure_active", return_value=None)


def test_track(mocked_tracker):
    data = {"event_type": "page_view", "data": "test_data"}
    response = client.post("/track", json=data)
    assert response.status_code == 200
    assert response.json() == {"message": "success"}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "Healthy"}
