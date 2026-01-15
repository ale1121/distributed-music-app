from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({
            "error": e.name,
            "message": e.description
        }), e.code
    

    @app.errorhandler(Exception)
    def handle_any_exception(e):
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500
