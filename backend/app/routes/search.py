from flask import Blueprint, request, current_app, session, jsonify
from app.utils.decorators import login_required
from app.utils.opensearch import opensearch
from werkzeug.exceptions import BadRequest


search_bp = Blueprint('search', __name__)


@search_bp.route("/search/preview", methods=["GET"])
@login_required
def search_preview():
    name = request.args.get("q")
    type = request.args.get("type")

    if name is None or len(name) < 3 or len(name) > 100:
        return []
    
    if type not in opensearch.TYPES:
        type = None
    
    results = opensearch.search(name, type)

    return jsonify(results), 200
