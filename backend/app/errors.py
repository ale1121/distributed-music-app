from flask import render_template, request, jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
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
