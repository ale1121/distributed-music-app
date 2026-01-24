import json
import requests
from sqlalchemy import select
from app.database.models import User, Artist, Album, Song
from app.database.db import Session
from .conf import INDEX_NAME, OPENSEARCH_URL


def bulk_index_catalog():
    """ Bulk index all existing artists, public albums and songs """
    artists_stmt = select(Artist.id, User.display_name) \
                    .join(User, User.id == Artist.id)
    artists = Session.execute(artists_stmt).all()

    albums_stmt = select(Album.id, Album.title, User.display_name.label("artist_name")) \
                    .join(User, User.id == Album.artist_id) \
                    .where(Album.published == True)
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
            "url": f"/song/{song.id}"
        }))

    if not lines:
        return

    payload = "\n".join(lines) + "\n"

    r = requests.post(f"{OPENSEARCH_URL}/_bulk", data=payload,
                      headers={"Content-Type": "application/json"})
    if r.status_code != 200:
        raise RuntimeError(f"Bulk index failed: {r.status_code} {r.text}")
