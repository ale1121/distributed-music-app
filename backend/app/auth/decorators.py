from functools import wraps
from werkzeug.exceptions import Forbidden
from .auth_ctx import get_auth_ctx, get_user_roles


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        get_auth_ctx()
        return f(*args, **kwargs)
    return decorated


def role_required(required_role):
    """
    Allow access if user has the required role
    Also ensures user is logged in
    """
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            roles = get_user_roles()
            if roles and roles.get(required_role, False):
                return f(*args, **kwargs)
            raise Forbidden("You don't have permission to view this page.")
        return decorated
    return wrapper
