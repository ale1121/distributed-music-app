import json
import requests
import os
import time
from pathlib import Path
from types import SimpleNamespace
from sqlalchemy import select, literal
from werkzeug.exceptions import NotFound
from ...models import Song, Album, Artist, User
from ...db import Session


OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", "http://opensearch:9200")
INDEX_NAME = "catalog"

FUZZINESS = 3
MIN_MATCH = 75
MAX_RESULTS = 6

TYPES = ['artist', 'album', 'song']


def search(name, type=None):
    """ Search catalog by name, optional filter by type """
    if type is None:
        payload = get_name_query(name)
    else:
        payload = get_name_type_query(name, type)

    r = requests.get(f"{OPENSEARCH_URL}/{INDEX_NAME}/_search", json=payload)
    if r.status_code != 200:
        raise RuntimeWarning(f"Search error: {r.status_code} {r.text}")
    return parse_results(r.json())


def get_name_query(name):
    return {
        "size": MAX_RESULTS,
        "query": {
            "match": {
                "name": {
                    "query": name,
                    "minimum_should_match": f"{MIN_MATCH}%",
                    "fuzziness": FUZZINESS
                }
            }
        },
        "sort": [
            "_score"
        ]
    }


def get_name_type_query(name, type):
    return {
        "size": MAX_RESULTS,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "name": {
                                "query": name,
                                "minimum_should_match": f"{MIN_MATCH}%",
                                "fuzziness": FUZZINESS
                            }
                        }
                    },
                    {
                        "term": {
                            "type": type
                        }
                    }
                ]
            }
        },
        "sort": [
            "_score"
        ]
    }


def parse_results(data):
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
    wait_for_opensearch_ready(timeout=120)
    if check_index_exists():
        return
    create_index()
    bulk_index_catalog()


def reindex_all():
    """
    Reindex entire catalog from db
    Create index if it doesn't exist
    """
    if not check_index_exists():
        create_index()
    bulk_index_catalog()


def check_index_exists():
    """ Check if index already exists """
    r = requests.head(f"{OPENSEARCH_URL}/{INDEX_NAME}")
    if r.status_code == 200:
        return True
    if r.status_code == 404:
        return False
    raise RuntimeError(f"Unexpected response from OpenSearch: {r.status_code} {r.text}")
    

def create_index():
    """ Create catalog index """

    # load index definition
    index_file = Path(__file__).with_name('catalog_index.json')
    with index_file.open('r') as f:
        index_def = json.load(f)

    # create index
    r = requests.put(f"{OPENSEARCH_URL}/{INDEX_NAME}", json=index_def)
    if r.status_code != 200:
        raise RuntimeError(f"Error creating index: {r.status_code} {r.text}")


def bulk_index_catalog():
    """ Bulk index all existing artists, albums and songs """
    artists_stmt = select(Artist.id, User.display_name) \
                    .join(User, User.id == Artist.id)
    artists = Session.execute(artists_stmt).all()

    albums_stmt = select(Album.id, Album.title, User.display_name.label("artist_name")) \
                    .join(User, User.id == Album.artist_id)
    albums = Session.execute(albums_stmt).all()

    songs_stmt = select(Song.id, Song.title, Album.id.label("album_id"),
                        User.display_name.label("artist_name")) \
                    .join(Album, Album.id == Song.album_id) \
                    .join(User, User.id == Album.artist_id)
    songs = Session.execute(songs_stmt)

    bulk_index(artists, albums, songs)


def bulk_index(artists, albums, songs):
    """ Bulk index all given artists, albums and songs """

    lines = []

    for artist in artists:
        lines.append(json.dumps({
            "index": {
                "_index": INDEX_NAME,
                "_id": f"artist{artist.id}"
            }}))
        lines.append(json.dumps({
            "name": artist.display_name,
            "type": "artist",
            "id": artist.id,
            "artist": None,
            "url": f"/artist/{artist.id}"
        }))

    for album in albums:
        lines.append(json.dumps({
            "index": {
                "_index": INDEX_NAME,
                "_id": f"album{album.id}"
            }}))
        lines.append(json.dumps({
            "name": album.title,
            "type": "album",
            "id": album.id,
            "artist": album.artist_name,
            "url": f"/album/{album.id}"
        }))

    for song in songs:
        lines.append(json.dumps({
            "index": {
                "_index": INDEX_NAME,
                "_id": f"song{song.id}"
            }}))
        lines.append(json.dumps({
            "name": song.title,
            "type": "song",
            "id": song.id,
            "artist": song.artist_name,
            "url": f"/album/{song.album_id}/song/{song.id}"
        }))

    payload = "\n".join(lines) + "\n"

    r = requests.post(f"{OPENSEARCH_URL}/_bulk", data=payload,
                      headers={"Content-Type": "application/json"})
    if r.status_code != 200:
        raise RuntimeError(f"Bulk index failed: {r.status_code} {r.text}")


def wait_for_opensearch_ready(timeout=120):
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
