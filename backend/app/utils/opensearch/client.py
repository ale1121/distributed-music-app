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


def init_catalog_index():
    wait_for_opensearch_ready(timeout=120)

    # check if index already exists
    r = requests.head(f"{OPENSEARCH_URL}/{INDEX_NAME}")
    if r.status_code != 404:
        return False
    
    # load index definition
    index_file = Path(__file__).with_name('catalog_index.json')
    with index_file.open('r') as f:
        index_def = json.load(f)

    # create index
    requests.put(f"{OPENSEARCH_URL}/{INDEX_NAME}", json=index_def)

    # bulk index all existing artists, albums and songs
    bulk_index_catalog()

    return True


def bulk_index_catalog():
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
                      headers={"Content-Type": "application/json"}, timeout=30)
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
