import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')

    KC_URL = os.getenv('KC_URL')
    KC_PUBLIC_URL = os.getenv('KC_PUBLIC_URL')
    KC_REALM = os.getenv('KC_REALM')
    KC_CLIENT_ID = os.getenv('KC_CLIENT_ID')
    KC_REDIRECT_URI = os.getenv('KC_REDIRECT_URI')

    ISSUER_URL = f"{KC_PUBLIC_URL}/realms/{KC_REALM}"

    AUTH_URL = f"{KC_PUBLIC_URL}/realms/{KC_REALM}/protocol/openid-connect/auth"
    LOGOUT_URL = f"{KC_PUBLIC_URL}/realms/{KC_REALM}/protocol/openid-connect/logout"
    TOKEN_URL = f"{KC_URL}/realms/{KC_REALM}/protocol/openid-connect/token"
    USERINFO_URL = f"{KC_URL}/realms/{KC_REALM}/protocol/openid-connect/userinfo"
    JWKS_URL = f"{KC_URL}/realms/{KC_REALM}/protocol/openid-connect/certs"

    ACCOUNT_URL = f"{KC_PUBLIC_URL}/realms/{KC_REALM}/account"
    ADMIN_URL = f"{KC_PUBLIC_URL}/admin/{KC_REALM}/console/#/{KC_REALM}"
