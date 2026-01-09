from flask import Blueprint, session, render_template, current_app
from app.utils.user_roles import get_user_roles
from sqlalchemy import select
from app.db import Session
from app.models import Song, Artist, Album, Play, User


home_bp = Blueprint('home', __name__)


@home_bp.route("/")
def view():
    """ View home page """

    if not "user" in session:
        return render_template("pages/login.html")
    
    user_id = session["user_id"]
    
    stmt = select(Song.id, Song.title, 
                  Album.id.label("album_id"), Album.title.label("album_title"),
                  Album.cover_file,
                  User.display_name.label("artist_name")) \
            .join(Play, Play.song_id == Song.id) \
            .join(Album, Album.id == Song.album_id) \
            .join(Artist, Artist.id == Album.artist_id) \
            .join(User, User.id == Artist.id) \
            .where(Play.user_id == user_id) \
            .distinct(Play.song_id) \
            .order_by(Play.song_id, Play.timestamp.desc()) \
            .limit(8)
    recents = Session.execute(stmt).all()

    return render_template("pages/search_page.html",
                           recents=recents,
                           current_path='/', roles=get_user_roles())
