from werkzeug.exceptions import NotFound, Forbidden
from flask import session
from app.db import Session
from app.models import Album, Song


def get_album(album_id, artist_required=False):
    """
    Get album from db, optionally check if user can edit album
    """
    album = Session.get(Album, album_id)
    if not album:
        raise NotFound("Album not found")
    if artist_required: 
        if album.artist_id != session["user_id"]:
            raise Forbidden("You don't have permission to edit this album")
    else:
        if not album.published:
            raise Forbidden("This album is private")
    return album


def get_song(album_id, song_id, artist_required=False):
    """
    Get song from db, optionally check if user can edit song
    """
    album = get_album(album_id, artist_required=artist_required)
    
    song = Session.get(Song, song_id)
    if not song:
        raise NotFound("Song not found")
    if song.album != album:
        raise NotFound("The song doesn't exist in this album")
    
    return song, album
