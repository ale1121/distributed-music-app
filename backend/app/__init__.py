from flask import Flask
from datetime import datetime
from zoneinfo import ZoneInfo
import logging
from .config.config import Config
from .config.jinja_filters import format_dt
from .db import Session
from . import models
from .routes.auth import auth_bp
from .routes.menu import menu_bp
from .routes.account import account_bp
from .routes.artist_account import artist_acc_bp
from .routes.admin import admin_bp
from .routes.trending import trending_bp
from .routes.artist_request import artist_req_bp
from .routes.uploads import uploads_bp
from .routes.album import album_bp
from .routes.song import song_bp
from .errors import register_error_handlers


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(auth_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(artist_acc_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(trending_bp)
    app.register_blueprint(artist_req_bp)
    app.register_blueprint(uploads_bp)
    app.register_blueprint(album_bp)
    app.register_blueprint(song_bp)

    register_error_handlers(app)

    app.jinja_env.filters["format_dt"] = format_dt

    logging.basicConfig(level=logging.DEBUG)    

    @app.teardown_request
    def remove_session(e):
        if e is not None:
            Session.rollback()
        Session.remove()
    
    return app
