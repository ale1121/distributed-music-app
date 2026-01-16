from werkzeug.exceptions import NotFound, Forbidden
from app.auth.auth_ctx import get_user_id
from app.database.db import Session
from app.database.models import Album, Song


def get_album(album_id, artist_required=False):
    """
    Get album from db
    If artist_required, check if the user owns the album
    Else check if the album is published
    """
    album = Session.get(Album, album_id)
    if not album:
        raise NotFound("Album not found")
    if artist_required: 
        if album.artist_id != get_user_id():
            raise Forbidden("You don't have permission to edit this album")
    else:
        if not album.published:
            raise Forbidden("This album is private")
    return album


def get_song(song_id, artist_required=False):
    """
    Get song from db
    If artist_required, check if the user owns the album the song is on
    Else check if the album is published
    """
    
    song = Session.get(Song, song_id)
    if not song:
        raise NotFound("Song not found")

    if artist_required:
        if song.album.artist_id != get_user_id():
            raise Forbidden("You don't have permission to edit this song")
    else:
        if not song.album.published:
            raise Forbidden("This song is in a private album")

    return song
