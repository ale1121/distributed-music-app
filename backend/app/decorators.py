from flask import session, redirect, url_for, render_template
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            print("not logged in: redirrecting")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def role_required(required_role):
    """Allow access if user has the required role"""
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user" not in session:
                return redirect(url_for("auth.login"))
            roles = session["user"].get("realm_access", {}).get("roles", [])
            if required_role in roles:
                return f(*args, **kwargs)
            return render_template("access_denied.html")
        return decorated
    return wrapper