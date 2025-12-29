import os
import time
from flask import (
    Blueprint, session, render_template, request, current_app,
    jsonify, send_from_directory
)
from werkzeug.exceptions import BadRequest, NotFound
from sqlalchemy import select
from app.utils.decorators import role_required, login_required
from app.db import Session
from app.models import Artist, Album
from app.utils.image import crop_resize_save_image
from app.utils.user_roles import get_user_roles


artist_bp = Blueprint('artist', __name__)


@artist_bp.route("/artist-account")
@role_required("ROLE_ARTIST")
def edit_view():
    """ View 'Artist Account' page """

    artist = Session.get(Artist, session["user_id"])
    if not artist:
        raise NotFound("Artist not found")
    
    stmt = select(Album).where(Album.artist == artist).order_by(Album.release_year.desc())
    albums = Session.scalars(stmt)

    current_app.logger.debug(f"---ALBUMS: {albums}")
    
    username = session["user"].get("preferred_username")
    display_name = session["user"].get("display_name")
    return render_template("pages/artist_dashboard.html",
                avatar_path=artist.avatar_path,
                albums=albums,
                current_path='/artist-account',
                roles=get_user_roles())


@artist_bp.route("/artist-account/avatar", methods=['POST'])
@role_required("ROLE_ARTIST")
def upload_profile_image():
    """ Upload artist avatar """

    if "image" not in request.files:
        raise BadRequest("Missing image")
    
    artist_id = session["user_id"]

    artist = Session.get(Artist, artist_id)
    if not artist:
        raise NotFound("Artist not found")
    
    if artist.avatar_path:
        try:
            os.remove(artist.avatar_path)
        except:
            pass
        finally:
            artist.avatar_path = None
    
    out_dir = current_app.config['AVATARS_PATH']
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(out_dir, f"profile-{artist_id}-{ts}.webp")

    try:
        crop_resize_save_image(request.files["image"], out_path, size=512)
    except:
        raise BadRequest("Invalid image file")
    
    artist.avatar_path = out_path
    Session.commit()
    
    return jsonify(profile_url=out_path), 201


@artist_bp.route("/artist-account/avatar", methods=["DELETE"])
@role_required("ROLE_ARTIST")
def delete_profile_image():
    """ Delete artist avatar """

    artist = Session.get(Artist, session["user_id"])
    
    if not artist:
        raise NotFound("Artist not found")
    if not artist.avatar_path:
        raise NotFound("Image path not found")
    
    try:
        os.remove(artist.avatar_path)
    except FileNotFoundError:
        raise NotFound("Image not found")
    finally:
        artist.avatar_path = None
        Session.commit()

    return jsonify(ok=True), 200
