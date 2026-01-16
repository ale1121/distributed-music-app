from flask import Blueprint, render_template
from app.auth.auth_ctx import get_user_roles, get_user_id
from app.auth.decorators import login_required
from sqlalchemy import select, func
from app.database.db import Session
from app.database.models import Song, Album, Play, User


home_bp = Blueprint('home', __name__)


@home_bp.route("/")
@login_required
def view():
    """ View home page """
    
    user_id = get_user_id()

    # get recently played songs and recently released albums
    recents = _get_recently_played(user_id, limit=4)
    new_releases = _get_new_releases(limit=4)

    return render_template("pages/search_page.html",
                           recents=recents, new_releases=new_releases,
                           current_path='/', roles=get_user_roles())


def _get_recently_played(user_id, limit=4):
    all_plays = select(Play.song_id,
                    func.max(Play.played_at).label("last_played")) \
                .where(Play.user_id == user_id) \
                .group_by(Play.song_id) \
                .subquery()
    
    stmt = select(Song.id, Song.title, 
                  Album.id.label("album_id"), Album.title.label("album_title"),
                  Album.cover_file,
                  User.display_name.label("artist_name")) \
            .join(all_plays, all_plays.c.song_id == Song.id) \
            .join(Album, Album.id == Song.album_id) \
            .join(User, User.id == Album.artist_id) \
            .order_by(all_plays.c.last_played.desc()) \
            .limit(limit)
    return Session.execute(stmt).all()


def _get_new_releases(limit=4):
    stmt = select(Album.id, Album.title, Album.cover_file, Album.release_year,
                    User.display_name.label("artist_name")) \
            .join(User, User.id == Album.artist_id) \
            .where(Album.published == True) \
            .order_by(Album.published_at.desc()) \
            .limit(limit)
    return Session.execute(stmt).all()
