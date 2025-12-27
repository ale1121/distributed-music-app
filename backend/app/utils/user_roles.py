from flask import session

def get_user_roles():
    user_roles = session["user"].get("realm_access", {}).get("roles", [])
    roles = {}
    roles['artist'] = "ROLE_ARTIST" in user_roles
    roles['admin'] = "ROLE_ADMIN" in user_roles
    return roles
