import os
import uuid
from datetime import datetime
from flask import (
    Blueprint, render_template, request, current_app, session, jsonify, redirect, url_for
)
from werkzeug.exceptions import NotFound, BadRequest, Forbidden
from sqlalchemy import select
from app.utils.decorators import role_required, login_required
from app.db import Session
from app.models import Album, Song, Artist, User
from app.utils.image import crop_resize_save_image
from app.utils.db_helpers import get_album
from app.utils.user_roles import get_user_roles


album_bp = Blueprint('album', __name__)


@album_bp.route("/album/<int:album_id>", methods=["GET"])
@login_required
def view(album_id):
    album = get_album(album_id)
    artist = album.artist
    artist_user = artist.user

    stmt = select(Song).where(Song.album == album) \
        .order_by(Song.position).order_by(Song.title)
    songs = Session.scalars(stmt).all()

    return render_template('pages/album.html',
                            album=album, artist=artist, songs=songs,
                            num_songs=len(songs),
                            artist_name=artist_user.display_name,
                            roles=get_user_roles())


@album_bp.route("/album/<int:album_id>/edit", methods=["GET"])
@role_required("ROLE_ARTIST")
def edit_view(album_id):
    """ View album edit page """

    album = get_album(album_id, artist_required=True)

    stmt = select(Song).where(Song.album == album) \
        .order_by(Song.position).order_by(Song.title)
    songs = Session.scalars(stmt).all()
    
    return render_template('pages/album_edit.html',
                            album=album, songs=songs,
                            roles=get_user_roles())


@album_bp.route("/album/<int:album_id>/edit", methods=["POST"])
@role_required("ROLE_ARTIST")
def save_details(album_id):
    """ Update album tile and release year """

    album = get_album(album_id, artist_required=True)

    data = request.get_json()
    if "release_year" not in data or "title" not in data:
        raise BadRequest("Missing album details")
        
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

    album = get_album(album_id, artist_required=True)
    album.published = True
    Session.commit()

    return jsonify(ok=True), 200


@album_bp.route("/album/<int:album_id>/delete", methods=["POST"])
@role_required("ROLE_ARTIST")
def delete_album(album_id):
    """ Delete album """

    album = get_album(album_id, artist_required=True)

    if album.cover_path:
        try: os.remove(album.cover_path)
        except: pass

    songs = Session.scalars(select(Song).where(Song.album == album))
    for song in songs:
        if song.audio_path:
            try: os.remove(song.audio_path)
            except: pass
        Session.delete(song)

    Session.delete(album)
    Session.commit()

    return redirect(url_for('artist.edit_view'), code=303)


@album_bp.route("/album/<int:album_id>/cover", methods=["POST"])
@role_required("ROLE_ARTIST")
def upload_cover_image(album_id):
    """ Upload album cover """

    if "image" not in request.files:
        raise BadRequest("Missing image")
    
    album = get_album(album_id, artist_required=True)
    
    if album.cover_path:
        try: os.remove(album.cover_path)
        except: pass
        finally: album.cover_path = None

    out_dir = current_app.config['COVERS_PATH']
    out_path = os.path.join(out_dir, f"cover-{album_id}-{uuid.uuid4().hex}.webp")

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

    album = get_album(album_id, artist_required=True)
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
