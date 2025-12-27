from flask import Blueprint, jsonify, session
from werkzeug.exceptions import NotFound, Conflict
from app.utils.decorators import login_required, role_required
from sqlalchemy import select
from app.db import Session
from app.models import User, Artist, ArtistRequest


artist_req_bp = Blueprint('artist_req', __name__)


@artist_req_bp.route('/artist-requests', methods=['POST'])
@login_required
def create():
    """ Create new artist request for current user """

    user_id = session["user_id"]
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


@artist_req_bp.route('/artist-requests/<int:request_id>', methods=['DELETE'])
@role_required('ROLE_ADMIN')
def delete(request_id):
    """ Delete artist request """

    req = Session.get(ArtistRequest, request_id)
    if not req:
        raise NotFound("Request not found")
    Session.delete(req)
    Session.commit()

    return jsonify(status="ok")
