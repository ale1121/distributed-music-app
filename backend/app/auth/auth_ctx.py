import os
import time
from flask import request, session, g
from werkzeug.exceptions import Unauthorized
import jwt
from jwt import PyJWKClient
from ..database.sync_user import sync_user_db

KC_URL = os.getenv('KC_URL', 'http://keycloak:8080')
KC_REALM = os.getenv('KC_REALM', 'muzo-realm')
jwks_client = PyJWKClient(f"{KC_URL}/realms/{KC_REALM}/protocol/openid-connect/certs")

KC_PUBLIC_URL = os.getenv('KC_PUBLIC_URL', 'http://localhost:5002')
ISSUER_URL = f"{KC_PUBLIC_URL}/realms/{KC_REALM}"


def get_auth_ctx():
    if getattr(g, 'auth_ctx', None) is not None:
        return g.auth_ctx
    
    if "user_id" in session and "roles" in session:
        g.auth_ctx = get_ctx_from_session()
    else:
        g.auth_ctx = get_ctx_from_token()
    return g.auth_ctx


def get_ctx_from_session():
    exp = session.get("exp")
    if not exp or time.time() > exp:
        session.clear()
        raise Unauthorized("Not authenticated")

    return {
        "user_id": session.get("user_id"),
        "roles": session.get("roles"),
    }


def get_ctx_from_token():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        try:
            decoded_token = decode_token(token)
        except Exception:
            raise Unauthorized("invalid token")
        
        user = sync_user_db(decoded_token)

        user_roles = decoded_token.get("realm_access", {}).get("roles", [])
        return {
            "user_id": user.id,
            "roles": {
                "ROLE_ARTIST": "ROLE_ARTIST" in user_roles,
                "ROLE_ADMIN": "ROLE_ADMIN" in user_roles
            }
        }
    raise Unauthorized("missing authorization")
            

def decode_token(token):
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False},
            issuer=ISSUER_URL
        )


def get_user_id():
    return get_auth_ctx()["user_id"]

def get_user_roles():
    return get_auth_ctx()["roles"]
