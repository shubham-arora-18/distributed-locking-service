from datetime import datetime
from datetime import timedelta
from datetime import timezone
from unittest import mock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from distributed_locking_service.main import app
from distributed_locking_service.models.process import Process
from distributed_locking_service.tests.integration_tests.test_distributed_lock_creation import (
    created_exclusive_write_distributed_lock,
)
from distributed_locking_service.tests.integration_tests.test_distributed_lock_creation import (
    get_random_lock_id,
)
from distributed_locking_service.tests.integration_tests.test_distributed_lock_creation import (
    valid_headers,
)

client = TestClient(app)

# import os
#
# os.environ["CLOUDSDK_CORE_PROJECT"] = "test"
# os.environ["DATASTORE_EMULATOR_HOST"] = "localhost:8081"

# ref added as otherwise the import is considered as unused import by the
created_exclusive_write_distributed_lock_ref = created_exclusive_write_distributed_lock
parameters = {"timeout": 70}


def get_random_process_id() -> str:
    return f"process_id_{str(uuid4())}"


@pytest.fixture
def created_distributed_lock():
    rand_lock_id = get_random_lock_id()
    params = {"is_write_exclusive": False}
    response_post = client.post(
        f"/v1/distributed_lock/{rand_lock_id}", headers=valid_headers, params=params
    )
    assert response_post.status_code == 201
    assert response_post.json()["current_state"] == "FREE"
    assert rand_lock_id == str(response_post.json()["lock_id"])
    yield response_post.json()


@pytest.fixture
def add_write_process(created_distributed_lock):
    rand_lock_id = created_distributed_lock["lock_id"]
    rand_process_id = get_random_process_id()
    response = client.put(
        f"/v1/distributed_lock/{rand_lock_id}/write-process/{rand_process_id}",
        headers=valid_headers,
        params=parameters,
    )
    assert response.status_code == 200
    assert any(
        wp.get("process_id") == rand_process_id for wp in response.json().get("write_process_list")
    )
    assert response.json()["current_state"] == "WRITE"

    yield response.json()


def test_invalid_addition_of_already_added_read_process(add_write_process):
    rand_lock_id = add_write_process["lock_id"]
    rand_process_id = add_write_process["write_process_list"][0]["process_id"]
    response = client.put(
        f"/v1/distributed_lock/{rand_lock_id}/write-process/{rand_process_id}",
        headers=valid_headers,
        params=parameters,
    )
    assert response.status_code == 400
    assert "Process id already present in the lock" in str(response.json())


def test_invalid_addition_of_read_process_to_write_lock(add_write_process):
    rand_lock_id = add_write_process["lock_id"]
    rand_process_id = get_random_process_id()
    response = client.put(
        f"/v1/distributed_lock/{rand_lock_id}/read-process/{rand_process_id}",
        headers=valid_headers,
        params=parameters,
    )

    assert response.status_code == 409
    assert (
        f"The lock with lock_id:{rand_lock_id} is currently in WRITE state. "
        f"Please wait for the lock to return to FREE or READ state." in str(response.json())
    )


def test_invalid_deletion_of_read_process_from_write_lock(add_write_process):
    rand_lock_id = add_write_process["lock_id"]
    rand_process_id = get_random_process_id()
    response = client.delete(
        f"/v1/distributed_lock/{rand_lock_id}/read-process/{rand_process_id}",
        headers=valid_headers,
    )

    assert response.status_code == 400
    assert "The lock is currently in WRITE state" in str(response.json())


@pytest.fixture
def add_second_write_process(add_write_process):
    rand_lock_id = add_write_process["lock_id"]
    rand_process_id = get_random_process_id()
    response = client.put(
        f"/v1/distributed_lock/{rand_lock_id}/write-process/{rand_process_id}",
        headers=valid_headers,
        params=parameters,
    )
    assert response.status_code == 200
    assert any(
        wp.get("process_id") == rand_process_id for wp in response.json().get("write_process_list")
    )
    assert len(response.json()["write_process_list"]) == 2
    assert response.json()["current_state"] == "WRITE"

    yield response.json()


def test_delete_invalid_write_process(add_second_write_process):
    rand_lock_id = add_second_write_process["lock_id"]
    rand_process_id = get_random_process_id()
    response = client.delete(
        f"/v1/distributed_lock/{rand_lock_id}/write-process/{rand_process_id}",
        headers=valid_headers,
    )

    assert response.status_code == 400
    assert "The process is not present in lock" in str(response.json())


@pytest.fixture
def delete_first_write_process(add_second_write_process):
    rand_lock_id = add_second_write_process["lock_id"]
    rand_process_id = add_second_write_process["write_process_list"][0]["process_id"]
    response = client.delete(
        f"/v1/distributed_lock/{rand_lock_id}/write-process/{rand_process_id}",
        headers=valid_headers,
    )
    assert response.status_code == 200
    assert len(response.json()["write_process_list"]) == 1
    assert not any(
        wp.get("process_id") == rand_process_id for wp in response.json().get("write_process_list")
    )
    assert "WRITE" == response.json()["current_state"]

    yield response.json()


