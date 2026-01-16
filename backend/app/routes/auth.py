import requests
import jwt
from jwt import PyJWKClient
from flask import Blueprint, current_app, redirect, request, session, url_for, render_template
from app.database.sync_user import sync_user_db


auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/api/login")
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
        return render_template('errors/login_failed.html', message='Missing code'), 404


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
            'errors/login_failed.html',
            message=f'{response.reason}'), 400

    # Parse the token and extract: access token and identity token
    tokens = response.json()
    access_token = tokens.get("access_token")
    id_token = tokens.get("id_token")

    if not access_token:
        return render_template("errors/login_failed.html", message="No access token in response")

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

        # Sync user in db
        user = sync_user_db(decoded_token)

        # Store token info in the current session
        user_roles  = decoded_token.get("realm_access", {}).get("roles", [])
        session["exp"] = decoded_token.get("exp")
        session['user_id'] = user.id
        session["roles"] = {
            "ROLE_ARTIST": "ROLE_ARTIST" in user_roles,
            "ROLE_ADMIN": "ROLE_ADMIN" in user_roles
        }

    except Exception as e:
        return render_template('errors/login_failed.html', message=str(e)), 400

    return redirect(url_for("home.view"))


@auth_bp.route("/api/logout")
def logout():
    session.clear()

    conf = current_app.config
    logout_redirect = (
        f"{conf['LOGOUT_URL']}?client_id={conf['KC_CLIENT_ID']}"
        f"&post_logout_redirect_uri={url_for('home.view', _external=True)}"
    )

    return redirect(logout_redirect)
