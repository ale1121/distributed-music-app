from flask import Blueprint, session, render_template
from app.decorators import login_required, role_required

artist_acc_bp = Blueprint('artist_acc', __name__)

@artist_acc_bp.route("/artist-account")
@login_required
@role_required("ROLE_ARTIST")
def view():
    username = session["user"].get("preferred_username")
    display_name = session["user"].get("display_name")
    return render_template("artist_dashboard.html",
                           username=username, display_name=display_name,
                           current_path='/artist-account')