from flask import Blueprint, jsonify
from werkzeug.exceptions import NotFound, Conflict
from app.auth.decorators import login_required, role_required
from app.database.db import Session
from app.database.models import User, ArtistRequest
from app.auth.auth_ctx import get_user_id


artist_req_bp = Blueprint('artist_req', __name__)


@artist_req_bp.route('/api/artist-requests', methods=['POST'])
@login_required
def create():
    """ Create new artist request for current user """

    user_id = get_user_id()
    user = Session.get(User, user_id)
    if not user:
        raise NotFound("User not found")
    if user.artist is not None:
        raise Conflict("You already have an artist account")
    if user.artist_request is not None:
        raise Conflict("There is already a pending request")
    
    new_request = ArtistRequest(user_id=user_id)
    Session.add(new_request)
    Session.commit()

    return jsonify(status="ok")


@artist_req_bp.route('/api/artist-requests/<int:request_id>', methods=['DELETE'])
@role_required('ROLE_ADMIN')
def delete(request_id):
    """ Delete artist request """

    req = Session.get(ArtistRequest, request_id)
    if not req:
        raise NotFound("Request not found")
    Session.delete(req)
    Session.commit()

    return jsonify(status="ok")
