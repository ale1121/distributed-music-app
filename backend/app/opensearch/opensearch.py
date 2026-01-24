import json
import requests
import time
from types import SimpleNamespace
from sqlalchemy import select, literal
from ..database.models import Song, Album, User
from ..database.db import Session
from .conf import OPENSEARCH_URL, INDEX_NAME
from .search_queries import get_query, match_name, multi_match_name, name_type_query
from .bulk_index import bulk_index, bulk_index_catalog
from .index import create_index, check_index_exists, delete_index


def search(name, type=None, multi_match=False, limit=6):
    """
    Search catalog by name, optional filter by type
    If multi_match, search name as multi-match, else search as full-text
    """
    if multi_match:
        name_query = multi_match_name(name)
    else:
        name_query = match_name(name)

    if type is None:
        payload = get_query(name_query, limit)
    else:
        payload = get_query(name_type_query(name_query, type), limit)

    r = requests.get(f"{OPENSEARCH_URL}/{INDEX_NAME}/_search", json=payload)
    if r.status_code != 200:
        raise RuntimeWarning(f"Search error: {r.status_code} {r.text}")
    return _parse_results(r.json())


def _parse_results(data):
    """ Parse search results """
    results = []
    hits = data.get("hits", {}).get("hits", [])
    for hit in hits:
        res = hit.get("_source", {})
        results.append({
            "name": res.get("name"),
            "type": res.get("type").capitalize(),
            "id": res.get("id"),
            "artist": res.get("artist"),
            "url": res.get("url")
        })
    return results


def index_document(name, type, id, url, artist=None):
    """ Index a document """
    doc = {
        "name": name,
        "type": type,
        "id": id,
        "artist": artist,
        "url": url
    }
    doc_id = f"{type}{id}"
    r = requests.put(f"{OPENSEARCH_URL}/{INDEX_NAME}/_doc/{doc_id}", json=doc)
    if r.status_code not in (200, 201):
        raise RuntimeWarning(f"Failed to index document {doc_id}: {r.status_code} {r.text}")


def delete_document(id, type):
    """ Delete a document """
    doc_id = f"{type}{id}"
    r = requests.delete(f"{OPENSEARCH_URL}/{INDEX_NAME}/_doc/{doc_id}")
    if r.status_code not in (200, 201):
        raise RuntimeWarning(f"Failed to delete document {type}{id}: {r.status_code} {r.text}")


def index_album(album: Album):
    """ Bulk index album and all songs """
    artist_name = album.artist.user.display_name
    album_doc = SimpleNamespace(
        id=album.id,
        title=album.title,
        artist_name=artist_name
    )
    songs_stmt = select(Song.id, Song.title,
                    literal(album.id).label('album_id'),
                    literal(artist_name).label('artist_name')) \
                .where(Song.album_id == album.id)
    songs = Session.execute(songs_stmt).all()

    bulk_index([], [album_doc], songs)


def delete_album(album: Album):
    """ Bulk delete album and all songs """
    songs_stmt = select(Song.id).where(Song.album_id == album.id)
    songs = Session.execute(songs_stmt).all()

    lines = []
    lines.append(json.dumps({
        "delete": {
            "_index": INDEX_NAME,
            "_id": f"album{album.id}"
        }
    }))
    for song in songs:
        lines.append(json.dumps({
            "delete": {
                "_index": INDEX_NAME,
                "_id": f"song{song.id}"
            }}))
    
    payload = "\n".join(lines) + "\n"
    r = requests.post(f"{OPENSEARCH_URL}/_bulk", data=payload,
                      headers={"Content-Type": "application/json"})
    if r.status_code != 200:
        raise RuntimeError(f"Bulk delete failed: {r.status_code} {r.text}")


def index_artist(artist_user: User):
    """ Bulk index artist and all their albums and songs """
    albums_stmt = select(Album.id, Album.title,
                        literal(artist_user.display_name).label('artist_name')) \
                    .where(Album.artist_id == artist_user.id)
    albums = Session.execute(albums_stmt).all()

    songs_stmt = select(Song.id, Song.title, Album.id.label("album_id"),
                        literal(artist_user.display_name).label('artist_name')) \
                    .join(Album, Album.id == Song.album_id) \
                    .where(Album.artist_id == artist_user.id)
    songs = Session.execute(songs_stmt).all()

    bulk_index([artist_user], albums, songs)


def init_catalog_index():
    """
    Wait for connection, check if catalog index exists
    If index does not exist, create and index entire catalog from db
    """
    _wait_for_opensearch_ready(timeout=120)
    if check_index_exists():
        return
    create_index()
    bulk_index_catalog()


def reindex_all():
    """
    Reindex entire catalog from db
    Create index if it doesn't exist
    """
    delete_index()
    bulk_index_catalog()


def _wait_for_opensearch_ready(timeout=120):
    timeout += time.time()
    while time.time() < timeout:
        try:
            r = requests.get(OPENSEARCH_URL, timeout=2)
            if r.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(10)
    raise RuntimeError("OpenSearch connection timed out")
