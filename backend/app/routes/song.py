from flask import (
    Blueprint, request, current_app, session, jsonify
)
from werkzeug.exceptions import BadRequest, Forbidden, NotFound
from sqlalchemy import select
from app.decorators import role_required
from app.db import Session
from app.models import Album, Song


song_bp = Blueprint('song', __name__)


@song_bp.route("/album/<int:album_id>/song/<int:song_id>/edit", methods=["POST"])
@role_required("ROLE_ARTIST")
def save_details(album_id, song_id):
    return jsonify(ok=True, song_id=song_id), 200


@song_bp.route("/album/<int:album_id>/song/<int:song_id>/delete", methods=["POST"])
@role_required("ROLE_ARTIST")
def delete_song(album_id, song_id):
    return jsonify(ok=True, song_id=song_id), 200

def get_song(album_id, song_id):
    album = Session.get(Album, album_id)
    if not album:
        raise NotFound("Album not found")
    if album.artist_id != session["user_id"]:
        raise Forbidden("You don't have permission to edit this album")
    
    song = Session.get(Song, song_id)
    if not song:
        raise NotFound("Song not found")
    if song.album != album:
        raise NotFound("The song doesn't exist in this album")
    
    return song