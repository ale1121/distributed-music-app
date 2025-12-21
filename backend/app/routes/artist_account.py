import os
from flask import (
    Blueprint, session, render_template, request, current_app,
    jsonify, send_from_directory
)
from werkzeug.exceptions import BadRequest, NotFound
from app.decorators import role_required
from app.db import Session
from app.models import Artist
from app.utils.image import crop_resize_save_image


artist_acc_bp = Blueprint('artist_acc', __name__)


@artist_acc_bp.route("/artist-account")
@role_required("ROLE_ARTIST")
def view():
    artist = Session.get(Artist, session["user_id"])
    if not artist:
        raise NotFound("Artist not found")
    
    default_avatar_path = current_app.config['DEFAULT_AVATAR']
    
    username = session["user"].get("preferred_username")
    display_name = session["user"].get("display_name")
    return render_template("artist_dashboard.html",
                           username=username, display_name=display_name,
                           avatar_path=artist.avatar_path, default_avatar_path=default_avatar_path,
                           current_path='/artist-account')


@artist_acc_bp.route("/artist-account/avatar", methods=['POST'])
@role_required("ROLE_ARTIST")
def upload_profile_image():
    if "image" not in request.files:
        raise BadRequest("Missing image")
    
    artist_id = session["user_id"]

    artist = Session.get(Artist, artist_id)
    if not artist:
        raise NotFound("Artist not found")
    
    out_dir = current_app.config['AVATARS_PATH']
    out_path = os.path.join(out_dir, f"profile-{artist_id}.jpg")

    try:
        crop_resize_save_image(request.files["image"], out_path, size=512)
    except:
        raise BadRequest("Invalid image file")
    
    artist.avatar_path = out_path
    Session.commit()
    
    return jsonify(profile_url=out_path), 201


@artist_acc_bp.route("/artiest-account/avatar", methods=["DELETE"])
@role_required("ROLE_ARTIST")
def delete_profile_image():
    artist = Session.get(Artist, session["user_id"])
    
    if not artist:
        raise NotFound("Artist not found")
    if not artist.avatar_path:
        raise NotFound("Image path not found")
    
    try:
        os.remove(artist.avatar_path)
    except FileNotFoundError:
        raise NotFound("Image not found")

    artist.avatar_path = None
    Session.commit()

    return jsonify(ok=True), 200
