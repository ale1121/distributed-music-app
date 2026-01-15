from flask import Flask, jsonify
import logging
from app.stream import stream_bp
from app.errors import register_error_handlers


def create_app():
    app = Flask(__name__)

    app.register_blueprint(stream_bp)

    register_error_handlers(app)

    logging.basicConfig(level=logging.DEBUG)

    @app.route("/health")
    def health():
        return jsonify(ok=True), 200

    return app
