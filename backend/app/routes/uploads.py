import os
from flask import send_from_directory, Blueprint, current_app


uploads_bp = Blueprint("uplaods", __name__)

AVATARS_PATH = os.path.join(os.getenv('UPLOADS_PATH', '/uploads'), "avatars")


@uploads_bp.route(f'{AVATARS_PATH}/<path:filename>')
def get_avatar(filename):
    """ Get profile image file """
    return send_from_directory(AVATARS_PATH, filename)
