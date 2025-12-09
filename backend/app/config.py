import os

class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    SQLALCHEMY_TRACK_NOTIFICATIONS = False

    SECRET_KEY = os.getenv('SECRET_KEY')

    KC_URL = os.getenv('KC_URL')
    KC_PUBLIC_URL = os.getenv('KC_PUBLIC_URL')
    KC_REALM = os.getenv('KC_REALM')
    KC_CLIENT_ID = os.getenv('KC_CLIENT_ID')
    KC_REDIRECT_URI = os.getenv('KC_REDIRECT_URI')

    ISSUER_URL = f"{KC_PUBLIC_URL}/realms/{KC_REALM}"

    AUTH_URL = f"{KC_PUBLIC_URL}/realms/{KC_REALM}/protocol/openid-connect/auth"
    TOKEN_URL = f"{KC_URL}/realms/{KC_REALM}/protocol/openid-connect/token"
    LOGOUT_URL = f"{KC_PUBLIC_URL}/realms/{KC_REALM}/protocol/openid-connect/logout"
    USERINFO_URL = f"{KC_URL}/realms/{KC_REALM}/protocol/openid-connect/userinfo"
    JWKS_URL = f"{KC_URL}/realms/{KC_REALM}/protocol/openid-connect/certs"

    ACCOUNT_URL = f"{KC_PUBLIC_URL}/realms/{KC_REALM}/account"
