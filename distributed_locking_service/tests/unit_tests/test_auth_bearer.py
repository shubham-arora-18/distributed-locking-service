import sys

sys.path.append("../../auth")
import asyncio

import fastapi
import pytest
import requests
from starlette.datastructures import Headers

from distributed_locking_service.auth.auth_bearer import JWTBearer
from distributed_locking_service.auth.auth_bearer import create_jwt_token
from distributed_locking_service.auth.auth_bearer import (
    fetch_tenant_id_from_jwt_payload,
)
from distributed_locking_service.auth.auth_bearer import get_client_id
from distributed_locking_service.exceptions import AuthException

jwt_b = JWTBearer()

url = "https://test.org/get"
method = "GET"


def test_invalid_jwt():
    invalid_headers = {
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2"
        + "lkIjoia3Jpc2huYSIsImV4cGlyZXMiOjQxMDIzNTg0MDB9."
        + "a5LBxmqo4jBFN7bAdBCLOKXDTrPPWnAH6Xu19s35W"  # pragma: allowlist secret
    }

    with pytest.raises(AuthException) as excep:
        req = requests.Request(method=method, url=url, headers=invalid_headers)
        req.prepare()
        asyncio.run(jwt_b(req))

    assert excep.value.detail == jwt_b.invalid_or_expired_token_message


# ideally this should be removed, as the parent class is already checking for bearer.
# And our code checks for letter casing for bearer as well. Which ideally we should not.
# Currently leaving this to prevent from breaking dependent libraries test cases.
def test_invalid_jwt_scheme():
    invalid_headers = {
        "Authorization": "bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2"
        + "lkIjoia3Jpc2huYSIsImV4cGlyZXMiOjQxMDIzNTg0MDB9."
        + "a5LBxmqo4jBFN7bAdBCLOKXDTrPPWnAH6Xu19s35W"  # pragma: allowlist secret
    }

    with pytest.raises(AuthException) as excep:
        req = requests.Request(method=method, url=url, headers=invalid_headers)
        req.prepare()
        asyncio.run(jwt_b(req))

    assert excep.value.detail == jwt_b.invalid_auth_scheme_message


def test_no_jwt_provided():
    invalid_headers = {"Authorization": ""}

    with pytest.raises(AuthException) as excep:
        req = requests.Request(method=method, url=url, headers=invalid_headers)
        req.prepare()
        asyncio.run(jwt_b(req))

    assert excep.value.detail == jwt_b.no_auth_code_provided_message


@pytest.fixture
def sample_fastapi_request():
    jwt_token = create_jwt_token("ABC")
    valid_headers = {"Authorization": "Bearer " + jwt_token, "x-partner-id": "ABC"}
    req = fastapi.Request(
        {
            "type": "http",
            "headers": Headers(valid_headers).raw,
        }
    )
    asyncio.run(JWTBearer().__call__(req))
    return req


def test_jwt_payload_extration_successful(sample_fastapi_request):
    assert fetch_tenant_id_from_jwt_payload(sample_fastapi_request) == "ABC"


def test_for_universal_access_get_client_id_returns_clientid():
    client_access_granted = ["PARTNER.ALL"]
    client_access_requested = "abc"
    assert get_client_id(client_access_requested, client_access_granted) == "ABC"


def test_for_requested_access_get_client_id_returns_clientid():
    client_access_granted = ["PARTNER.ID.ABC"]
    client_access_requested = "abc"
    assert get_client_id(client_access_requested, client_access_granted) == "ABC"


def test_get_client_id_throws_auth_error():
    with pytest.raises(AuthException) as excep:
        client_access_granted = ["PARTNER.ID.ABC"]
        client_access_requested = "efg"
        get_client_id(client_access_requested, client_access_granted)

    assert excep.value.status_code == 401
