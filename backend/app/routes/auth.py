import requests
import jwt
from jwt import PyJWKClient
from flask import Blueprint, current_app, redirect, request, session, url_for, render_template
from sqlalchemy import select
from app.db import Session
from app.models import User, Artist


auth_bp = Blueprint('auth', __name__)


def sync_user_db(decoded_token):
    sub = decoded_token.get('sub')
    email = decoded_token.get('email')
    username = decoded_token.get('preferred_username')
    display_name = decoded_token.get('display_name')

    user = Session.scalar(select(User).where(User.keycloak_id == sub))
    if not user:
        user = User(
            keycloak_id=sub,
            email=email,
            username=username,
            display_name=display_name,
        )
        Session.add(user)
    else:
        user.email = email
        user.display_name = display_name
        
    if 'ROLE_ARTIST' in decoded_token.get('realm_access', {}).get('roles', []):
        artist = Session.get(Artist, user.id)
        if not artist:
            artist = Artist(id=user.id)
            Session.add(artist)

    Session.commit()
    Session.refresh(user)
    
    return user


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
            message=f'{response.reason}'), 400

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

        # Sync user in db
        user = sync_user_db(decoded_token)

        # Store tokens in the current session
        session['user'] = decoded_token
        session['access_token'] = access_token
        session['id_token'] = id_token
        session['user_id'] = user.id

    except Exception as e:
        return render_template('login_failed.html', message=str(e)), 400

    return redirect(url_for("menu.home"))


@auth_bp.route("/logout")
def logout():
    conf = current_app.config
    id_token = session.get("id_token")
    session.clear()

    logout_redirect = (
        f"{conf['LOGOUT_URL']}?client_id={conf['KC_CLIENT_ID']}"
        f"&post_logout_redirect_uri={url_for('menu.home', _external=True)}"
    )

    if id_token:
        logout_redirect += f"&id_token_hint={id_token}"

    return redirect(logout_redirect)
