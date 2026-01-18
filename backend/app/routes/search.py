from flask import Blueprint, request, current_app, jsonify, url_for
from app.auth.decorators import login_required, role_required
from app.opensearch import opensearch
from app.opensearch.conf import OPENSEARCH_DOC_TYPES
from werkzeug.exceptions import InternalServerError
from app.database.db import Session
from app.database.models import Artist, Album, Song


search_bp = Blueprint('search', __name__)


@search_bp.route("/api/search/suggest", methods=["GET"])
@login_required
def search_suggestions():
    """
    Get minimal search suggestions from OpenSearch
    """
    name = request.args.get("q")
    type = request.args.get("type")

    # validate search terms
    if name is None or len(name) < 3 or len(name) > 100:
        return []
    if type not in OPENSEARCH_DOC_TYPES:
        type = None
    
    # get opensearch results, use multi-match for name
    results = opensearch.search(name, type=type, multi_match=True, limit=6)

    return jsonify(results), 200


@search_bp.route("/api/search/results", methods=["GET"])
@login_required
def search_full():
    """
    Get full search results from OpenSearch and database
    """
    name = request.args.get("q")
    type = request.args.get("type")

    # validate search terms
    if name is None or len(name) < 3 or len(name) > 100:
        return []
    if type not in OPENSEARCH_DOC_TYPES:
        type = None
    
    # get opensearch results, use full-text search for name
    results = opensearch.search(name, type=type, multi_match=False, limit=12)

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


@search_bp.route("/api/admin/reindex-catalog", methods=["POST"])
@role_required("ROLE_ADMIN")
def reindex_catalog():
    """ Reindex entire catalog from db in OpenSearch """
    try:
        opensearch.reindex_all()
    except RuntimeError as e:
        current_app.logger.error(str(e))
        raise InternalServerError("Reindexing failed. See error log for details.")
    return jsonify(ok=True), 200
