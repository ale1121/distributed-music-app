import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'secretkey')

    KC_URL = os.getenv('KC_URL', 'http://keycloak:8080')
    KC_PUBLIC_URL = os.getenv('KC_PUBLIC_URL', 'http://localhost:5002')
    KC_REALM = os.getenv('KC_REALM', 'muzo-realm')
    KC_CLIENT_ID = os.getenv('KC_CLIENT_ID', 'muzo-client')
    KC_REDIRECT_URI = os.getenv('KC_REDIRECT_URI', 'http://localhost:5000/callback')

    ISSUER_URL = f"{KC_PUBLIC_URL}/realms/{KC_REALM}"

    AUTH_URL = f"{KC_PUBLIC_URL}/realms/{KC_REALM}/protocol/openid-connect/auth"
    LOGOUT_URL = f"{KC_PUBLIC_URL}/realms/{KC_REALM}/protocol/openid-connect/logout"
    TOKEN_URL = f"{KC_URL}/realms/{KC_REALM}/protocol/openid-connect/token"
    USERINFO_URL = f"{KC_URL}/realms/{KC_REALM}/protocol/openid-connect/userinfo"
    JWKS_URL = f"{KC_URL}/realms/{KC_REALM}/protocol/openid-connect/certs"

    ACCOUNT_URL = f"{KC_PUBLIC_URL}/realms/{KC_REALM}/account"
    ADMIN_URL = f"{KC_PUBLIC_URL}/admin/{KC_REALM}/console/#/{KC_REALM}"

    UPLOADS_PATH = os.getenv('UPLOADS_PATH', '/uploads')
    AVATARS_PATH = os.path.join(UPLOADS_PATH, "avatars")
    COVERS_PATH = os.path.join(UPLOADS_PATH, 'covers')
    
    AUDIO_PATH = os.getenv('AUDIO_PATH', '/data/audio')

    STREAMING_URL = os.getenv('STREAMING_URL', 'http://localhost:5001')

    GRAFANA_URL = os.getenv('GRAFANA_URL', 'http://localhost:5003')
    GRAFANA_DASHBOARD = os.getenv('GRAFANA_DASHBOARD', 'muzo-stats')
