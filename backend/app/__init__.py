from flask import Flask, render_template
import logging
from .config import Config
from .models import db
from .routes.auth import auth_bp
from .routes.menu import menu_bp
from .routes.account import account_bp
from .routes.artist_account import artist_acc_bp
from .routes.admin import admin_bp
from .routes.trending import trending_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(artist_acc_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(trending_bp)

    logging.basicConfig(level=logging.DEBUG)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.route("/health")
    def health():
        return {"status": "ok"}
    
    return app