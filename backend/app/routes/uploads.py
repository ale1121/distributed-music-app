import os
from flask import send_from_directory, Blueprint


uploads_bp = Blueprint("uploads", __name__)

UPLOADS_PATH = os.getenv('UPLOADS_PATH', '/uploads')
AVATARS_PATH = os.path.join(UPLOADS_PATH, "avatars")
COVERS_PATH = os.path.join(UPLOADS_PATH, "covers")


@uploads_bp.route(f'{AVATARS_PATH}/<path:filename>')
def get_avatar(filename):
    """ Get profile image file """
    return send_from_directory(AVATARS_PATH, filename, mimetype="image/webp")


@uploads_bp.route(f'{COVERS_PATH}/<path:filename>')
def get_cover(filename):
    """ Get album cover file """
    return send_from_directory(COVERS_PATH, filename, mimetype="image/webp")
