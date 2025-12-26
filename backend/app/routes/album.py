import os
import time
from datetime import datetime
from flask import (
    Blueprint, render_template, request, current_app, session, jsonify, redirect, url_for
)
from werkzeug.exceptions import NotFound, BadRequest, Forbidden
from sqlalchemy import select
from app.decorators import role_required
from app.db import Session
from app.models import Album, Song
from app.utils.image import crop_resize_save_image


album_bp = Blueprint('album', __name__)


@album_bp.route("/album/<int:album_id>/edit", methods=["GET"])
@role_required("ROLE_ARTIST")
def edit_view(album_id):
    """ View album edit page """

    album = get_album(album_id)

    stmt = select(Song).where(Song.album == album)
    songs = Session.scalars(stmt)
    
    return render_template('album_edit.html',
                            album=album, songs=songs,
                            default_cover=current_app.config['DEFAULT_COVER'])


@album_bp.route("/album/<int:album_id>/edit", methods=["POST"])
@role_required("ROLE_ARTIST")
def save_details(album_id):
    """ Update album tile and release year """

    album = get_album(album_id)

    data = request.get_json()

    release_year = int(data["release_year"])
    if release_year < 1000 or release_year > datetime.now().year:
        raise BadRequest("Invalid release year")
    
    title = data["title"].strip()
    if len(title) > 100:
        raise BadRequest("Title too long")

    album.title = title
    album.release_year = release_year

    Session.commit()
    
    return jsonify(ok=True), 200


@album_bp.route("/album/<int:album_id>/publish", methods=["POST"])
@role_required("ROLE_ARTIST")
def publish_album(album_id):
    """ Make album public """

    album = get_album(album_id)
    album.published = True
    Session.commit()

    return jsonify(ok=True), 200


@album_bp.route("/album/<int:album_id>/delete", methods=["POST"])
@role_required("ROLE_ARTIST")
def delete_album(album_id):
    """ Delete album """

    album = get_album(album_id)
    Session.delete(album)
    Session.commit()

    return redirect(url_for('artist_acc.view'), code=303)


@album_bp.route("/album/<int:album_id>/cover", methods=["POST"])
@role_required("ROLE_ARTIST")
def upload_cover_image(album_id):
    """ Upload album cover """

    if "image" not in request.files:
        raise BadRequest("Missing image")
    
    album = get_album(album_id)
    
    if album.cover_path:
        try:
            os.remove(album.cover_path)
        except:
            pass
        finally:
            album.cover_path = None

    out_dir = current_app.config['COVERS_PATH']
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(out_dir, f"cover-{album_id}-{ts}.webp")

    try:
        crop_resize_save_image(request.files["image"], out_path, size=512)
    except:
        raise BadRequest("Invalid image file")
    
    album.cover_path = out_path
    Session.commit()
    
    return jsonify(cover_url=out_path), 201


@album_bp.route("/album/<int:album_id>/cover", methods=["DELETE"])
@role_required("ROLE_ARTIST")
def delete_cover_image(album_id):
    """ Delete album cover """

    album = get_album(album_id)
    if not album.cover_path:
        raise NotFound("Image path not found")
    
    try:
        os.remove(album.cover_path)
    except FileNotFoundError:
        raise NotFound("Image not found")
    finally:
        album.cover_path = None
        Session.commit()

    return jsonify(ok=True), 200


@album_bp.route("/album/create", methods=["POST"])
@role_required("ROLE_ARTIST")
def create_album():
    """ Create a new album with default details """

    album = Album(
        title="Untitled Album",
        artist_id = session["user_id"],
        published=False
    )
    Session.add(album)
    Session.commit()
    Session.refresh(album)

    return redirect(url_for('album.edit_view', album_id=album.id), code=303)


def get_album(album_id):
    """
    Get album from db, check if user can edit album
    """

    album = Session.get(Album, album_id)
    if not album:
        raise NotFound("Album not found")
    if album.artist_id != session["user_id"]:
        raise Forbidden("You don't have permission to edit this album")
    return album