@pytest.fixture
def delete_second_write_process(delete_first_write_process):
    rand_lock_id = delete_first_write_process["lock_id"]
    rand_process_id = delete_first_write_process["write_process_list"][0]["process_id"]
    response = client.delete(
        f"/v1/distributed_lock/{rand_lock_id}/write-process/{rand_process_id}",
        headers=valid_headers,
    )
    assert response.status_code == 200
    assert len(response.json()["write_process_list"]) == 0
    assert "FREE" == response.json()["current_state"]

    yield response.json()


def test_invalid_delete_write_process_from_free_lock(delete_second_write_process):
    rand_lock_id = delete_second_write_process["lock_id"]
    rand_process_id = get_random_process_id()
    response = client.delete(
        f"/v1/distributed_lock/{rand_lock_id}/write-process/{rand_process_id}",
        headers=valid_headers,
    )
    assert response.status_code == 400
    assert "The lock is already in FREE state." in str(response.json())


def test_invalid_second_write_process_addition_to_write_exclusive_lock(
    created_exclusive_write_distributed_lock_ref,
):
    rand_lock_id = created_exclusive_write_distributed_lock_ref["lock_id"]
    rand_process_id = get_random_process_id()
    client.put(
        f"/v1/distributed_lock/{rand_lock_id}/write-process/{rand_process_id}",
        headers=valid_headers,
        params=parameters,
    )

    rand_process_id = get_random_process_id()
    response_2 = client.put(
        f"/v1/distributed_lock/{rand_lock_id}/write-process/{rand_process_id}",
        headers=valid_headers,
        params=parameters,
    )

    assert response_2.status_code == 409
    assert "The lock is write exclusive. It can only hold one write process at a time." in str(
        response_2.json()
    )


#   testing if a lock contains 2 write process and one of them is timed out, when you get the lock,
#   the timed out process is automatically removed and the lock is refreshed.
@mock.patch("distributed_locking_service.services.distributed_lock.Process")
def test_valid_add_and_get_timed_out_lock(mock_process, add_write_process):
    rand_process_id = get_random_process_id()
    past_time = datetime.now(timezone.utc) - timedelta(seconds=10)
    # the process below is a timed out process by 8 secs(10-2)
    expired_process = Process(process_id="test_process_id", lock_acquired_at=past_time, timeout=2)
    mock_process.return_value = expired_process
    rand_lock_id = add_write_process["lock_id"]

    client.put(
        f"/v1/distributed_lock/{rand_lock_id}/write-process/{rand_process_id}",
        headers=valid_headers,
        params=parameters,
    )

    response = client.get(f"/v1/distributed_lock/{rand_lock_id}", headers=valid_headers)

    assert "WRITE" == response.json()["current_state"]
    assert len(response.json()["write_process_list"]) == 1
    assert not any(
        rp.get("process_id") == "test_process_id"
        for rp in response.json().get("write_process_list")
    )


@mock.patch("distributed_locking_service.services.distributed_lock.Process")
def test_invalid_add_and_get_timed_out_lock(mock_process, add_write_process):
    rand_process_id = get_random_process_id()
    past_time = datetime.now(timezone.utc) - timedelta(seconds=10)
    # the process below is a live process with 90 secs remaining to live(100-10)
    expired_process = Process(process_id="test_process_id", lock_acquired_at=past_time, timeout=100)
    mock_process.return_value = expired_process
    rand_lock_id = add_write_process["lock_id"]

    client.put(
        f"/v1/distributed_lock/{rand_lock_id}/write-process/{rand_process_id}",
        headers=valid_headers,
        params=parameters,
    )

    response = client.get(f"/v1/distributed_lock/{rand_lock_id}", headers=valid_headers)

    assert "WRITE" == response.json()["current_state"]
    assert len(response.json()["write_process_list"]) == 2
    assert any(
        rp.get("process_id") == "test_process_id"
        for rp in response.json().get("write_process_list")
    )


@mock.patch("distributed_locking_service.services.distributed_lock.Process")
def test_valid_auto_deletion_of_single_timed_out_process_changes_lock_state_to_free(
    mock_process, created_exclusive_write_distributed_lock
):
    rand_process_id = get_random_process_id()
    past_time = datetime.now(timezone.utc) - timedelta(seconds=10)
    # the process below is a timed out process by 8 secs(10-2)
    expired_process = Process(process_id="test_process_id", lock_acquired_at=past_time, timeout=2)
    mock_process.return_value = expired_process
    rand_lock_id = created_exclusive_write_distributed_lock["lock_id"]

    client.put(
        f"/v1/distributed_lock/{rand_lock_id}/write-process/{rand_process_id}",
        headers=valid_headers,
        params=parameters,
    )

    response = client.get(f"/v1/distributed_lock/{rand_lock_id}", headers=valid_headers)
    assert "FREE" == response.json()["current_state"]
    assert len(response.json()["write_process_list"]) == 0
