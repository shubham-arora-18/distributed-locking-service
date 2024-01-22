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
    valid_headers,
)

client = TestClient(app)

# import os
#
# os.environ["CLOUDSDK_CORE_PROJECT"] = "test"
# os.environ["DATASTORE_EMULATOR_HOST"] = "localhost:8081"


created_exclusive_write_distributed_lock_ref = created_exclusive_write_distributed_lock
parameters = {"timeout": 70}


def get_random_process_id() -> str:
    return f"process_id_{str(uuid4())}"


@pytest.fixture
def add_read_process(created_exclusive_write_distributed_lock_ref):
    rand_lock_id = created_exclusive_write_distributed_lock_ref["lock_id"]
    rand_process_id = get_random_process_id()
    response = client.put(
        f"/v1/distributed_lock/{rand_lock_id}/read-process/{rand_process_id}",
        headers=valid_headers,
        params=parameters,
    )
    assert response.status_code == 200
    assert any(
        rp.get("process_id") == rand_process_id for rp in response.json().get("read_process_list")
    )
    assert response.json()["current_state"] == "READ"

    yield response.json()


def test_invalid_addition_of_already_added_read_process(add_read_process):
    rand_lock_id = add_read_process["lock_id"]
    rand_process_id = add_read_process["read_process_list"][0]["process_id"]
    response = client.put(
        f"/v1/distributed_lock/{rand_lock_id}/read-process/{rand_process_id}",
        headers=valid_headers,
        params=parameters,
    )
    assert response.status_code == 406
    assert f"Process id {rand_process_id} already present in the lock" in str(response.json())


def test_refresh_read_process(add_read_process):
    rand_lock_id = add_read_process["lock_id"]
    rand_process_id = add_read_process["read_process_list"][0]["process_id"]
    response = client.put(
        f"/v1/distributed_lock/{rand_lock_id}/read-process/{rand_process_id}/refresh",
        headers=valid_headers,
        params=parameters,
    )
    assert response.status_code == 200
    assert len(response.json().get("read_process_list")) == 1
    assert rand_process_id == response.json().get("read_process_list")[0]["process_id"]


def test_invalid_addition_of_write_process_to_read_lock(add_read_process):
    rand_lock_id = add_read_process["lock_id"]
    rand_process_id = get_random_process_id()
    response = client.put(
        f"/v1/distributed_lock/{rand_lock_id}/write-process/{rand_process_id}",
        headers=valid_headers,
        params=parameters,
    )

    assert response.status_code == 409
    assert (
        f"The lock with lock_id:{rand_lock_id} is currently in READ state. "
        f"Please wait for the lock to return to FREE or READ state." in str(response.json())
    )


def test_invalid_deletion_of_write_process_from_read_lock(add_read_process):
    rand_lock_id = add_read_process["lock_id"]
    rand_process_id = get_random_process_id()
    response = client.delete(
        f"/v1/distributed_lock/{rand_lock_id}/write-process/{rand_process_id}",
        headers=valid_headers,
    )

    assert response.status_code == 400
    assert "The lock is currently in READ state" in str(response.json())


@pytest.fixture
def add_second_read_process(add_read_process):
    rand_lock_id = add_read_process["lock_id"]
    rand_process_id = get_random_process_id()
    response = client.put(
        f"/v1/distributed_lock/{rand_lock_id}/read-process/{rand_process_id}",
        headers=valid_headers,
        params=parameters,
    )
    assert response.status_code == 200
    assert any(
        rp.get("process_id") == rand_process_id for rp in response.json().get("read_process_list")
    )
    assert len(response.json()["read_process_list"]) == 2
    assert response.json()["current_state"] == "READ"

    yield response.json()


def test_delete_invalid_read_process(add_second_read_process):
    rand_lock_id = add_second_read_process["lock_id"]
    rand_process_id = get_random_process_id()
    response = client.delete(
        f"/v1/distributed_lock/{rand_lock_id}/read-process/{rand_process_id}",
        headers=valid_headers,
    )

    assert response.status_code == 400
    assert "The process is not present in lock" in str(response.json())


@pytest.fixture
def delete_first_read_process(add_second_read_process):
    rand_lock_id = add_second_read_process["lock_id"]
    rand_process_id = add_second_read_process["read_process_list"][0]["process_id"]
    response = client.delete(
        f"/v1/distributed_lock/{rand_lock_id}/read-process/{rand_process_id}",
        headers=valid_headers,
    )
    assert response.status_code == 200
    assert len(response.json()["read_process_list"]) == 1
    assert not any(
        rp.get("process_id") == rand_process_id for rp in response.json().get("read_process_list")
    )
    assert "READ" == response.json()["current_state"]

    yield response.json()


@pytest.fixture
def delete_second_read_process(delete_first_read_process):
    rand_lock_id = delete_first_read_process["lock_id"]
    rand_process_id = delete_first_read_process["read_process_list"][0]["process_id"]
    response = client.delete(
        f"/v1/distributed_lock/{rand_lock_id}/read-process/{rand_process_id}",
        headers=valid_headers,
    )
    assert response.status_code == 200
    assert len(response.json()["read_process_list"]) == 0
    assert "FREE" == response.json()["current_state"]

    yield response.json()


