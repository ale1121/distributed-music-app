from flask import Blueprint, render_template, current_app
from werkzeug.exceptions import NotFound
from app.auth.decorators import login_required
from app.auth.auth_ctx import get_user_id, get_user_roles
from app.database.db import Session
from app.database.models import ArtistRequest, User


account_bp = Blueprint('account', __name__)


@account_bp.route("/account", methods=["GET"])
@login_required
def view():
    """ View 'My Account' page """

    user_id = get_user_id()
    user = Session.get(User, user_id)
    if not user:
        raise NotFound("User not found")
    artist_req_active = Session.get(ArtistRequest, user_id) is not None

    return render_template("pages/account.html", 
                           user=user, 
                           manage_acc_url=current_app.config['ACCOUNT_URL'],
                           artist_req_active=artist_req_active,
                           current_path='/account',
                           roles=get_user_roles()), 200
