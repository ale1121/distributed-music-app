import os
from flask import Blueprint, render_template, request, current_app, jsonify
from werkzeug.exceptions import BadRequest, NotFound, Forbidden, HTTPException
from sqlalchemy import select
from app.auth.decorators import role_required, login_required
from app.database.db import Session
from app.database.models import Artist, Album
from app.utils.image import crop_resize_save_image
from app.auth.auth_ctx import get_user_roles, get_user_id


artist_bp = Blueprint('artist', __name__)


@artist_bp.route("/artist/<int:artist_id>")
@login_required
def view(artist_id):
    """ View artist page """

    artist = Session.get(Artist, artist_id)
    if not artist:
        raise NotFound("Artist not found")

    stmt = select(Album).where(Album.artist == artist) \
        .where(Album.published == True) \
        .order_by(Album.release_year.desc()).order_by(Album.title)
    albums = Session.scalars(stmt).all()

    return render_template("pages/artist.html",
                artist=artist, artist_name=artist.user.display_name,
                albums=albums, num_albums=len(albums),
                roles=get_user_roles()), 200


@artist_bp.route("/artist-account")
@role_required("ROLE_ARTIST")
def edit_view():
    """ View 'Artist Account' page """

    artist = Session.get(Artist, get_user_id())
    if not artist:
        raise NotFound("Artist not found")
    
    stmt = select(Album).where(Album.artist == artist) \
        .order_by(Album.release_year.desc()).order_by(Album.title)
    albums = Session.scalars(stmt)

    return render_template("pages/artist_dashboard.html",
                avatar_file=artist.avatar_file,
                artist_id=artist.id, albums=albums,
                current_path='/artist-account',
                roles=get_user_roles()), 200


@artist_bp.route("/api/artists/<int:artist_id>/avatar", methods=['PUT'])
@role_required("ROLE_ARTIST")
def upload_avatar(artist_id):
    """ Upload artist avatar """

    if "image" not in request.files:
        raise BadRequest("Missing image")

    if artist_id != get_user_id():
        raise Forbidden("You can only change your own avatar")

    artist = Session.get(Artist, artist_id)
    if not artist:
        raise NotFound("Artist not found")
    
    avatars_dir = current_app.config['AVATARS_PATH']

    if artist.avatar_file:
        # remove existing file
        try:
            avatar_path = os.path.join(avatars_dir, artist.avatar_file)
            os.remove(avatar_path)
        except:
            pass
        finally:
            artist.avatar_file = None

    # save new file
    try:
        out_file, out_path = crop_resize_save_image(
            request.files["image"], avatars_dir,
            f"profile-{artist_id}", size=512)
    except:
        raise BadRequest("Invalid image file")

    artist.avatar_file = out_file
    Session.commit()
    return jsonify(image_url=out_path), 201


@artist_bp.route("/api/artists/<int:artist_id>/avatar", methods=["DELETE"])
@role_required("ROLE_ARTIST")
def delete_avatar(artist_id):
    """ Delete artist avatar """

    if artist_id != get_user_id():
        raise Forbidden("You can only delete your own avatar")

    artist = Session.get(Artist, artist_id)
    if not artist:
        raise NotFound("Artist not found")
    if not artist.avatar_file:
        raise NotFound("Image path not found")
    
    try:
        avatars_dir = current_app.config['AVATARS_PATH']
        avatar_path = os.path.join(avatars_dir, artist.avatar_file)
        os.remove(avatar_path)
    except: 
        pass
    finally:
        artist.avatar_file = None
        Session.commit()

    return jsonify(ok=True), 200
