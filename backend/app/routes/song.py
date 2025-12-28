import os
import uuid
from flask import (
    Blueprint, request, current_app, session, jsonify
)
from werkzeug.exceptions import BadRequest, Forbidden, NotFound
from sqlalchemy import select
from app.utils.decorators import role_required
from app.utils.db_helpers import get_album, get_song
from app.db import Session
from app.models import Album, Song


song_bp = Blueprint('song', __name__)


@song_bp.route("/album/<int:album_id>/song/<int:song_id>/edit", methods=["POST"])
@role_required("ROLE_ARTIST")
def save_details(album_id, song_id):
    """ Update song tile """

    song = get_song(album_id, song_id, artist_required=True)

    data = request.get_json()
    if "title" not in data or "position" not in data:
        raise BadRequest("Missing song details")

    position = int(data["position"])
    if position < 0:
        raise BadRequest("Invalid position")
    
    title = data["title"].strip()
    if len(title) > 100:
        raise BadRequest("Title too long")

    song.title = title
    song.position = position

    Session.commit()
    
    return jsonify(ok=True), 200


@song_bp.route("/album/<int:album_id>/song/<int:song_id>", methods=["DELETE"])
@role_required("ROLE_ARTIST")
def delete_song(album_id, song_id):
    """ Delete song """

    song = get_song(album_id, song_id, artist_required=True)

    if song.audio_path:
        try: os.remove(song.audio_path)
        except: pass
    
    Session.delete(song)
    Session.commit()

    return jsonify(ok=True), 200


@song_bp.route("/album/<int:album_id>/song", methods=["POST"])
@role_required("ROLE_ARTIST")
def add_song(album_id):
    """ Add new song to the album """

    album = get_album(album_id, artist_required=True)

    title = (request.form.get("title") or "").strip()
    position = request.form.get("position") or ""
    audio = request.files.get("audio")

    if not title or not position or not audio or not audio.filename:
        raise BadRequest("Missing song details")
    
    position = int(position)
    if position < 0:
        raise BadRequest('Invalid position')

    file_ext = os.path.splitext(audio.filename)[1]
    if file_ext not in {'.mp3'}:
        raise BadRequest('Unsupported file type')
    
    out_dir = current_app.config['AUDIO_PATH']
    os.makedirs(out_dir, exist_ok=True)

    out_path = os.path.join(out_dir, f"audio-{album_id}-{uuid.uuid4().hex}{file_ext}")
    audio.save(out_path)

    song = Song(
        title=title,
        position=position,
        audio_path = out_path,
        album_id = album_id
    )
    Session.add(song)
    Session.commit()

    return jsonify(ok=True), 201
