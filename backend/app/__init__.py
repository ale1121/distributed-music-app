from flask import Flask, render_template, request, jsonify
from werkzeug.exceptions import HTTPException
import logging
from .config import Config
from .db import Session, create_all
from . import models
from .routes.auth import auth_bp
from .routes.menu import menu_bp
from .routes.account import account_bp
from .routes.artist_account import artist_acc_bp
from .routes.admin import admin_bp
from .routes.trending import trending_bp
from .routes.artist_request import artist_req_bp

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

    logging.basicConfig(level=logging.DEBUG)

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        if request.accept_mimetypes.best == "application/json":
            return jsonify({
                "error": e.name,
                "message": e.description
            }), e.code
        return render_template(
            "error.html", code=e.code, name=e.name, message=e.description
        ), e.code
    
    @app.errorhandler(Exception)
    def handle_any_exception(e):
        return render_template(
            "error.html",
            code=500,
            name="Internal Server Error",
            message=str(e)
        ), 500

    @app.teardown_request
    def remove_session(e):
        if e is not None:
            Session.rollback()
        Session.remove()

    @app.get("/dev/init-db")
    def dev_init_db():
        create_all()
        return {"ok": True}
    
    return app