from flask import Blueprint, request, current_app, session, jsonify, url_for
from app.utils.decorators import login_required
from app.utils.opensearch import opensearch
from werkzeug.exceptions import BadRequest
from sqlalchemy import select
from app.db import Session
from app.models import Artist, Album, Song


search_bp = Blueprint('search', __name__)


@search_bp.route("/search/preview", methods=["GET"])
@login_required
def search_preview():
    """ Get minimal search suggestions from OpenSearch """
    name = request.args.get("q")
    type = request.args.get("type")

    # validate search terms
    if name is None or len(name) < 3 or len(name) > 100:
        return []
    if type not in opensearch.TYPES:
        type = None
    
    # get opensearch results
    results = opensearch.search(name, type=type, limit=6)

    return jsonify(results), 200


@search_bp.route("/search/results", methods=["GET"])
@login_required
def search_full():
    """ Get full search results from OpenSearch and database """
    name = request.args.get("q")
    type = request.args.get("type")

    # validate search terms
    if name is None or len(name) < 3 or len(name) > 100:
        return []
    if type not in opensearch.TYPES:
        type = None
    
    # get opensearch results
    results = opensearch.search(name, type=type, limit=12)

    # add details from db
    full_results = []
    for res in results:
        if res["type"] == "Artist":
            artist = Session.get(Artist, res["id"])
            if not artist: continue
            # add avatar path
            full_results.append({
                "type": "Artist", "name": res["name"], "url": res["url"],
                "img": url_for('uploads.get_avatar', filename=artist.avatar_file) if artist.avatar_file
                        else url_for('static', filename='assets/placeholder-avatar.webp')
            })
        elif res["type"] == "Album":
            album = Session.get(Album, res["id"])
            if not album: continue
            # add cover path + year
            full_results.append({
                "type": "Album", "name": res["name"], "url": res["url"], "artist": res["artist"],
                "img": url_for('uploads.get_cover', filename=album.cover_file) if album.cover_file
                        else url_for('static', filename='assets/placeholder-cover.webp'),
                "year": album.release_year
            })
        else:
            song = Session.get(Song, res["id"])
            if not song: continue
            album = song.album
            # add album cover path + album title
            full_results.append({
                "type": "Song", "name": res["name"], "url": res["url"], "artist": res["artist"],
                "img": url_for('uploads.get_cover', filename=album.cover_file) if album.cover_file
                        else url_for('static', filename='assets/placeholder-cover.webp'),
                "album": album.title
            })

    return jsonify(full_results), 200
