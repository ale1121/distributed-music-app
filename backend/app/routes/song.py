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
    """ Update song tile """

    song = get_song(album_id, song_id)

    data = request.get_json()

    title = data["title"].strip()
    if len(title) > 100:
        raise BadRequest("Title too long")

    song.title = title

    Session.commit()
    
    return jsonify(ok=True), 200


@song_bp.route("/album/<int:album_id>/song/<int:song_id>", methods=["DELETE"])
@role_required("ROLE_ARTIST")
def delete_song(album_id, song_id):
    """ Delete song """

    song = get_song(album_id, song_id)
    Session.delete(song)
    Session.commit()

    return jsonify(ok=True), 200


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
