from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from distributed_locking_service.main import app

client = TestClient(app)

# import os
#
# os.environ["CLOUDSDK_CORE_PROJECT"] = "test"
# os.environ["DATASTORE_EMULATOR_HOST"] = "localhost:8081"

valid_headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1ZXIiOiJJc3N1ZXIiL"
    "CJJc3N1ZWQgQXQiOiIyMDI1LTAzLTEwVDA5OjMyOjAyLjkxNFoiLCJleHBpcmVzIjoxNz"
    "M2NDY5MTIyLCJwYXJ0bmVyX2FjY2VzcyI6WyJQQVJUTkVSLklELlNIVUJIQU0iXSwidGVu"
    "YW50X2lkIjoic2h1YmhhbSIsIlJvbGUiOiJBZG1pbiJ9.JBFt15ksk6J8klYTJkelfMYov"
    "FYCs8AvHVjirrPEtiM",  # pragma: allowlist secret
    "x-partner-id": "SHUBHAM",
}


def get_random_lock_id() -> str:
    return f"random_id_{str(uuid4())}"


def test_health_check():
    response = client.get("/v1/healthcheck")
    assert "healthy" in str(response.json())
    assert response.status_code == 200


def test_invalid_route_post_request():
    # params = {
    #     "app": "sku_foreca",
    #     "commit_id": "123",
    #     "docker_url": "test-docker-url.com",  # incorrect url
    # }
    response = client.post("/v1/distributed_lock/", headers=valid_headers)

    assert response.status_code == 404
    assert "Not Found" in str(response.json())


@pytest.fixture
def created_exclusive_write_distributed_lock():
    rand_lock_id = get_random_lock_id()
    params = {"is_write_exclusive": True}
    response_post = client.post(
        f"/v1/distributed_lock/{rand_lock_id}", headers=valid_headers, params=params
    )
    assert response_post.status_code == 201
    assert response_post.json()["current_state"] == "FREE"
    assert rand_lock_id == str(response_post.json()["lock_id"])
    yield response_post.json()


def test_valid_lock_id_get_call(created_exclusive_write_distributed_lock):
    rand_lock_id = created_exclusive_write_distributed_lock["lock_id"]
    insert_id = created_exclusive_write_distributed_lock["id"]
    response_get = client.get(f"/v1/distributed_lock/{rand_lock_id}", headers=valid_headers)
    assert response_get.status_code == 200
    assert rand_lock_id == str(response_get.json()["lock_id"])
    assert True is response_get.json()["is_write_exclusive"]
    assert insert_id == str(response_get.json()["id"])


def test_invalid_lock_id_get_call():
    rand_lock_id = get_random_lock_id()
    response_get = client.get(f"/v1/distributed_lock/{rand_lock_id}", headers=valid_headers)
    assert response_get.status_code == 404
    assert f"DistributedLock with lock_id: {rand_lock_id} not found" in str(response_get.json())


def test_invalid_post_api_with_repeated_lock_id(created_exclusive_write_distributed_lock):
    rand_lock_id = created_exclusive_write_distributed_lock["lock_id"]
    response_post = client.post(f"/v1/distributed_lock/{rand_lock_id}", headers=valid_headers)
    assert response_post.status_code == 400
    assert f"Different Lock with id:{rand_lock_id} already exists." in str(response_post.json())
