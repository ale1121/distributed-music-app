import json
import requests
import jwt
from jwt import PyJWKClient
from functools import wraps
from flask import (
    Blueprint, current_app, redirect, request, session, url_for, render_template
)
from .models import db, User, Role

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            print("not logged in: redirrecting")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated

def role_required(required_role):
    """Allow access if user has the required role OR is an admin."""
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user" not in session:
                return redirect(url_for("auth.login"))
            roles = session["user"].get("realm_access", {}).get("roles", [])
            if "ROLE_ADMIN" in roles or required_role in roles:
                return f(*args, **kwargs)
            return render_template("access_denied.html")
        return decorated
    return wrapper

def sync_user_from_token(decoded_token):
    sub = decoded_token.get('sub')
    email = decoded_token.get('email')
    username = decoded_token.get('preferred_username')

    realm_roles = decoded_token.get('realm_access', {}).get('roles', [])

    user = User.query.filter_by(keycloak_id=sub).first()
    if not user:
        user = User(
            keycloak_id=sub,
            email=email,
            username=username,
        )
        db.session.add(user)

    if realm_roles:
        db_roles = Role.query.filter(Role.name.in_(realm_roles)).all()
        user.roles = db_roles

    db.session.commit()

    return user


@auth_bp.route("/")
def home():
    if "user" in session:
        username = session["user"].get("preferred_username", "User")
        roles = session["user"].get("realm_access", {}).get("roles", [])
        role_info = ", ".join(roles) if roles else "No roles"

        return render_template("home.html", user=session["user"], username=username, role_info=role_info)
    return render_template("home.html", user=None)


@auth_bp.route("/login")
def login():
    conf = current_app.config

    auth_redirect = (
        f"{conf['AUTH_URL']}?client_id={conf['KC_CLIENT_ID']}"
        f"&response_type=code&scope=openid profile email"
        f"&redirect_uri={conf['KC_REDIRECT_URI']}"
    )
    return redirect(auth_redirect)


@auth_bp.route("/callback")
def callback():
    conf = current_app.config

    # Extract auth code from the URL query parameters sent by Keycloak    
    code = request.args.get("code")
    if not code:
        return render_template('login_failed.html', message='Missing code'), 404


    # Prepare the data for the token exchange request
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": conf['KC_REDIRECT_URI'],
        "client_id": conf['KC_CLIENT_ID'],
    }

    # Exchange the authorization code for token

    response = requests.post(conf['TOKEN_URL'], data=data)
    if response.status_code != 200:
        return render_template(
            'login_failed.html',
            reason=f'Token endpoint error: {response.status_code}'), 400

    # Parse the token and extract: access token and identity token
    tokens = response.json()
    access_token = tokens.get("access_token")
    id_token = tokens.get("id_token")

    if not access_token:
        return render_template("login_failed.html", message="No access token in response")

    # Decode JWT
    jwks_client = PyJWKClient(conf['JWKS_URL'])
    signing_key = jwks_client.get_signing_key_from_jwt(access_token)

    try:
        decoded_token = jwt.decode(
            access_token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False},
            issuer=conf['ISSUER_URL']
        )
    except Exception as e:
        return render_template('login_failed.html', message=str(e)), 400

    # Sync user in db
    user = sync_user_from_token(decoded_token)

    # Store tokens in the current session

    session['user'] = decoded_token
    session['access_token'] = access_token
    session['id_token'] = id_token
    session['user_id'] = user.id

    return redirect(url_for("auth.home"))


@auth_bp.route("/logout")
def logout():
    conf = current_app.config
    id_token = session.get("id_token")
    session.clear()

    logout_redirect = (
        f"{conf['LOGOUT_URL']}?client_id={conf['KC_CLIENT_ID']}"
        f"&post_logout_redirect_uri={url_for('auth.home', _external=True)}"
    )

    if id_token:
        logout_redirect += f"&id_token_hint={id_token}"

    return redirect(logout_redirect)


@auth_bp.route("/user")
@login_required
@role_required("ROLE_USER")
def user_dashboard():
    username = session["user"].get("preferred_username")
    return render_template("user_dashboard.html", username=username)


@auth_bp.route("/artist")
@login_required
@role_required("ROLE_ARTIST")
def student_dashboard():
    username = session["user"].get("preferred_username")
    return render_template("artist_dashboard.html", username=username)


@auth_bp.route("/admin")
@login_required
@role_required("ROLE_ADMIN")
def admin_dashboard():
    username = session["user"].get("preferred_username")
    return render_template("admin_dashboard.html", username=username)


@auth_bp.route("/debug")
def debug():
    user_data = json.dumps(session.get('user', {}), indent=2)
    return render_template("debug.html", user_data=user_data)