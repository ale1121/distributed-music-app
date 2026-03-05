import os
from flask import Blueprint, request, current_app, jsonify, render_template, url_for
from werkzeug.exceptions import BadRequest, HTTPException
from app.auth.decorators import role_required, login_required
from app.database.db_helpers import get_album, get_song
from app.auth.auth_ctx import get_user_roles, get_user_id
from app.utils.audio import save_audio_file
from app.database.db import Session
from app.database.models import Song, Play
from app.opensearch import opensearch
from app.utils.stream import sign_streaming_url


song_bp = Blueprint('song', __name__)


@song_bp.route("/song/<int:song_id>", methods=["GET"])
@login_required
def view(song_id):
    song = get_song(song_id)
    album = song.album
    artist = album.artist

    return render_template('pages/song.html',
                    song=song, album=album,
                    artist=artist,
                    artist_name=artist.user.display_name,
                    roles=get_user_roles()), 200


@song_bp.route("/api/albums/<int:album_id>/songs", methods=["POST"])
@role_required("ROLE_ARTIST")
def add_song(album_id):
    """ Add new song to the album """

    album = get_album(album_id, artist_required=True)

    title = (request.form.get("title") or "").strip()
    position = request.form.get("position") or 0
    audio = request.files.get("audio")

    # validate song details
    if not title or not audio or not audio.filename:
        raise BadRequest("Missing song details")
    
    if len(title) > 100:
        raise BadRequest("Title too long")

    position = int(position)
    if position < 0 or position > 1000:
        raise BadRequest('Invalid position')

    out_dir = current_app.config['AUDIO_PATH']
    try:
        out_file, duration = save_audio_file(
            audio, out_dir, f"audio-{album.id}")
    except HTTPException:
        raise
    except Exception:
        raise BadRequest("Invalid audio file")

    # add song to db
    song = Song(
        title=title,
        position=position,
        audio_file = out_file,
        duration = duration,
        album_id = album.id
    )
    Session.add(song)
    Session.commit()
    Session.refresh(song)

    if album.published:
        # index song if album is public
        opensearch.index_document(song.title, 'song', song.id,
                                url_for('song.view', song_id=song.id),
                                artist=album.artist.user.display_name)

    return jsonify({"song_id": song.id}), 201


@song_bp.route("/api/songs/<int:song_id>", methods=["PUT"])
@role_required("ROLE_ARTIST")
def save_details(song_id):
    """ Update song tilte and position """

    song = get_song(song_id, artist_required=True)

    # validate song details
    data = request.get_json()
    if "title" not in data or "position" not in data:
        raise BadRequest("Missing song details")

    position = int(data["position"])
    if position < 0:
        raise BadRequest("Invalid position")
    
    title = data["title"].strip()
    if len(title) > 100:
        raise BadRequest("Title too long")

    # update song in db
    song.title = title
    song.position = position
    Session.commit()
    Session.refresh(song)

    if song.album.published:
        # reindex song if album is public
        opensearch.index_document(song.title, 'song', song.id,
                                url_for('song.view', song_id=song.id),
                                artist=song.album.artist.user.display_name)
    
    return jsonify(ok=True), 200


@song_bp.route("/api/songs/<int:song_id>", methods=["DELETE"])
@role_required("ROLE_ARTIST")
def delete_song(song_id):
    """ Delete song """

    song = get_song(song_id, artist_required=True)

    # remove audio file
    audio_dir = current_app.config['AUDIO_PATH']
    try: os.remove(os.path.join(audio_dir, song.audio_file))
    except: pass
    
    # delete song from db
    Session.delete(song)
    Session.commit()

    # delete song from index
    if song.album.published:
        opensearch.delete_document(song.id, 'song')

    return jsonify(ok=True), 200


@song_bp.route("/api/songs/<int:song_id>/play", methods=["GET"])
@login_required
def play_song(song_id):
    song = get_song(song_id)

    # get signed streaming url for song
    stream_url = sign_streaming_url(song.audio_file)

    # save play to db
    play = Play(
        song_id=song.id,
        user_id=get_user_id()
    )
    Session.add(play)
    Session.commit()

    return jsonify({
        "stream_url": stream_url
    }), 200
