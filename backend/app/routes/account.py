import requests
from flask import Blueprint, session, render_template, current_app
from app.utils.decorators import login_required, role_required
from app.utils.user_roles import get_user_roles
from app.db import Session
from app.models import ArtistRequest


account_bp = Blueprint('account', __name__)


@account_bp.route("/account")
@login_required
def view():
    """ View 'My Account' page """
    
    username = session["user"].get("preferred_username")
    display_name = session["user"].get("display_name")
    email = session["user"].get("email")

    user_id = session["user_id"]
    artist_req_active = Session.get(ArtistRequest, user_id) is not None

    return render_template("pages/account.html", 
                           username=username, display_name=display_name, email=email, 
                           manage_acc_url=current_app.config['ACCOUNT_URL'],
                           artist_req_active=artist_req_active,
                           current_path='/account',
                           roles=get_user_roles())

