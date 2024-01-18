"""
Module for authentication handling
"""
import logging
import time
from typing import Optional

import jwt

# secret=please_please_update_me_please
# algorithm=HS256
#
# JWT_SECRET = config("secret")
# JWT_ALGORITHM = config("algorithm")
logger = logging.getLogger(__name__)


def token_response(token: str):
    """
    function to return token
    :param token:
    :return:
    """
    return {"access_token": token}


# def signJWT(user_id: str) -> Dict[str, str]:
#     payload = {"user_id": user_id, "expires": time.time() + 6000}
#     token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
#
#     return token_response(token)


def decode_jwt(token: str) -> Optional[dict]:
    """
    function to decode jwt token
    :param token:
    :return:
    """
    try:
        # decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        if decoded_token.get("expires", time.time()) > time.time():
            return decoded_token
        if decoded_token.get("exp", time.time()) > time.time():
            return decoded_token
        return None
        # return decoded_token if decoded_token["expires"] >= time.time() else None
    except (jwt.DecodeError,):
        return None
    except ValueError:
        return {}
