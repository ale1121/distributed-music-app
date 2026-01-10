import json
import requests
import os
import time
from pathlib import Path
from sqlalchemy import select
from ...models import Song, Album, Artist, User
from ...db import Session


OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", "http://opensearch:9200")
INDEX_NAME = "catalog"


def index_document(name, type, id, url, artist=None):
    doc = json.dumps({
        "name": name,
        "type": type,
        "id": id,
        "artist": artist,
        "url": url
    })
    doc_id = f"{type}{id}"
    r = requests.put(f"{OPENSEARCH_URL}/{INDEX_NAME}/_doc/{doc_id}", json=doc)
    if r.status_code not in (200, 201):
        raise RuntimeWarning(f"Failed to index document {doc_id}: {r.status_code} {r.text}")


def delete_document(id, type):
    doc_id = f"{type}{id}"
    r = requests.put(f"{OPENSEARCH_URL}/{INDEX_NAME}/{doc_id}")
    if r.status_code not in (200, 201):
        raise RuntimeWarning(f"Failed to delete document {type}{id}: {r.status_code} {r.text}")


def init_catalog_index():
    wait_for_opensearch_ready(timeout=120)
    if check_index_exists():
        return
    create_index()
    bulk_index_catalog()


def reindex():
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
