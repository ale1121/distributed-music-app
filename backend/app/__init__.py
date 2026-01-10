from flask import Flask
from datetime import datetime
from zoneinfo import ZoneInfo
import logging
from .config.config import Config
from .config.jinja_filters import format_dt, format_duration
from .db import Session
from . import models
from .routes.auth import auth_bp
from .routes.home import home_bp
from .routes.account import account_bp
from .routes.artist import artist_bp
from .routes.admin import admin_bp
from .routes.trending import trending_bp
from .routes.artist_request import artist_req_bp
from .routes.uploads import uploads_bp
from .routes.album import album_bp
from .routes.song import song_bp
from .routes.search import search_bp
from .utils.errors import register_error_handlers
from .utils.opensearch.client import init_catalog_index


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(artist_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(trending_bp)
    app.register_blueprint(artist_req_bp)
    app.register_blueprint(uploads_bp)
    app.register_blueprint(album_bp)
    app.register_blueprint(song_bp)
    app.register_blueprint(search_bp)

    register_error_handlers(app)

    logging.basicConfig(level=logging.DEBUG) 

    if init_catalog_index():
        logging.info("OpenSearch index initialised")
    else:
        logging.info("OpenSearch index already exists")

    app.jinja_env.filters["format_dt"] = format_dt
    app.jinja_env.filters["format_duration"] = format_duration   

    @app.teardown_request
    def remove_session(e):
        if e is not None:
            Session.rollback()
        Session.remove()
    
    return app
