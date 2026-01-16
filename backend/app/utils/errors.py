from flask import render_template, request, jsonify
from werkzeug.exceptions import HTTPException, Unauthorized


def register_error_handlers(app):
    @app.errorhandler(Unauthorized)
    def handle_unauthorized(e):
        if is_api_request():
            return jsonify({
                "error": e.name,
                "message": e.description
            }), e.code
        else:
            return render_template('pages/login.html'), e.code

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        if is_api_request():
            return jsonify({
                "error": e.name,
                "message": e.description
            }), e.code
        return render_template(
            "errors/error.html", name=e.name, message=e.description
        ), e.code
    
    @app.errorhandler(Exception)
    def handle_any_exception(e):
        if is_api_request():
            return jsonify({
                "error": "Internal server error",
                "message": str(e)
            }), 500
        return render_template(
            "errors/error.html", code=500, name="Internal server error", message=str(e)
        ), 500
    
def is_api_request():
    return request.path.startswith('/api') \
        or request.accept_mimetypes.best == "application/json"
