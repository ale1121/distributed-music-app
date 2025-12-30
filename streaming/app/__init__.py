from flask import Flask, jsonify
from app.config import Config
import logging
from app.stream import stream_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(stream_bp)

    logging.basicConfig(level=logging.DEBUG)

    @app.route("/health")
    def health():
        return jsonify(ok=True), 200

    return app
