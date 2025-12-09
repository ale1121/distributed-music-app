from flask import Blueprint, session, render_template
from app.auth.decorators import login_required, role_required

account_bp = Blueprint('account', __name__)

@account_bp.route("/account")
@login_required
@role_required("ROLE_USER")
def view():
    username = session["user"].get("preferred_username")
    display_name = session["user"].get("nickname", "altceva")
    return render_template("account_page.html", 
                           username=username, display_name=display_name,
                           current_path='/account')