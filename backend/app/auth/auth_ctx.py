import os
import time
from flask import request, session, g
from werkzeug.exceptions import Unauthorized
import jwt
from jwt import PyJWKClient
from .sync_user import sync_user


KC_URL = os.getenv('KC_URL', 'http://keycloak:8080')
KC_REALM = os.getenv('KC_REALM', 'muzo-realm')
jwks_client = PyJWKClient(f"{KC_URL}/realms/{KC_REALM}/protocol/openid-connect/certs")

KC_PUBLIC_URL = os.getenv('KC_PUBLIC_URL', 'http://localhost:5002')
ISSUER_URL = f"{KC_PUBLIC_URL}/realms/{KC_REALM}"


def get_auth_ctx():
    """ Get user details from session or auth token """

    if getattr(g, 'auth_ctx', None) is not None:
        return g.auth_ctx
    
    if "user_id" in session and "roles" in session:
        g.auth_ctx = _get_ctx_from_session()
    else:
        g.auth_ctx = _get_ctx_from_token()
    return g.auth_ctx


def _get_ctx_from_session():
    # check expiry
    exp = session.get("exp")
    if not exp or time.time() > exp:
        session.clear()
        raise Unauthorized("Not authenticated")

    return {
        "user_id": session.get("user_id"),
        "roles": session.get("roles"),
    }


def _get_ctx_from_token():
    # get auth header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        # extract and decode token
        token = auth_header.split(" ", 1)[1].strip()
        try:
            decoded_token = _decode_token(token)
        except Exception:
            raise Unauthorized("invalid token")
        
        user = sync_user(decoded_token)

        user_roles = decoded_token.get("realm_access", {}).get("roles", [])
        return {
            "user_id": user.id,
            "roles": {
                "ROLE_ARTIST": "ROLE_ARTIST" in user_roles,
                "ROLE_ADMIN": "ROLE_ADMIN" in user_roles
            }
        }
    raise Unauthorized("missing authorization")
            

def _decode_token(token):
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False},
            issuer=ISSUER_URL
        )


def get_user_id():
    """ Get current user id """
    return get_auth_ctx()["user_id"]

def get_user_roles():
    """ Get current user roles """
    return get_auth_ctx()["roles"]
