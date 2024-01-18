"""
Utility Module for checking auth header
"""
import json
import logging
import time

import jwt
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from distributed_locking_service.auth.auth_handler import decode_jwt
from distributed_locking_service.exceptions import AuthException

logger = logging.getLogger(__name__)

CLIENT_ID = "x-partner-id"
UNIVERSAL_ACCESS = "PARTNER.ALL"
CLIENT_ID_PREFIX = "PARTNER.ID."
PARTNER_ACCESS = "partner_access"
DEFAULT_CLIENT_ID = ""


class JWTBearer(HTTPBearer):
    """
    Utility class for checking auth header

    """

    invalid_auth_scheme_message = "Invalid authentication scheme."
    invalid_or_expired_token_message = "Invalid token or expired token."
    no_auth_code_provided_message = "No Authorization code provided"

    def __init__(self, auto_error: bool = False):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)  # type: ignore
        if credentials:
            if not credentials.scheme == "Bearer":
                raise AuthException(status_code=401, detail=self.invalid_auth_scheme_message)
            valid_jwt_token, payload = JWTBearer.verify_jwt(credentials.credentials)
            if not valid_jwt_token:
                raise AuthException(status_code=401, detail=self.invalid_or_expired_token_message)
            request.state.jwt_payload = payload
            return credentials.credentials

        raise AuthException(status_code=401, detail=self.no_auth_code_provided_message)

    @staticmethod
    def verify_jwt(jwtoken: str):
        """
        function to check valid token
        :param jwtoken:
        :return:
        """
        is_token_valid: bool = False

        try:
            payload = decode_jwt(jwtoken)
        except ValueError:
            payload = None
        if payload:
            is_token_valid = True
        return is_token_valid, payload
        # if jwtoken:
        #     is_token_valid = True
        # return is_token_valid


def create_jwt_token(client_id: str):
    # define the payload of the token
    if client_id.upper() == "ALL":
        partner_id_access = UNIVERSAL_ACCESS
    else:
        partner_id_access = CLIENT_ID_PREFIX + client_id.upper()

    payload = {
        "tenant_id": "random_id",
        PARTNER_ACCESS: [partner_id_access],
        "expires": time.time() + 8 * 60 * 60,  # validity for 8 hours
    }
    # define the secret key for signing the token
    secret_key = "my_secret_key"

    # create the JWT token
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


def fetch_tenant_id_from_jwt_payload(
    request: Request, log_input_request: bool = True, optional_request_log: str = "No Optional Log"
):

    log_request(request, log_input_request, optional_request_log)
    if not hasattr(request.state, "jwt_payload"):
        raise Exception("Jwt payload not present in the request")
    else:
        if request.state.jwt_payload.get(PARTNER_ACCESS) is None:
            # raise Exception("Tenant Id not present in jwt payload")
            client_id = DEFAULT_CLIENT_ID  # returning default client id if not present for backwards compatibility
            logger.info("Returning default tenant id")
        else:
            if request.headers.get(CLIENT_ID) is None:
                raise AuthException(f"Please add the x-partner-id header.", 401)
            client_access_requested = request.headers.get(CLIENT_ID)
            client_access_granted = request.state.jwt_payload.get(PARTNER_ACCESS)
            client_id = get_client_id(client_access_requested, client_access_granted)  # type: ignore

        logger.info(f"Client id = {client_id}")
        return client_id


def get_client_id(client_access_requested: str, client_access_granted):
    if UNIVERSAL_ACCESS in client_access_granted:
        return client_access_requested.upper()

    client_access_requested_constant = CLIENT_ID_PREFIX + client_access_requested.upper()
    if client_access_requested_constant in client_access_granted:
        return client_access_requested.upper()

    raise AuthException(f"You are unauthorized to access client: {client_access_requested}", 401)


def log_request(request: Request, log_input_request, optional_request_log):
    if log_input_request is False:
        logger.info(f"Request Voluntarily Not Logged. Optional Log: {optional_request_log}")
        return

    dict = request.scope
    log_dict = {}
    for key in dict:
        log_dict[key] = str(dict[key])
    json_data = json.dumps(log_dict)
    logging.info(f" Input Http Request:{json_data}")