def test_invalid_delete_read_process_from_free_lock(delete_second_read_process):
    rand_lock_id = delete_second_read_process["lock_id"]
    rand_process_id = get_random_process_id()
    response = client.delete(
        f"/v1/distributed_lock/{rand_lock_id}/read-process/{rand_process_id}",
        headers=valid_headers,
    )
    assert response.status_code == 400
    assert "The lock is already in FREE state." in str(response.json())


#   testing if a lock contains 2 read process and one of them is timed out, when you get the lock,
#   the timed out process is automatically removed and the lock is refreshed.
@mock.patch("distributed_locking_service.services.distributed_lock.Process")
def test_valid_add_and_get_timed_out_lock(mock_process, add_read_process):
    rand_process_id = get_random_process_id()
    past_time = datetime.now(timezone.utc) - timedelta(seconds=10)
    # the process below is a timed out process by 8 secs(10-2)
    expired_process = Process(process_id=rand_process_id, lock_acquired_at=past_time, timeout=2)
    mock_process.return_value = expired_process
    rand_lock_id = add_read_process["lock_id"]

    client.put(
        f"/v1/distributed_lock/{rand_lock_id}/read-process/{rand_process_id}",
        headers=valid_headers,
        params=parameters,
    )

    response = client.get(f"/v1/distributed_lock/{rand_lock_id}", headers=valid_headers)

    assert response.status_code == 200
    assert "READ" == response.json()["current_state"]
    assert len(response.json()["read_process_list"]) == 1
    assert not any(
        rp.get("process_id") == rand_process_id for rp in response.json().get("read_process_list")
    )


@mock.patch("distributed_locking_service.services.distributed_lock.Process")
def test_valid_add_and_get_lock(mock_process, add_read_process):
    rand_process_id = get_random_process_id()
    past_time = datetime.now(timezone.utc) - timedelta(seconds=10)
    # the process below is a live process with 90 secs remaining to live(100-10)
    live_process = Process(process_id=rand_process_id, lock_acquired_at=past_time, timeout=100)
    mock_process.return_value = live_process
    rand_lock_id = add_read_process["lock_id"]

    client.put(
        f"/v1/distributed_lock/{rand_lock_id}/read-process/{rand_process_id}",
        headers=valid_headers,
        params=parameters,
    )

    response = client.get(f"/v1/distributed_lock/{rand_lock_id}", headers=valid_headers)

    assert response.status_code == 200
    assert "READ" == response.json()["current_state"]
    assert len(response.json()["read_process_list"]) == 2
    assert any(
        rp.get("process_id") == rand_process_id for rp in response.json().get("read_process_list")
    )


@mock.patch("distributed_locking_service.services.distributed_lock.Process")
def test_valid_auto_deletion_of_single_timed_out_process_changes_lock_state_to_free(
    mock_process, created_exclusive_write_distributed_lock
):
    rand_process_id = get_random_process_id()
    past_time = datetime.now(timezone.utc) - timedelta(seconds=10)
    # the process below is a timed out process by 8 secs(10-2)
    expired_process = Process(process_id=rand_process_id, lock_acquired_at=past_time, timeout=2)
    mock_process.return_value = expired_process
    rand_lock_id = created_exclusive_write_distributed_lock["lock_id"]

    client.put(
        f"/v1/distributed_lock/{rand_lock_id}/read-process/{rand_process_id}",
        headers=valid_headers,
        params=parameters,
    )

    response = client.get(f"/v1/distributed_lock/{rand_lock_id}", headers=valid_headers)
    assert "FREE" == response.json()["current_state"]
    assert len(response.json()["read_process_list"]) == 0


# the second put call would overwrite the first expired put call
def test_exclusive_lock_with_two_put_calls(created_exclusive_write_distributed_lock):
    rand_lock_id = created_exclusive_write_distributed_lock["lock_id"]

    with mock.patch(
        "distributed_locking_service.services.distributed_lock.Process"
    ) as mock_process:
        rand_process_id = get_random_process_id()
        past_time = datetime.now(timezone.utc) - timedelta(seconds=10)
        # the process below is a timed out process by 8 secs(10-2)
        expired_process = Process(process_id=rand_process_id, lock_acquired_at=past_time, timeout=2)
        mock_process.return_value = expired_process

        response = client.put(
            f"/v1/distributed_lock/{rand_lock_id}/read-process/{rand_process_id}",
            headers=valid_headers,
            params=parameters,
        )
        assert response.status_code == 200
        assert "READ" == response.json()["current_state"]
        assert len(response.json()["read_process_list"]) == 1
        assert any(
            rp.get("process_id") == rand_process_id
            for rp in response.json().get("read_process_list")
        )

    rand_process_id_2 = get_random_process_id()
    response_2 = client.put(
        f"/v1/distributed_lock/{rand_lock_id}/write-process/{rand_process_id_2}",
        headers=valid_headers,
        params=parameters,
    )
    assert response.status_code == 200
    assert "WRITE" == response_2.json()["current_state"]
    assert len(response_2.json()["write_process_list"]) == 1
    assert any(
        rp.get("process_id") == rand_process_id_2
        for rp in response_2.json().get("write_process_list")
    )
