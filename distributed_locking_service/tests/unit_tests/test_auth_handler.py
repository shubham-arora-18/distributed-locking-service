from distributed_locking_service.auth.auth_handler import decode_jwt

jwt_token = (
    "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoia3Jpc2huYSIsImV4cCI6MTY3Mzg1ODEzNX0"
    ".gBrsAN5EHdnikCY-tEEtauqE02WFRq8oby5Iqm1JDC0"
)


def test_decode_jwt_exception():
    expired_token = (
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoia3Jpc2huYSIsImV4cCI6MTY3Mzg1ODEzNX0"
        ".gBrsAN5EHdnikCY-tEEtauqE02WFRq8oby5Iqm1JDC0"
    )

    assert decode_jwt(expired_token) is None


def test_decode_jwt_invalid_jwt():
    expired_token = (
        ".eyJ1c2VyX2lkIjoia3Jpc2huYSIsImV4cCI6MTY3Mzg1ODEzNX0"
        ".gBrsAN5EHdnikCY-tEEtauqE02WFRq8oby5Iqm1JDC0"
    )

    assert decode_jwt(expired_token) is None

    # with pytest.raises(ValueError)


def test_decode_jwt_invalid_jwt():
    expired_token = (
        "eyJ0eXAiOiIiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoia3Jpc2huYSIsImV4cCI6NDEwMjM1ODQwMH0"
        ".R0a86OeLQlju-Ju6t2zlGiqmAybNLWIbpAJTN_9A8n8"
    )

    assert not decode_jwt(expired_token) is None
