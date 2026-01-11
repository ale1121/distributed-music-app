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
from app.utils.opensearch import opensearch


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

    # validate album details
    data = request.get_json()
    if "release_year" not in data or "title" not in data:
        raise BadRequest("Missing album details")
        
    release_year = int(data["release_year"])
    if release_year < 1000 or release_year > datetime.now().year:
        raise BadRequest("Invalid release year")
    
    title = data["title"].strip()
    if len(title) > 100:
        raise BadRequest("Title too long")

    # update album in db
    album.title = title
    album.release_year = release_year
    Session.commit()
    Session.refresh(album)

    if album.published:
        # reindex album if public
        opensearch.index_document(album.title, 'album', album.id,
                url_for('album.view', album_id=album.id,
                artist=album.artist.user.display_name))

    return jsonify(ok=True), 200


@album_bp.route("/album/<int:album_id>/publish", methods=["POST"])
@role_required("ROLE_ARTIST")
def publish_album(album_id):
    """ Make album public """

    # update album in db
    album = get_album(album_id, artist_required=True)
    album.published = True
    Session.commit()
    Session.refresh(album)

    # index album and songs
    opensearch.index_album(album)

    return jsonify(ok=True), 200


@album_bp.route("/album/<int:album_id>/delete", methods=["POST"])
@role_required("ROLE_ARTIST")
def delete_album(album_id):
    """ Delete album """

    album = get_album(album_id, artist_required=True)

    if album.cover_file:
        # remove cover file
        try: os.remove(album.cover_file)
        except: pass

    # delete album and songs from index
    opensearch.delete_album(album)

    # delete all songs from db
    songs = Session.scalars(select(Song).where(Song.album == album))
    for song in songs:
        if song.audio_file:
            try: os.remove(song.audio_file)
            except: pass
        Session.delete(song)

    # delete album from db
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

    covers_dir = current_app.config['COVERS_PATH']

    if album.cover_file:
        # remove existing file
        try:
            cover_path = os.path.join(covers_dir, album.cover_file)
            os.remove(cover_path)
        except:
            pass
        finally:
            album.cover_file = None

    # save new file
    try:
        out_file, out_path = crop_resize_save_image(
            request.files["image"], covers_dir,
            f"cover-{album_id}", size=512)
        album.cover_file = out_file
        Session.commit()
        return jsonify(cover_url=out_path), 201
    except:
        raise BadRequest("Invalid image file")


@album_bp.route("/album/<int:album_id>/cover", methods=["DELETE"])
@role_required("ROLE_ARTIST")
def delete_cover_image(album_id):
    """ Delete album cover """

    album = get_album(album_id, artist_required=True)
    if not album.cover_file:
        raise NotFound("Image path not found")
    
    try:
        covers_dir = current_app.config['COVERS_PATH']
        cover_path = os.path.join(covers_dir, album.cover_file)
        os.remove(cover_path)
    except FileNotFoundError:
        pass
    finally:
        album.cover_file = None
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
